from __future__ import annotations

from datetime import datetime
from typing import Annotated

import typer

from lobster_roll.errors import LobsterError
from lobster_roll.models import resolve_entry_macros
from lobster_roll.output import emit, fail, now_iso, resolve_day

diary_app = typer.Typer(help="Log and query daily food intake")


@diary_app.command("log")
def diary_log(
    entry_id: Annotated[str, typer.Argument(help="Meal id or food id to log.")],
    entry_type: Annotated[str, typer.Option("--type", help="Type: meal or food. Auto-detected if omitted.")] = "",
    date_str: Annotated[str, typer.Option("--date", help="Date as YYYY-MM-DD, today, or yesterday.")] = "today",
    time_str: Annotated[str, typer.Option("--time", help="Time as HH:MM. Defaults to now.")] = "",
    amount_g: Annotated[float, typer.Option("--amount", help="Amount in grams (overrides default).")] = 0,
    notes: Annotated[str, typer.Option("--notes", help="Free-text notes.")] = "",
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Log a food or meal to the diary."""
    from lobster_roll.storage import load_foods, load_meals, log_entry

    foods = load_foods()
    meals = load_meals()

    # Auto-detect type
    if not entry_type:
        if entry_id in meals:
            entry_type = "meal"
        elif entry_id in foods:
            entry_type = "food"
        else:
            fail(LobsterError(
                "entry_not_found",
                f"'{entry_id}' is not a known food or meal.",
                "Use 'food list' or 'meal list' to see available items.",
            ))

    resolved_date = resolve_day(date_str)
    resolved_time = time_str or datetime.now().strftime("%H:%M")

    entry = {
        "date": resolved_date,
        "time": resolved_time,
        "entry_type": entry_type,
        "entry_id": entry_id,
        "amount_g": str(amount_g) if amount_g else "",
        "notes": notes,
    }

    log_entry(entry)

    # Calculate macros for the response
    macros = resolve_entry_macros(entry, foods, meals)
    emit("diary_entry", {**entry, "macros": macros}, json_output)


@diary_app.command("show")
def diary_show(
    date_str: Annotated[str, typer.Option("--date", help="Date as YYYY-MM-DD, today, or yesterday.")] = "today",
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Show diary entries for a date."""
    from lobster_roll.storage import get_diary_for_date, load_foods, load_meals

    resolved = resolve_day(date_str)
    entries = get_diary_for_date(resolved)
    foods = load_foods()
    meals = load_meals()

    resolved_entries = []
    for entry in entries:
        macros = resolve_entry_macros(entry, foods, meals)
        resolved_entries.append({**entry, "macros": macros})

    emit("diary_day", {"date": resolved, "entries": resolved_entries, "count": len(resolved_entries)}, json_output)


@diary_app.command("remove")
def diary_remove(
    date_str: Annotated[str, typer.Option("--date", help="Date of the entry.")] = "today",
    time_str: Annotated[str, typer.Option("--time", help="Time of the entry (HH:MM).")] = "",
    entry_id: Annotated[str, typer.Option("--entry-id", help="The food or meal id of the entry.")] = "",
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Remove a diary entry by date, time, and entry id."""
    from lobster_roll.storage import remove_diary_entry

    resolved = resolve_day(date_str)
    if not time_str or not entry_id:
        fail(LobsterError("missing_args", "Both --time and --entry-id are required.", "Use 'diary show --date <date>' to find the entry."))

    try:
        removed = remove_diary_entry(resolved, time_str, entry_id)
        emit("diary_entry_removed", {"removed": removed}, json_output)
    except LobsterError as e:
        fail(e)
