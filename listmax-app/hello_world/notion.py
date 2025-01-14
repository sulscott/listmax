import requests

NOTION_API_KEY = "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"
DATABASE_ID = "158794c72e3d80e4937bcbbf4a3ccba6"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}


def add_ingredient_to_notion(recipe_name, ingredient, quantity, grocery_section):
    page_data = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "ingredient": {"title": [{"text": {"content": ingredient}}]},
            "recipe_name": {
                "rich_text": [
                    {
                        "text": {"content": recipe_name}
                    }
                ]
            },
            "quantity": {
                "rich_text": [
                    {
                        "text": {"content": quantity}
                    }
                ]
            },
            "grocery_section": {
                "rich_text": [
                    {
                        "text": {"content": grocery_section}
                    }
                ]
            },
            "purchased": {
            "checkbox": False
            }
        }
    }


    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=page_data)
    response.raise_for_status()
    return response.json()
