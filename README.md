# Lobster Roll 🦞

Agent-ready nutrition diary CLI — foods, meals, and daily tracking.

## Three atoms

- **food** — a single ingredient with nutrition per 100g
- **meal** — a reusable recipe made of foods
- **diary** — daily log of what you ate

## Install

```bash
pip install -e '.[dev]'
```

## Usage

```bash
# Add foods
lobster-roll food add "Chicken Breast" --per 100 --cal 120 --protein 23

# Create meals
lobster-roll meal add "Morning Oats" --ingredients "oats:80|whey:30"

# Log intake
lobster-roll diary log morning_oats

# Get summaries
lobster-roll summary today --json
lobster-roll summary week --json
```

## Agent mode

All commands support `--json` for structured JSON output and `--agent` for structured error envelopes.

## Data

Stored in `~/.lobster-roll/` as CSV files. Override with `LOBSTER_ROLL_DATA` env var.
