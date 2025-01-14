import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.client('dynamodb')
CACHE = {}

def get_conversions_for_ingredient(ingredient_name):
    # Check cache first
    if ingredient_name in CACHE:
        return CACHE[ingredient_name]
    
    try:
        response = dynamodb.get_item(
            TableName='CanonicalIngredients',
            Key={'ingredient_name': {'S': ingredient_name.lower()}}
        )
        item = response.get('Item')
        if not item:
            return None
        
        base_unit = item['base_unit']['S']
        units = item.get('units', {}).get('L', [])
        
        conversions = []
        for unit in units:
            unit_map = unit['M']
            unit_name = unit_map['unit_name']['S']
            aliases = [alias['S'] for alias in unit_map['aliases']['L']]
            conversion_factor = float(unit_map['conversion_factor']['N'])
            conversions.append({
                'unit_name': unit_name,
                'aliases': aliases,
                'conversion_factor': conversion_factor
            })
        
        data = {
            'base_unit': base_unit,
            'units': conversions
        }
        
        # Cache the result
        CACHE[ingredient_name] = data
        return data
    except ClientError as e:
        print(f"Error fetching ingredient conversions: {e}")
        return None

def convert_to_base_unit(quantity, unit, ingredient_name):
    conversions = get_conversions_for_ingredient(ingredient_name)
    if not conversions:
        return quantity, unit  # No conversion available
    
    for conv in conversions['units']:
        if unit.lower() in [alias.lower() for alias in conv['aliases']]:
            base_quantity = quantity * conv['conversion_factor']
            return base_quantity, conversions['base_unit']
    
    return quantity, unit  # Unit not found in conversions
