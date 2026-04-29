from __future__ import annotations

import re
from typing import Annotated

import typer

from lobster_roll.errors import LobsterError
from lobster_roll.models import calculate_meal_macros, parse_ingredients
from lobster_roll.output import emit, fail

meal_app = typer.Typer(help="Manage reusable meals (recipes)")


def _slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


@meal_app.command("add")
def meal_add(
    name: Annotated[str, typer.Argument(help="Meal name (e.g. 'Morning Smoothie')")],
    ingredients: Annotated[str, typer.Option("--ingredients", "-i", help="Ingredients as food_id:grams|food_id:grams")] = "",
    meal_id: Annotated[str, typer.Option("--id", help="Override the auto-generated id.")] = "",
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Add a reusable meal (recipe) made of foods."""
    from lobster_roll.storage import add_meal, load_foods

    mid = meal_id or _slugify(name)

    # Validate ingredients exist as foods
    foods = load_foods()
    parsed = parse_ingredients(ingredients)
    missing = [p["food_id"] for p in parsed if p["food_id"] not in foods]
    if missing:
        fail(LobsterError(
            "food_not_found",
            f"Unknown food(s): {', '.join(missing)}.",
            "Add them first with 'lobster-roll food add'.",
        ))

    meal = {"id": mid, "name": name, "ingredients": ingredients}
    try:
        add_meal(meal)
        macros = calculate_meal_macros(ingredients, foods)
        emit("meal", {**meal, "macros": macros}, json_output)
    except LobsterError as e:
        fail(e)


@meal_app.command("list")
def meal_list(
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """List all saved meals."""
    from lobster_roll.storage import list_meals

    meals = list_meals()
    emit("meal_list", {"meals": meals, "count": len(meals)}, json_output)


@meal_app.command("show")
def meal_show(
    meal_id: Annotated[str, typer.Argument(help="Meal id to look up.")],
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Show a meal with calculated macros."""
    from lobster_roll.storage import load_foods, load_meals

    meals = load_meals()
    if meal_id not in meals:
        fail(LobsterError("meal_not_found", f"Meal '{meal_id}' not found.", "Use 'meal list' to see available meals."))
    meal = meals[meal_id]
    foods = load_foods()
    macros = calculate_meal_macros(meal["ingredients"], foods)

    # Resolve ingredient names
    ingredients = parse_ingredients(meal["ingredients"])
    resolved = []
    for ing in ingredients:
        food = foods.get(ing["food_id"], {})
        resolved.append({
            "food_id": ing["food_id"],
            "food_name": food.get("name", ing["food_id"]),
            "grams": ing["grams"],
        })

    emit("meal_detail", {**meal, "ingredients_detail": resolved, "macros": macros}, json_output)


@meal_app.command("remove")
def meal_remove(
    meal_id: Annotated[str, typer.Argument(help="Meal id to remove.")],
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Remove a meal."""
    from lobster_roll.storage import remove_meal

    try:
        removed = remove_meal(meal_id)
        emit("meal_removed", {"removed": removed}, json_output)
    except LobsterError as e:
        fail(e)
