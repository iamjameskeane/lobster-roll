from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Annotated

import typer

from lobster_roll import constants
from lobster_roll.errors import LobsterError
from lobster_roll.output import emit, fail, now_iso

profile_app = typer.Typer(help="Manage nutrition targets")


def _profile_path() -> Path:
    return constants.DATA_DIR / "profile.json"


def _load_profiles() -> list[dict]:
    path = _profile_path()
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
        return data if isinstance(data, list) else [data]


def _save_profiles(profiles: list[dict]) -> None:
    constants.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_profile_path(), "w") as f:
        json.dump(profiles, f, indent=2, default=str)


def _get_active_profile(profiles: list[dict]) -> dict | None:
    """Get the most recent active profile (valid_until is null or future)."""
    today = date.today().isoformat()
    active = [p for p in profiles if not p.get("valid_until") or p["valid_until"] >= today]
    if not active:
        return None
    # Return most recent by valid_from
    return max(active, key=lambda p: p.get("valid_from", ""))


@profile_app.command("show")
def profile_show(
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Show current nutrition targets."""
    profiles = _load_profiles()
    active = _get_active_profile(profiles)
    if active is None:
        emit("profile", {"active": None, "message": "No profile set. Use 'profile set' to create one."}, json_output)
        return
    emit("profile", {"active": active, "history_count": len(profiles)}, json_output)


@profile_app.command("set")
def profile_set(
    calories: Annotated[int, typer.Option("--calories", help="Target daily calories.")] = 0,
    delta: Annotated[int, typer.Option("--delta", help="Calorie delta from maintenance (+/-).")] = 0,
    protein: Annotated[int, typer.Option("--protein", help="Target daily protein (g).")] = 0,
    carbs: Annotated[int, typer.Option("--carbs", help="Target daily carbs (g).")] = 0,
    fat: Annotated[int, typer.Option("--fat", help="Target daily fat (g).")] = 0,
    notes: Annotated[str, typer.Option("--notes", help="Why this profile.")] = "",
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Set new nutrition targets. Closes previous profile and creates new one."""
    today = date.today().isoformat()
    profiles = _load_profiles()

    # Close previous active profile
    for p in profiles:
        if not p.get("valid_until"):
            p["valid_until"] = today

    # Create new profile
    new_profile = {
        "daily_calories": calories,
        "calorie_delta": delta,
        "protein_g": protein,
        "carbs_g": carbs,
        "fat_g": fat,
        "valid_from": today,
        "valid_until": None,
        "notes": notes,
    }
    profiles.append(new_profile)
    _save_profiles(profiles)
    emit("profile_set", {"profile": new_profile}, json_output)


@profile_app.command("history")
def profile_history(
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """Show all past and current profiles."""
    profiles = _load_profiles()
    emit("profile_history", {"profiles": profiles, "count": len(profiles)}, json_output)
