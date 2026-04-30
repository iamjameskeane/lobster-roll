from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from lobster_roll.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def tmp_data_dir(tmp_path, monkeypatch):
    """Isolate each test to a temp data directory."""
    monkeypatch.setenv("LOBSTER_ROLL_DATA", str(tmp_path))
    # Re-import to pick up the new env var
    import lobster_roll.constants as constants
    constants.DATA_DIR = tmp_path
    constants.FOODS_CSV = tmp_path / "foods.csv"
    constants.MEALS_CSV = tmp_path / "meals.csv"
    constants.DIARY_CSV = tmp_path / "diary.csv"
    yield tmp_path


def _json(result):
    return json.loads(result.output)


def test_capabilities():
    result = runner.invoke(app, ["capabilities", "--json"])
    assert result.exit_code == 0
    data = _json(result)
    assert data["ok"] is True
    assert "commands" in data["data"]


def test_food_add_and_list():
    result = runner.invoke(app, [
        "food", "add", "Chicken Breast",
        "--per", "100", "--cal", "120", "--protein", "23",
        "--carbs", "0", "--fat", "2.6", "--source", "label",
        "--json",
    ])
    assert result.exit_code == 0
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["id"] == "chicken_breast"

    result = runner.invoke(app, ["food", "list", "--json"])
    data = _json(result)
    assert data["data"]["count"] == 1


def test_food_show():
    runner.invoke(app, ["food", "add", "Oats", "--cal", "389", "--protein", "13", "--carbs", "66", "--fat", "7", "--json"])
    result = runner.invoke(app, ["food", "show", "oats", "--json"])
    data = _json(result)
    assert data["data"]["name"] == "Oats"


def test_food_remove():
    runner.invoke(app, ["food", "add", "Rice", "--cal", "130", "--protein", "2.7", "--carbs", "28", "--fat", "0.3", "--json"])
    result = runner.invoke(app, ["food", "remove", "rice", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["removed"]["id"] == "rice"


def test_meal_add_and_show():
    runner.invoke(app, ["food", "add", "Oats", "--cal", "389", "--protein", "13", "--carbs", "66", "--fat", "7", "--json"])
    runner.invoke(app, ["food", "add", "Whey Protein", "--cal", "120", "--protein", "24", "--carbs", "3", "--fat", "1.5", "--json"])

    result = runner.invoke(app, [
        "meal", "add", "Morning Oats",
        "--ingredients", "oats:80|whey_protein:30",
        "--json",
    ])
    assert result.exit_code == 0
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["id"] == "morning_oats"
    assert data["data"]["macros"]["protein_g"] > 0

    result = runner.invoke(app, ["meal", "show", "morning_oats", "--json"])
    data = _json(result)
    assert len(data["data"]["ingredients_detail"]) == 2


def test_meal_list():
    runner.invoke(app, ["food", "add", "Oats", "--cal", "389", "--protein", "13", "--carbs", "66", "--fat", "7", "--json"])
    runner.invoke(app, ["meal", "add", "Oats Bowl", "--ingredients", "oats:100", "--json"])
    result = runner.invoke(app, ["meal", "list", "--json"])
    data = _json(result)
    assert data["data"]["count"] == 1


def test_diary_log_and_show():
    runner.invoke(app, ["food", "add", "Chicken", "--per", "100", "--cal", "120", "--protein", "23", "--json"])
    runner.invoke(app, ["food", "add", "Rice", "--per", "100", "--cal", "130", "--protein", "2.7", "--json"])
    runner.invoke(app, ["meal", "add", "Chicken Rice", "--ingredients", "chicken:200|rice:150", "--json"])

    result = runner.invoke(app, ["diary", "log", "chicken_rice", "--date", "2026-04-29", "--time", "13:00", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["macros"]["protein_g"] > 0

    result = runner.invoke(app, ["diary", "show", "--date", "2026-04-29", "--json"])
    data = _json(result)
    assert data["data"]["count"] == 1


def test_summary_today():
    runner.invoke(app, ["food", "add", "Chicken", "--per", "100", "--cal", "120", "--protein", "23", "--json"])
    runner.invoke(app, ["meal", "add", "Lunch", "--ingredients", "chicken:200", "--json"])
    runner.invoke(app, ["diary", "log", "lunch", "--json"])

    result = runner.invoke(app, ["summary", "today", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["totals"]["protein_g"] > 0


def test_summary_week():
    runner.invoke(app, ["food", "add", "Chicken", "--per", "100", "--cal", "120", "--protein", "23", "--json"])
    runner.invoke(app, ["meal", "add", "Lunch", "--ingredients", "chicken:200", "--json"])
    runner.invoke(app, ["diary", "log", "lunch", "--json"])

    result = runner.invoke(app, ["summary", "week", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert len(data["data"]["days"]) == 7


def test_diary_remove():
    runner.invoke(app, ["food", "add", "Chicken", "--per", "100", "--cal", "120", "--protein", "23", "--json"])
    runner.invoke(app, ["meal", "add", "Lunch", "--ingredients", "chicken:200", "--json"])
    runner.invoke(app, ["diary", "log", "lunch", "--date", "2026-04-29", "--time", "13:00", "--json"])

    result = runner.invoke(app, ["diary", "remove", "--date", "2026-04-29", "--time", "13:00", "--entry-id", "lunch", "--json"])
    data = _json(result)
    assert data["ok"] is True

    result = runner.invoke(app, ["diary", "show", "--date", "2026-04-29", "--json"])
    data = _json(result)
    assert data["data"]["count"] == 0


def test_profile_set_and_show():
    result = runner.invoke(app, [
        "profile", "set",
        "--calories", "2200", "--delta", "-500",
        "--protein", "180", "--carbs", "200", "--fat", "60",
        "--notes", "cutting phase",
        "--json",
    ])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["profile"]["daily_calories"] == 2200
    assert data["data"]["profile"]["protein_g"] == 180

    result = runner.invoke(app, ["profile", "show", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["active"]["daily_calories"] == 2200
    assert data["data"]["active"]["notes"] == "cutting phase"


def test_profile_history():
    runner.invoke(app, ["profile", "set", "--calories", "2000", "--protein", "150", "--json"])
    runner.invoke(app, ["profile", "set", "--calories", "2200", "--protein", "180", "--json"])
    result = runner.invoke(app, ["profile", "history", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["count"] == 2


# --- Search tests ---

def _add_test_foods():
    """Helper: add a set of foods for search testing."""
    foods = [
        ("Chicken Breast", "120", "23", "0", "2.6"),
        ("Chicken Thigh", "170", "19", "0", "10"),
        ("Brown Rice", "112", "2.6", "23", "0.9"),
        ("White Rice", "130", "2.7", "28", "0.3"),
        ("Oats", "389", "13", "66", "7"),
        ("Whole Milk", "64", "3.4", "4.6", "3.6"),
        ("Whey Protein", "120", "24", "3", "1.5"),
    ]
    for name, cal, protein, carbs, fat in foods:
        runner.invoke(app, [
            "food", "add", name,
            "--cal", cal, "--protein", protein,
            "--carbs", carbs, "--fat", fat, "--json",
        ])


def test_food_search_substring():
    """Substring match on name should return results."""
    _add_test_foods()
    result = runner.invoke(app, ["food", "search", "chicken", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["count"] == 2
    ids = [r["id"] for r in data["data"]["results"]]
    assert "chicken_breast" in ids
    assert "chicken_thigh" in ids


def test_food_search_substring_on_id():
    """Substring match on id should also work."""
    _add_test_foods()
    result = runner.invoke(app, ["food", "search", "rice", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["count"] == 2


def test_food_search_fuzzy():
    """Fuzzy match should catch typos like 'chiken' -> chicken."""
    _add_test_foods()
    result = runner.invoke(app, ["food", "search", "chiken", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["count"] >= 2  # chicken_breast, chicken_thigh
    ids = [r["id"] for r in data["data"]["results"]]
    assert "chicken_breast" in ids


def test_food_search_fuzzy_whole_ml():
    """Fuzzy match 'whole ml' should find 'Whole Milk'."""
    _add_test_foods()
    result = runner.invoke(app, ["food", "search", "whole ml", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["count"] >= 1
    ids = [r["id"] for r in data["data"]["results"]]
    assert "whole_milk" in ids


def test_food_search_no_results():
    """Search for something that doesn't match."""
    _add_test_foods()
    result = runner.invoke(app, ["food", "search", "salmon", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["count"] == 0
    assert data["data"]["results"] == []


def test_food_search_case_insensitive():
    """Search should be case-insensitive."""
    _add_test_foods()
    result = runner.invoke(app, ["food", "search", "CHICKEN", "--json"])
    data = _json(result)
    assert data["data"]["count"] == 2


def test_food_search_ranked():
    """Substring matches should rank above fuzzy-only matches."""
    _add_test_foods()
    result = runner.invoke(app, ["food", "search", "oats", "--json"])
    data = _json(result)
    assert data["ok"] is True
    # "Oats" is a direct substring match, should be first
    assert data["data"]["results"][0]["id"] == "oats"


def test_meal_search_substring():
    """Meal search should match meal names."""
    runner.invoke(app, ["food", "add", "Oats", "--cal", "389", "--protein", "13", "--json"])
    runner.invoke(app, ["food", "add", "Whey Protein", "--cal", "120", "--protein", "24", "--json"])
    runner.invoke(app, ["meal", "add", "Morning Oats", "--ingredients", "oats:80|whey_protein:30", "--json"])
    runner.invoke(app, ["meal", "add", "Overnight Oats", "--ingredients", "oats:100|whey_protein:30", "--json"])

    result = runner.invoke(app, ["meal", "search", "oats", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["count"] == 2


def test_meal_search_fuzzy():
    """Meal fuzzy search should catch typos."""
    runner.invoke(app, ["food", "add", "Chicken", "--cal", "120", "--protein", "23", "--json"])
    runner.invoke(app, ["meal", "add", "Chicken Rice", "--ingredients", "chicken:200", "--json"])

    result = runner.invoke(app, ["meal", "search", "chiken rce", "--json"])
    data = _json(result)
    assert data["ok"] is True
    assert data["data"]["count"] >= 1
