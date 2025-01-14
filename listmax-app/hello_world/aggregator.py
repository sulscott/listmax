# aggregator.py (for example)
import re
from fractions import Fraction
from conversions import convert_to_base_unit

def parse_quantity(raw_qty: str) -> tuple[float, str]:
    """
    Parses a raw quantity string (e.g., "1 1/2 cups") into (float_value, unit_string).
    Examples:
      "1 1/2 cups"  -> (1.5, "cups")
      "3/4 cups"    -> (0.75, "cups")
      "1.25 cups"   -> (1.25, "cups")
      "2 cups"      -> (2.0, "cups")
      "2.5 tsp"     -> (2.5, "tsp")
      "tbsp"        -> fallback: (1.0, "tbsp") if we can't parse
    """

    raw_qty = raw_qty.strip().lower()
    # Regex explanation:
    # ^\s* : start, optional spaces
    # (\d+(\.\d+)?)? : optional whole or decimal number
    # \s* : optional spaces
    # (\d/\d)? : optional fraction part
    # \s*(.*)$ : rest is unit
    pattern = r'^\s*((?:\d+)?\.\d+|\d+)?\s*(\d/\d)?\s*(.*)$'
    match = re.match(pattern, raw_qty)

    if not match:
        # If we can’t match at all, fallback to 1.0 and everything is the unit
        return (1.0, raw_qty)

    # Groups:
    # 1) full decimal/whole number
    # 2) decimal portion inside that (not used directly)
    # 3) fraction portion (e.g. "1/2")
    # 4) the rest (unit)

    whole_str = match.group(1)   # e.g. "1" or "1.25"
    fraction_str = match.group(2) # e.g. "1/2"
    unit_str = match.group(3).strip() # e.g. "cups"

    total_val = 0.0
    if whole_str:
        try:
            total_val += float(whole_str)
        except ValueError:
            pass

    if fraction_str:
        # Convert fraction like "1/2" or "3/4" to float
        total_val += float(Fraction(fraction_str))

    if total_val == 0.0 and not unit_str:
        # If we ended up with no number and no unit, fallback
        return (1.0, raw_qty)

    return (total_val if total_val > 0 else 1.0, unit_str)

def aggregate_ingredients(ingredient_list):
    """
    Uses parse_quantity + convert_to_base_unit to:
      - parse mixed fraction strings
      - convert to base unit
      - aggregate duplicates by (ingredient_name, base_unit)
    """

    aggregator = {}

    for ing in ingredient_list:
        name = ing["name"]       # e.g. "flour"
        raw_qty = ing["quantity"]# e.g. "1 1/2 cups"

        qty_val, unit_str = parse_quantity(raw_qty)
        base_val, base_unit = convert_to_base_unit(qty_val, unit_str, name)

        key = (name, base_unit)
        aggregator[key] = aggregator.get(key, 0.0) + base_val

    return aggregator
