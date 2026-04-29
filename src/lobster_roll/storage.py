from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from lobster_roll import constants
from lobster_roll.errors import LobsterError


def ensure_data_dir() -> None:
    constants.DATA_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_file(path: Path, fields: list[str]) -> None:
    if not path.exists():
        ensure_data_dir()
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()


def _read_csv(path: Path, fields: list[str]) -> list[dict[str, str]]:
    _ensure_file(path, fields)
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    ensure_data_dir()
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _append_csv(path: Path, fields: list[str], row: dict[str, str]) -> None:
    _ensure_file(path, fields)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writerow(row)


# --- Food operations ---

def load_foods() -> dict[str, dict[str, str]]:
    rows = _read_csv(constants.FOODS_CSV, constants.FOOD_FIELDS)
    return {row["id"]: row for row in rows}


def list_foods() -> list[dict[str, str]]:
    return _read_csv(constants.FOODS_CSV, constants.FOOD_FIELDS)


def add_food(food: dict[str, str]) -> None:
    foods = load_foods()
    if food["id"] in foods:
        raise LobsterError("food_exists", f"Food '{food['id']}' already exists.", "Use 'food show' to see it or choose a different id.")
    _append_csv(constants.FOODS_CSV, constants.FOOD_FIELDS, food)


def remove_food(food_id: str) -> dict[str, str]:
    foods = load_foods()
    if food_id not in foods:
        raise LobsterError("food_not_found", f"Food '{food_id}' not found.", "Use 'food list' to see available foods.")
    removed = foods.pop(food_id)
    _write_csv(constants.FOODS_CSV, constants.FOOD_FIELDS, list(foods.values()))
    return removed


# --- Meal operations ---

def load_meals() -> dict[str, dict[str, str]]:
    rows = _read_csv(constants.MEALS_CSV, constants.MEAL_FIELDS)
    return {row["id"]: row for row in rows}


def list_meals() -> list[dict[str, str]]:
    return _read_csv(constants.MEALS_CSV, constants.MEAL_FIELDS)


def add_meal(meal: dict[str, str]) -> None:
    meals = load_meals()
    if meal["id"] in meals:
        raise LobsterError("meal_exists", f"Meal '{meal['id']}' already exists.", "Use 'meal show' to see it or choose a different id.")
    _append_csv(constants.MEALS_CSV, constants.MEAL_FIELDS, meal)


def remove_meal(meal_id: str) -> dict[str, str]:
    meals = load_meals()
    if meal_id not in meals:
        raise LobsterError("meal_not_found", f"Meal '{meal_id}' not found.", "Use 'meal list' to see available meals.")
    removed = meals.pop(meal_id)
    _write_csv(constants.MEALS_CSV, constants.MEAL_FIELDS, list(meals.values()))
    return removed


# --- Diary operations ---

def load_diary() -> list[dict[str, str]]:
    return _read_csv(constants.DIARY_CSV, constants.DIARY_FIELDS)


def log_entry(entry: dict[str, str]) -> None:
    _append_csv(constants.DIARY_CSV, constants.DIARY_FIELDS, entry)


def remove_diary_entry(date_str: str, time_str: str, entry_id: str) -> dict[str, str]:
    rows = load_diary()
    found = None
    remaining = []
    for row in rows:
        if row["date"] == date_str and row["time"] == time_str and row["entry_id"] == entry_id:
            found = row
        else:
            remaining.append(row)
    if found is None:
        raise LobsterError(
            "entry_not_found",
            f"Diary entry not found: {date_str} {time_str} {entry_id}.",
            "Use 'diary show --date <date>' to see entries.",
        )
    _write_csv(constants.DIARY_CSV, constants.DIARY_FIELDS, remaining)
    return found


def get_diary_for_date(date_str: str) -> list[dict[str, str]]:
    return [r for r in load_diary() if r["date"] == date_str]
