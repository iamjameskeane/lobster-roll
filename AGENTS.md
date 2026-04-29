# AGENTS.md

Guidance for coding agents working on `lobster-roll`.

## North star

`lobster-roll` is a personal nutrition diary for agents, exposed as a CLI.

Three atoms:
- **food** — a single ingredient with nutrition per 100g
- **meal** — a reusable recipe made of foods with amounts
- **diary** — daily log of meals and foods eaten

Optimize for:
1. deterministic behavior
2. stable JSON contracts
3. structured errors
4. no prompts in agent mode
5. small normalized outputs by default
6. runtime introspection via `capabilities`

## Development loop

Use TDD for behavior changes:

```bash
python -m pytest tests/test_cli.py::test_name -q
python -m pytest -q
```

Install locally:

```bash
pip install -e '.[dev]'
```

## CLI contract

- `--json` commands emit response envelopes to stdout.
- `--agent` forces structured error envelopes.
- Human diagnostics go to stderr.
- Data stored in `~/.lobster-roll/` as CSV files.

## Command taxonomy

- `food add` / `food list` / `food show` / `food remove` — manage personal food library
- `meal add` / `meal list` / `meal show` / `meal remove` — manage reusable recipes
- `diary log` / `diary show` / `diary remove` — log and query daily intake
- `summary today` / `summary date` / `summary week` — macro summaries
- `capabilities` — list agent-safe commands

## Adding commands

1. Add tests first.
2. Return a stable envelope: `ok`, `schema_version`, `data`, `warnings`, `meta`.
3. Add the command to `CAPABILITIES`.
4. Update `skills/lobster-roll/SKILL.md` if it changes the agent workflow.
5. Run `pytest -q` before committing.

## Git identity

```bash
git config user.name "Clawsaurusrex"
git config user.email "clawsaurusrex@agentmail.to"
```
