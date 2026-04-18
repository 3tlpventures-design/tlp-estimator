# TLP Home Selection Estimator

**Version:** v1.0  
**Company:** TLP Ventures LLC  
**Stack:** Single-file HTML/CSS/JavaScript — no build step, no server required

---

## Overview

A browser-based estimating tool for interior finish selections on residential construction projects. Runs entirely from `index.html` — open it in any modern browser. All data is saved to `localStorage` automatically.

---

## Features

### Project Setup
- Client contact info, project ID, job address, and start date
- Budget entry with running remaining-budget display
- Global finish tier selector (T1–T5) applied across all rooms by default
- Per-floor ceiling height overrides (Floor 1 / Floor 2)

### Room Intake
- Add unlimited rooms with name, type, dimensions (L × W × H), and location
- 17 room types supported (Bedroom, Kitchen, Bath, Living Area, Stairs, Garage, Exterior, and more)
- 10 location tags (Front Left, Rear Right, Center, etc.)
- Floor SF auto-calculated from L × W and displayed live
- Checkbox selection per row with select-all toggle in header
- **Delete Selected** — remove one, several, or all rooms at once
- Individual row delete button for single-room removal

### Room Selections (per room)
Each room gets a dedicated selection sheet with cards for:

| Category | Details |
|---|---|
| **Flooring** | Hardwood, LVP, Tile, Carpet — per SF with 10% waste factor |
| **Paint & Wall Finishes** | Wall SF auto-calculated from dimensions |
| **Trim & Millwork** | Base, casing, crown — auto-calculated from perimeter LF |
| **Ceilings** | Coffered, tray, barrel vault, specialty treatments |
| **Lighting** | Chandeliers, pendants, vanity, ceiling fans, sconces, flush mounts |
| **Cabinetry** | Base/upper, island, vanity, hood surrounds |
| **Countertops & Backsplash** | Stone, tile, custom |
| **Plumbing Fixtures** | Kitchen faucets, sinks, tubs, showers, toilets, pot fillers |
| **Bath Accessories** | Mirrors, towel bars, shower glass |
| **Appliances** | Refrigerator, range, dishwasher, microwave, hood, washer/dryer |
| **Hardware** | Door knobs, deadbolts, hinges, stops, pocket doors |
| **TLP Electrical** | Recessed cans, dimmers, bulbs, smoke detectors |
| **Specialty** | Fireplaces, stair treads/newels/spindles/rails, shelving, water heaters |

- T5 Premium tier allows manual product/price entry and locks the line item
- Per-item tier overrides (independent of global tier)
- T4 allowance tracking with over/under indicator

### Finish Tiers
| Tier | Label | Description |
|---|---|---|
| T1 | Contractor | Builder-grade baseline |
| T2 | Good | Entry-level upgraded finish |
| T3 | Better | TLP standard default ★ |
| T4 | Best | High-end selection |
| T5 | Premium | Custom / specify actual product & price |

### Reports
- **Dashboard** — all rooms at a glance with totals, tier, and progress indicators
- **Division Summary** — cost breakdown by trade category with bar chart visualization; printable
- **Pricing Tables** — TLP historical rates pre-loaded for all 6 major categories; Tennessee tax rate (9.25%) applied

### Top Bar (live meters)
- Selections Budget
- Remaining Budget (color-coded: green / gold / red)
- This Room total
- Completion progress bar

---

## Files

| Path | Description |
|---|---|
| `index.html` | Complete application — all HTML, CSS, and JavaScript |
| `pricing.json` | Authoritative pricing table loaded at runtime. Build artifact — do not hand-edit |
| `data/` | Source-of-truth spreadsheets. See `data/README.md` |
| `scripts/` | Python build pipeline (`build_pricing.py`, `config.py`) |
| `tests/` | Round-trip tests against the captured pricing oracle |
| `CHANGELOG.md` | Notable changes |

---

## Usage

1. Open `index.html` in a browser (Chrome or Edge recommended)
2. Go to **Project Setup** — enter client info and set budget/tier
3. Go to **Room Intake** — add all rooms with dimensions
4. Click **Next: Room Selections** to price out each room
5. Review totals in **Dashboard** and **Division Summary**

Data persists in `localStorage`. No account or internet connection required.

---

## Updating pricing

Pricing lives in `data/Allowance_Pricing_Levels.xlsx` and
`data/BLANK_Allowances_3_5_2024.xlsm`. Edit the spreadsheet, then regenerate
the JSON the site loads:

```
pip install -r scripts/requirements.txt
python scripts/build_pricing.py
pytest tests/
```

Commit both the updated spreadsheet and the regenerated `pricing.json`.
GitHub Pages picks up the new rates on next deploy. The build script prints
category counts and per-tier coverage only — it never echoes raw prices.

If `pricing.json` fails to load at runtime, `index.html` falls back to its
inline copy of `MASTER_PRICING` so the site keeps working.

---

## Recent Changes

- Fixed: L/W/H dimension inputs no longer lose focus after each keystroke
- Added: Checkbox column in Room Intake with select-all toggle
- Added: **Delete Selected** button to remove checked rooms with confirmation
