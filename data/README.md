# Pricing source spreadsheets

These workbooks are the **source of truth** for TLP pricing. `pricing.json` at
the repo root is a build artifact regenerated from them by
`scripts/build_pricing.py`.

## Files

- `Allowance_Pricing_Levels.xlsx` — lights, plumbing, sinks/tubs, hardware,
  cabinets, water heater, shelving, appliances, flooring, countertops, tile,
  paint, fireplace, bath accessories. One tab per category section.
- `BLANK_Allowances_3_5_2024.xlsm` — stairs.

## Schema per tab

Each tab has a header row followed by one row per category:

| column        | meaning |
|---------------|---------|
| `category_id` | stable key used in `index.html` (e.g. `light-chandelier-low`). Don't rename. |
| `t1`..`t5`    | tier rates. Leave blank for "not offered at this tier". |
| `tlpFixed`    | `TRUE` when TLP supplies the item at a flat rate regardless of tier. Blank otherwise. |
| `notes`       | freeform — not read by the pipeline. |

## Updating prices

1. Edit the cells.
2. Run `python scripts/build_pricing.py` from the repo root.
3. Commit both the spreadsheet and the regenerated `pricing.json`.
4. Push. GitHub Pages deploys automatically.

The pipeline fails fast if a row is missing the `category_id` key or if the
same `category_id` appears in more than one tab.

## Bootstrapping note

The current values in these files were generated from `MASTER_PRICING` in the
original `index.html` so the existing site behavior is preserved exactly.
Replace either file with a real TLP spreadsheet that has the same schema when
one is available.
