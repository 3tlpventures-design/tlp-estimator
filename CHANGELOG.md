# Changelog

## [Unreleased]

### Added
- Excel → JSON pricing pipeline (`scripts/build_pricing.py`, `scripts/config.py`)
- Round-trip tests (`tests/test_build_pricing.py`) that lock pipeline output to
  the captured `MASTER_PRICING` oracle plus a guardrail against raw prices in
  build stdout
- `pricing.json` loaded at runtime by `index.html`
- Source-of-truth spreadsheets under `data/`:
  - `Allowance_Pricing_Levels.xlsx` (15 category tabs)
  - `BLANK_Allowances_3_5_2024.xlsm` (Stairs)
- `tests/expected_pricing.json` — oracle snapshot of pricing at pipeline cutover

### Changed
- `index.html` fetches `pricing.json` at init; inline `MASTER_PRICING` is now
  fallback-only (used if the fetch fails)

### Notes
- No behavioral change visible to estimator users: rates match the previous
  inline values exactly (79 categories, 7 `tlpFixed` entries preserved)
- Source spreadsheets were bootstrapped from the extracted oracle. Dad can
  replace them with real TLP workbooks using the same schema
  (`category_id | t1..t5 | tlpFixed | notes`)
