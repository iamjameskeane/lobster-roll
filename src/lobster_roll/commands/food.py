from __future__ import annotations

import re
from typing import Annotated

import typer

from lobster_roll.constants import FOOD_FIELDS
from lobster_roll.errors import LobsterError
from lobster_roll.output import emit, fail, now_iso

food_app = typer.Typer(help="Manage personal food library")


def _slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


@food_app.command("add")
def food_add(
    name: Annotated[str, typer.Argument(help="Food name (e.g. 'Chicken Breast')")],
    per_grams: Annotated[float, typer.Option("--per", help="Serving size in grams for the nutrition values.")] = 100,
    calories: Annotated[float, typer.Option("--cal", help="Calories per serving.")] = 0,
    protein: Annotated[float, typer.Option("--protein", help="Protein (g) per serving.")] = 0,
    carbs: Annotated[float, typer.Option("--carbs", help="Carbs (g) per serving.")] = 0,
    fat: Annotated[float, typer.Option("--fat", help="Fat (g) per serving.")] = 0,
    fiber: Annotated[float, typer.Option("--fiber", help="Fiber (g) per serving.")] = 0,
    source: Annotated[str, typer.Option("--source", help="Data source: label, edamam, manual.")] = "manual",
    food_id: Annotated[str, typer.Option("--id", help="Override the auto-generated id.")] = "",
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Add a food to your personal library."""
    from lobster_roll.storage import add_food

    fid = food_id or _slugify(name)
    food = {
        "id": fid,
        "name": name,
        "per_grams": str(per_grams),
        "calories": str(calories),
        "protein_g": str(protein),
        "carbs_g": str(carbs),
        "fat_g": str(fat),
        "fiber_g": str(fiber),
        "source": source,
    }
    try:
        add_food(food)
        emit("food", food, json_output)
    except LobsterError as e:
        fail(e)


@food_app.command("list")
def food_list(
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """List all foods in your personal library."""
    from lobster_roll.storage import list_foods

    foods = list_foods()
    emit("food_list", {"foods": foods, "count": len(foods)}, json_output)


@food_app.command("show")
def food_show(
    food_id: Annotated[str, typer.Argument(help="Food id to look up.")],
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Show details for a specific food."""
    from lobster_roll.storage import load_foods

    foods = load_foods()
    if food_id not in foods:
        fail(LobsterError("food_not_found", f"Food '{food_id}' not found.", "Use 'food list' to see available foods."))
    emit("food", foods[food_id], json_output)


@food_app.command("remove")
def food_remove(
    food_id: Annotated[str, typer.Argument(help="Food id to remove.")],
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Remove a food from your personal library."""
    from lobster_roll.storage import remove_food

    try:
        removed = remove_food(food_id)
        emit("food_removed", {"removed": removed}, json_output)
    except LobsterError as e:
        fail(e)


@food_app.command("search")
def food_search(
    query: Annotated[str, typer.Argument(help="Search term (substring + fuzzy matching).")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results to return.")] = 20,
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Search foods by name or id. Combines substring and fuzzy matching."""
    from lobster_roll.search import search_items
    from lobster_roll.storage import list_foods

    foods = list_foods()
    results = search_items(query, foods, fields=["id", "name"], limit=limit)
    emit("food_search", {"query": query, "results": results, "count": len(results)}, json_output)
