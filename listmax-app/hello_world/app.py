import json
import urllib.parse
import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Existing modules
from recipe_schema import schema_data
from notion import add_ingredient_to_notion

# Import the aggregator logic
from aggregator import aggregate_ingredients

def lambda_handler(event, context):

    raw_body = event.get('body', '')
    parsed_body = urllib.parse.parse_qs(raw_body)
    body_list = parsed_body.get('Body', [])

    if not body_list:
        print("No 'Body' field found in the incoming message.")
        return {'statusCode': 200, 'body': 'No URL found'}

    url_encoded = body_list[0] 
    url = urllib.parse.unquote(url_encoded)
    print(f"Extracted URL: {url}")

    try:
        # "Browser-like" User-Agent to bypass 403 blocks
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for non-200 status
        html_content = response.text
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"403 Forbidden: The site blocked our request for {url}.")
        else:
            print(f"HTTP Error: {e}")
        return {
            'statusCode': 200,
            'body': f'Could not fetch the recipe from {url}.'
        }

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_text = soup.get_text(separator=' ', strip=True)
    
    # Use OpenAI
    # TODO: save key as env variable
    openai_api_key = "PUT_KEY_HERE" 
    prompt = f"""
    Extract the recipe name and ingredients from the below text. 
    Normalize the ingredients to be lower case and singular if possible.
    You can leave in important qualifiers like "slivered almonds" or "shaved parmesan". 
    If an ingredient is listed multiple times (i.e. for a sauce and for the main dish),
    include it each time and I will aggregate later. 
    
    When giving quantities that include fractions, please write them as a decimal. Do not ever return a fraction in the quantity field. For example:
    1/2 cups -> .5 cups
    3/4 tablespoons -> .75 tablespoons

    Text:
    {extracted_text}
    """
    
    client = OpenAI(api_key=openai_api_key)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You extract recipe ingredients and quantities into JSON data."},
            {"role": "user", "content": prompt}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": schema_data
        }
    )

    result_text = response.choices[0].message.content.strip()
    result_data = json.loads(result_text)
    
    # Print out the entire LLM response for debugging:
    print("Raw LLM JSON response:", response)
    print("Raw LLM text:", result_text)
    
    recipe_name = result_data["recipe_name"]
    ingredients = result_data["ingredients"]  # list of dicts

    # 1) Aggregate duplicates & convert to base unit
    aggregated = aggregate_ingredients(ingredients)
    # aggregated is now { (ingredient_name, base_unit): total_qty, ... }

    # 2) Send results to Notion
    for (ingredient_name, base_unit), total_qty in aggregated.items():
        # Build a string like "120 g"
        final_qty_str = f"{total_qty} {base_unit}"

        # In your notion.py, add_ingredient_to_notion might need a 'section', 
        # but if we don't care about that, pass a placeholder or omit it:
        add_ingredient_to_notion(recipe_name, ingredient_name, final_qty_str, "misc")

    return {
        'statusCode': 200,
        'body': 'Data extracted and aggregated successfully'
    }
