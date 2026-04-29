from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated

import typer

from lobster_roll.models import summarize_day
from lobster_roll.output import emit, resolve_day

summary_app = typer.Typer(help="Macro summaries")


@summary_app.command("today")
def summary_today(
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Macro summary for today."""
    _emit_summary(date.today().isoformat(), json_output)


@summary_app.command("date")
def summary_date(
    date_str: Annotated[str, typer.Argument(help="Date as YYYY-MM-DD, today, or yesterday.")],
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Macro summary for a specific date."""
    _emit_summary(resolve_day(date_str), json_output)


@summary_app.command("week")
def summary_week(
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Daily macro summaries for the past 7 days."""
    from lobster_roll.storage import get_diary_for_date, load_foods, load_meals

    foods = load_foods()
    meals = load_meals()
    today = date.today()
    days = []
    week_totals = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fiber_g": 0}

    for i in range(7):
        d = today - timedelta(days=6 - i)
        date_str = d.isoformat()
        entries = get_diary_for_date(date_str)
        summary = summarize_day(entries, foods, meals)
        days.append({"date": date_str, **summary})
        for k in week_totals:
            week_totals[k] += summary["totals"].get(k, 0)

    week_totals = {k: round(v, 1) for k, v in week_totals.items()}
    week_totals["daily_avg"] = {k: round(v / 7, 1) for k, v in week_totals.items() if isinstance(v, (int, float))}

    emit("week_summary", {"days": days, "week_totals": week_totals}, json_output)


def _emit_summary(date_str: str, json_output: bool) -> None:
    from lobster_roll.storage import get_diary_for_date, load_foods, load_meals

    foods = load_foods()
    meals = load_meals()
    entries = get_diary_for_date(date_str)
    summary = summarize_day(entries, foods, meals)
    emit("summary", {"date": date_str, **summary}, json_output)
