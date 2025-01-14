schema_data = {
    "name": "recipe_schema",
    "schema": {
        "type": "object",
        "properties": {
            "recipe_name": {
                "description": "The name of the extracted recipe",
                "type": "string"
            },
            "ingredients": {
                "description": "List of ingredients with their quantities",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The ingredient name"
                        },
                        "quantity": {
                            "type": "string",
                            "description": "The quantity of the ingredient"
                        },
                        "grocery_section": {
                            "type": "string",
                            "description": "The section of the ingredient"
                        }
                    },
                    "required": ["name", "quantity"]
                }
            }
        },
        "required": ["recipe_name", "ingredients"],
        "additionalProperties": False
    }
}
