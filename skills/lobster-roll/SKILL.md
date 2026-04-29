---
name: lobster-roll
description: Agent-ready nutrition diary CLI for tracking foods, meals (reusable recipes), and daily intake. Three atoms: food, meal, diary. CSV-backed, JSON-enveloped, designed for Hermes agent integration.
tags: [nutrition, food, meals, diary, calories, macros, tracking, cli, agent]
related_skills: [garmin-agent-flows, garmin-connect-auth]
---

# Lobster Roll

Personal nutrition diary for agents. Three atoms:

- **food** — a single ingredient with nutrition per 100g (id, name, per_grams, calories, protein_g, carbs_g, fat_g, fiber_g, source)
- **meal** — a reusable recipe = list of foods with grams (id, name, ingredients as `food_id:grams|food_id:grams`)
- **diary** — daily log = meals or foods eaten with date, time, type, entry_id, amount_g, notes

## Orientation (CRITICAL — do this every session)

Before doing anything, read the schema and check what exists:

```bash
# 1. Read the schema — understand conventions
read_file ~/.lobster-roll/SCHEMA.md

# 2. Check current state
lobster-roll food list --json
lobster-roll meal list --json
lobster-roll diary show --date today --json

# 3. Check recent activity
read_file ~/.lobster-roll/log.md offset=<last 20 lines>
```

Only after orientation should you add foods, create meals, or log entries. This prevents:
- Adding duplicate foods
- Creating meals that reference missing foods
- Missing existing meals that match what the user ate

## Quick reference

```bash
# Foods — manage personal library
lobster-roll food add "Chicken Breast" --per 100 --cal 120 --protein 23 --carbs 0 --fat 2.6 --source label --json
lobster-roll food list --json
lobster-roll food show chicken_breast --json
lobster-roll food remove chicken_breast --json

# Meals — reusable recipes
lobster-roll meal add "Morning Oats" --ingredients "oats:80|whey:30|banana:120" --json
lobster-roll meal list --json
lobster-roll meal show morning_oats --json
lobster-roll meal remove morning_oats --json

# Diary — log intake
lobster-roll diary log morning_oats --date 2026-04-29 --time 08:00 --json
lobster-roll diary log chicken_breast --type food --amount 200 --date 2026-04-29 --time 13:00 --json
lobster-roll diary show --date 2026-04-29 --json
lobster-roll diary remove --date 2026-04-29 --time 13:00 --entry-id chicken_breast --json

# Summaries — macro rollups
lobster-roll summary today --json
lobster-roll summary date 2026-04-29 --json
lobster-roll summary week --json

# Introspection
lobster-roll capabilities --json
```

## The Three Atoms

### Food — single ingredient with nutrition per 100g
- Fields: id, name, per_grams, calories, protein_g, carbs_g, fat_g, fiber_g, source
- Add from labels, recipes, or manual entry
- Auto-slugified IDs from names

### Meal — reusable recipe made of foods
- Fields: id, name, ingredients (food_id:grams|food_id:grams format)
- Log once, use forever
- Must reference existing food IDs

### Diary — daily log of what was eaten
- Fields: date, time, entry_type (meal/food), entry_id, amount_g, notes
- Auto-detects type from entry_id
- The primary tracking surface

## Agent workflow

### Adding foods from nutrition labels

When the user sends a photo of a nutrition label:
1. Extract: serving size, calories, protein, carbs, fat, fiber
2. Generate a slug id from the food name
3. Call `lobster-roll food add` with the extracted values
4. Confirm to the user

### Creating meals from descriptions

When the user describes a meal/recipe:
1. Identify ingredients and approximate amounts
2. Ensure all foods exist in the library (add missing ones first)
3. Call `lobster-roll meal add` with the ingredient string
4. Show the calculated macros

### Daily logging

When the user says what they ate:
1. Match to an existing meal if possible (check `meal list`)
2. Otherwise match to foods and log individually
3. Call `lobster-roll diary log` for each item
4. After logging, optionally show `summary today`

### End-of-day summary

```bash
lobster-roll summary today --json
```

Returns totals for calories, protein, carbs, fat, fiber plus per-entry breakdown.

### Weekly review

```bash
lobster-roll summary week --json
```

Returns 7-day breakdown with daily totals and week averages. Useful for:
- Protein intake consistency
- Calorie trend
- Macro balance

## Data storage

All data stored in `~/.lobster-roll/` as CSV files:
- `foods.csv` — personal food library
- `meals.csv` — reusable recipes
- `diary.csv` — daily intake log
- `SCHEMA.md` — conventions and rules for agents
- `index.md` — content catalog
- `log.md` — chronological action log

Override with `LOBSTER_ROLL_DATA` environment variable.

## Macro calculation

Macros are calculated by resolving the food chain:
- Diary entry → (meal → foods × grams) or (food × amount)
- All macros normalized to per_grams basis
- Amount overrides scale proportionally

## Integration with garmin-claws

Lobster Roll nutrition data pairs with garmin-claws fitness data:
- Calories in (lobster-roll) vs calories out (garmin-claws daily summary)
- Protein intake vs training load (garmin-claws training load-balance)
- Meal timing vs sleep quality (garmin-claws sleep summary)

Future: combined daily coach flow that considers both nutrition and training readiness.

## Pitfalls

- Storage imports constants module dynamically (`from lobster_roll import constants`) — do NOT use `from lobster_roll.constants import X` in storage.py or test isolation breaks
- The Typer runner in tests creates separate invocations — CSV files persist across runner.invoke calls within the same test, so plan test data accordingly
- Food IDs are auto-slugified from names — watch for collisions (e.g. "Chicken Breast" and "chicken breast" produce the same id)
- Always orient first — read SCHEMA + food list + meal list + recent diary before any operation
