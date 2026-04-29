from __future__ import annotations

from typing import Any

from lobster_roll.constants import MACRO_FIELDS


def parse_ingredients(ingredients_str: str) -> list[dict[str, str]]:
    """Parse 'food_id:grams|food_id:grams' into list of {food_id, grams}."""
    if not ingredients_str.strip():
        return []
    parts = []
    for item in ingredients_str.split("|"):
        item = item.strip()
        if ":" not in item:
            continue
        food_id, grams = item.split(":", 1)
        parts.append({"food_id": food_id.strip(), "grams": grams.strip()})
    return parts


def calculate_meal_macros(
    ingredients_str: str, foods: dict[str, dict[str, str]], amount_override_g: float | None = None
) -> dict[str, float]:
    """Calculate total macros for a meal from its ingredients."""
    ingredients = parse_ingredients(ingredients_str)
    totals: dict[str, float] = {k: 0.0 for k in MACRO_FIELDS}
    total_base_grams = 0.0

    for ing in ingredients:
        food_id = ing["food_id"]
        grams = float(ing["grams"])
        total_base_grams += grams
        if food_id not in foods:
            continue
        food = foods[food_id]
        per_grams = float(food["per_grams"])
        scale = grams / per_grams
        for field in MACRO_FIELDS:
            totals[field] += float(food.get(field, 0)) * scale

    # Scale if amount override is different from total base grams
    if amount_override_g is not None and total_base_grams > 0:
        ratio = amount_override_g / total_base_grams
        for field in MACRO_FIELDS:
            totals[field] *= ratio

    return {k: round(v, 1) for k, v in totals.items()}


def calculate_food_macros(food: dict[str, str], amount_g: float) -> dict[str, float]:
    """Calculate macros for a food at a given amount."""
    per_grams = float(food["per_grams"])
    scale = amount_g / per_grams
    return {k: round(float(food.get(k, 0)) * scale, 1) for k in MACRO_FIELDS}


def resolve_entry_macros(
    entry: dict[str, str], foods: dict[str, dict[str, str]], meals: dict[str, dict[str, str]]
) -> dict[str, float]:
    """Resolve a diary entry to its macro totals."""
    entry_type = entry["entry_type"]
    entry_id = entry["entry_id"]
    amount_override = float(entry["amount_g"]) if entry.get("amount_g") else None

    if entry_type == "meal":
        if entry_id not in meals:
            return {k: 0.0 for k in MACRO_FIELDS}
        meal = meals[entry_id]
        return calculate_meal_macros(meal["ingredients"], foods, amount_override)
    elif entry_type == "food":
        if entry_id not in foods:
            return {k: 0.0 for k in MACRO_FIELDS}
        food = foods[entry_id]
        grams = amount_override if amount_override else float(food["per_grams"])
        return calculate_food_macros(food, grams)
    else:
        return {k: 0.0 for k in MACRO_FIELDS}


def summarize_day(
    entries: list[dict[str, str]], foods: dict[str, dict[str, str]], meals: dict[str, dict[str, str]]
) -> dict[str, Any]:
    """Summarize all diary entries for a single day."""
    totals: dict[str, float] = {k: 0.0 for k in MACRO_FIELDS}
    resolved_entries = []
    for entry in entries:
        macros = resolve_entry_macros(entry, foods, meals)
        for k in MACRO_FIELDS:
            totals[k] += macros[k]
        resolved_entries.append({**entry, "macros": macros})

    return {
        "entry_count": len(entries),
        "entries": resolved_entries,
        "totals": {k: round(v, 1) for k, v in totals.items()},
    }
