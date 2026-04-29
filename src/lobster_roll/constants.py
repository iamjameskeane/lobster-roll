from __future__ import annotations

import os
from pathlib import Path
from typing import Any

APP_NAME = "lobster-roll"
APP_SCHEMA_PREFIX = "lobster-roll.v1"

DATA_DIR = Path(os.environ.get("LOBSTER_ROLL_DATA", Path.home() / ".lobster-roll"))

FOODS_CSV = DATA_DIR / "foods.csv"
MEALS_CSV = DATA_DIR / "meals.csv"
DIARY_CSV = DATA_DIR / "diary.csv"

FOOD_FIELDS = ["id", "name", "per_grams", "calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "source"]
MEAL_FIELDS = ["id", "name", "ingredients"]
DIARY_FIELDS = ["date", "time", "entry_type", "entry_id", "amount_g", "notes"]

MACRO_FIELDS = ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g"]

CAPABILITIES: list[dict[str, Any]] = [
    {
        "name": "food add",
        "description": "Add a food to the personal library.",
        "requires_auth": False,
        "safe": True,
        "read_only": False,
        "output_schema": f"{APP_SCHEMA_PREFIX}.food",
    },
    {
        "name": "food list",
        "description": "List all foods in the personal library.",
        "requires_auth": False,
        "safe": True,
        "read_only": True,
        "output_schema": f"{APP_SCHEMA_PREFIX}.food_list",
    },
    {
        "name": "food show",
        "description": "Show details for a specific food.",
        "requires_auth": False,
        "safe": True,
        "read_only": True,
        "output_schema": f"{APP_SCHEMA_PREFIX}.food",
    },
    {
        "name": "food remove",
        "description": "Remove a food from the personal library.",
        "requires_auth": False,
        "safe": True,
        "read_only": False,
        "output_schema": f"{APP_SCHEMA_PREFIX}.food_removed",
    },
    {
        "name": "meal add",
        "description": "Add a reusable meal (recipe) made of foods.",
        "requires_auth": False,
        "safe": True,
        "read_only": False,
        "output_schema": f"{APP_SCHEMA_PREFIX}.meal",
    },
    {
        "name": "meal list",
        "description": "List all saved meals.",
        "requires_auth": False,
        "safe": True,
        "read_only": True,
        "output_schema": f"{APP_SCHEMA_PREFIX}.meal_list",
    },
    {
        "name": "meal show",
        "description": "Show a meal with calculated macros.",
        "requires_auth": False,
        "safe": True,
        "read_only": True,
        "output_schema": f"{APP_SCHEMA_PREFIX}.meal_detail",
    },
    {
        "name": "meal remove",
        "description": "Remove a meal.",
        "requires_auth": False,
        "safe": True,
        "read_only": False,
        "output_schema": f"{APP_SCHEMA_PREFIX}.meal_removed",
    },
    {
        "name": "diary log",
        "description": "Log a food or meal to the diary.",
        "requires_auth": False,
        "safe": True,
        "read_only": False,
        "output_schema": f"{APP_SCHEMA_PREFIX}.diary_entry",
    },
    {
        "name": "diary show",
        "description": "Show diary entries for a date.",
        "requires_auth": False,
        "safe": True,
        "read_only": True,
        "output_schema": f"{APP_SCHEMA_PREFIX}.diary_day",
    },
    {
        "name": "diary remove",
        "description": "Remove a diary entry.",
        "requires_auth": False,
        "safe": True,
        "read_only": False,
        "output_schema": f"{APP_SCHEMA_PREFIX}.diary_entry_removed",
    },
    {
        "name": "summary today",
        "description": "Macro summary for today.",
        "requires_auth": False,
        "safe": True,
        "read_only": True,
        "output_schema": f"{APP_SCHEMA_PREFIX}.summary",
    },
    {
        "name": "summary date",
        "description": "Macro summary for a specific date.",
        "requires_auth": False,
        "safe": True,
        "read_only": True,
        "output_schema": f"{APP_SCHEMA_PREFIX}.summary",
    },
    {
        "name": "summary week",
        "description": "Daily macro summaries for the past 7 days.",
        "requires_auth": False,
        "safe": True,
        "read_only": True,
        "output_schema": f"{APP_SCHEMA_PREFIX}.week_summary",
    },
    {
        "name": "profile show",
        "description": "Show current nutrition targets.",
        "requires_auth": False,
        "safe": True,
        "read_only": True,
        "output_schema": f"{APP_SCHEMA_PREFIX}.profile",
    },
    {
        "name": "profile set",
        "description": "Set new nutrition targets. Closes previous profile.",
        "requires_auth": False,
        "safe": True,
        "read_only": False,
        "output_schema": f"{APP_SCHEMA_PREFIX}.profile_set",
    },
    {
        "name": "profile history",
        "description": "Show all past and current profiles.",
        "requires_auth": False,
        "safe": True,
        "read_only": True,
        "output_schema": f"{APP_SCHEMA_PREFIX}.profile_history",
    },
    {
        "name": "capabilities",
        "description": "List agent-safe commands and their contracts.",
        "requires_auth": False,
        "safe": True,
        "read_only": True,
        "output_schema": f"{APP_SCHEMA_PREFIX}.capabilities",
    },
]
