from __future__ import annotations

import os
import sys
from typing import Annotated

import typer

from lobster_roll.constants import CAPABILITIES
from lobster_roll.output import STATE, emit

app = typer.Typer(help="Agent-ready nutrition diary — foods, meals, and daily tracking")

from lobster_roll.commands.diary import diary_app
from lobster_roll.commands.food import food_app
from lobster_roll.commands.meal import meal_app
from lobster_roll.commands.summary import summary_app

app.add_typer(food_app, name="food")
app.add_typer(meal_app, name="meal")
app.add_typer(diary_app, name="diary")
app.add_typer(summary_app, name="summary")


@app.callback()
def main(
    agent: Annotated[
        bool,
        typer.Option(
            "--agent",
            help="Agent mode: no prompts, no rich formatting, structured JSON errors.",
        ),
    ] = False,
) -> None:
    STATE["agent"] = agent or os.environ.get("LOBSTER_ROLL_AGENT") == "1"


@app.command()
def capabilities(
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON for agents.")] = False,
) -> None:
    """List agent-safe commands and their contracts."""
    emit("capabilities", {"commands": CAPABILITIES}, json_output, meta={})


if __name__ == "__main__":
    try:
        app()
    except BrokenPipeError:
        sys.exit(0)
