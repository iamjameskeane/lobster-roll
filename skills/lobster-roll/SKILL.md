---
name: lobster-roll
description: "Agent-ready nutrition diary CLI for tracking foods, meals (reusable recipes), and daily intake. Three atoms: food, meal, diary. CSV-backed, JSON-enveloped, designed for Hermes agent integration."
tags: [nutrition, food, meals, diary, calories, macros, tracking, cli, agent]
triggers:
  - lobster-roll
  - nutrition tracking
  - food diary
  - calorie tracking
  - macro tracking
  - meal logging
  - what did I eat
  - protein intake
---

# Lobster Roll

Personal nutrition diary for agents. Four atoms:

- **food** — a single ingredient with nutrition per 100g
- **meal** — a reusable recipe = list of foods with grams
- **diary** — daily log of meals and foods eaten
- **profile** — nutrition targets with date ranges

## When This Skill Activates

- User says what they ate or sends a food label photo
- User asks about calorie/macro intake or targets
- User wants to set nutrition goals
- Agent needs consumption data for calorie balance calculations

## Orientation (CRITICAL — do this every session)

Before doing anything, check what exists:

```bash
lobster-roll food list --json
lobster-roll meal list --json
lobster-roll diary show --date today --json
lobster-roll profile show --json
```

This prevents adding duplicate foods, creating meals that reference missing foods, or missing existing meals.

## Quick Reference

```bash
# Foods — manage personal library
lobster-roll food add "Chicken Breast" --per 100 --cal 120 --protein 23 --carbs 0 --fat 2.6 --source label --json
lobster-roll food list --json
lobster-roll food show chicken_breast --json
lobster-roll food remove chicken_breast --json

# Meals — reusable recipes with portions
lobster-roll meal add "Protein Shake (2 scoops)" --ingredients "healthyfit_vegan_protein:60" --json
lobster-roll meal list --json
lobster-roll meal show protein_shake_2_scoops --json
lobster-roll meal remove protein_shake_2_scoops --json

# Diary — log intake
lobster-roll diary log morning_oats --date 2026-04-29 --time 08:00 --json
lobster-roll diary log chicken_breast --type food --amount 200 --date 2026-04-29 --time 13:00 --json
lobster-roll diary show --date 2026-04-29 --json
lobster-roll diary remove --date 2026-04-29 --time 13:00 --entry-id chicken_breast --json

# Profile — nutrition targets
lobster-roll profile set --calories 2200 --delta -750 --protein 180 --notes "cutting phase" --json
lobster-roll profile show --json
lobster-roll profile history --json

# Summaries — macro rollups
lobster-roll summary today --json
lobster-roll summary date 2026-04-29 --json
lobster-roll summary week --json

# Introspection
lobster-roll capabilities --json
```

## The Three Atoms

### Food — single ingredient with nutrition per 100g

Fields: id, name, per_grams, calories, protein_g, carbs_g, fat_g, fiber_g, source

- Add from labels, recipes, or manual entry
- Auto-slugified IDs from names (e.g., "Chicken Breast" → `chicken_breast`)
- Watch for ID collisions (case-insensitive slugs)

### Meal — reusable recipe made of foods

Fields: id, name, ingredients (`food_id:grams|food_id:grams` format)

- Log once, use forever
- Must reference existing food IDs
- **Use meals as portion shortcuts** — "1 scoop" = 30g, "2 squares" = 40g

### Diary — daily log of what was eaten

Fields: date, time, entry_type (meal/food), entry_id, amount_g, notes

- Auto-detects type from entry_id (meal or food)
- Amount override scales proportionally for meals
- Notes field for context ("3 coffees, 150ml each")

### Profile — nutrition targets

Fields: daily_calories, calorie_delta, protein_g, carbs_g, fat_g, valid_from, valid_until, notes

- Multiple profiles with date ranges
- Previous profile auto-closed when new one set
- Agent compares diary totals to profile targets

## Agent Workflow

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

**Portion shortcuts:** Create meals for repeatable portions. "1 scoop" of protein powder = a meal with 30g. "1 square" of chocolate = a meal with 20g. Then logging is just `lobster-roll diary log protein_shake`.

### Daily logging

When the user says what they ate:
1. Match to an existing meal if possible (check `meal list`)
2. Otherwise match to foods and log individually
3. Call `lobster-roll diary log` for each item
4. After logging, optionally show `summary today`

### Managing targets

When the user wants to set or change nutrition goals:
```bash
lobster-roll profile set --calories 2200 --delta -500 --protein 180 --carbs 200 --fat 60 --notes "cutting phase" --json
```

### Calorie balance (agent-side)

lobster-roll tracks consumed. garmin-claws tracks burned. The agent bridges them:

```bash
garmin-claws flow run calories --json    # burn data
lobster-roll summary today --json        # consumption data
```

Budget = projected_burn. Remaining = budget - consumed. No cross-dependency.

## Data Storage

All data stored in `~/.lobster-roll/` as CSV files:
- `foods.csv` — personal food library
- `meals.csv` — reusable recipes
- `diary.csv` — daily intake log
- `profile.json` — nutrition targets with date ranges
- `SCHEMA.md` — conventions and rules for agents
- `index.md` — content catalog
- `log.md` — chronological action log

Override with `LOBSTER_ROLL_DATA` environment variable.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `food_not_found` | Food ID doesn't exist | Run `food list` to see available foods |
| `meal_not_found` | Meal ID doesn't exist | Run `meal list` to see available meals |
| `entry_not_found` | Diary entry doesn't match | Run `diary show --date <date>` to see entries |
| `food_exists` | Duplicate food ID | Use `food show` to see existing, or choose different id |
| No profile set | No targets configured | Run `profile set` with targets |

## Pitfalls

- **Orientation first** — always check food list, meal list, and diary before adding/logging
- **Food ID collisions** — "Chicken Breast" and "chicken breast" produce the same slug
- **Meals as portions** — use meal definitions for "1 scoop", "2 squares" etc., not raw grams every time
- **Profile history** — `profile set` closes the previous profile automatically
- **All macros tracked** — calories, protein, carbs, fat, fiber are all logged, not just protein
- **CSV isolation in tests** — storage imports constants dynamically, don't use `from lobster_roll.constants import X` in storage.py
