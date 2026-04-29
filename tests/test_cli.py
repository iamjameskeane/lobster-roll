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
