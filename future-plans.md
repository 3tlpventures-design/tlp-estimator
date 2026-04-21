# TLP Estimator — Future Plans

Forward-looking roadmap. Phase 1 (`pricing.json` loaded at runtime from
Dad-editable spreadsheets) is live. Everything below is directional — each
phase gets its own concrete plan + atomic-commit sequence before we build.

**Rewritten April 2026** after seeing Wayne's actual workbook
(`data/reference/TLP MASTER PRICING TABLE.xlsx`). Large parts of what was
originally sketched here as "future" are already designed on his side.
This version distinguishes **what we build** (customer-facing estimator)
from **what Wayne/Cody builds** (TLP cost-intelligence backend).

---

## Two systems, one business

| | **This repo** — the estimator | **Wayne's workbook** — the cost database |
|---|---|---|
| Audience | Clients, salespeople, field estimators | Owner, purchasing, Wayne |
| Shape | 79 categories × 5 tiers (`pricing.json`) | Invoice rows × cost columns |
| Question it answers | "What does a Tier 3 vanity light cost the client?" | "What did a 2×12 SYP cost on Kupin Aug 2025?" |
| Maintained by | Chandler + Claude (this session) | Wayne + Cody (another Claude instance, via Python/gspread) |
| Update cadence | Whenever spreadsheet is edited | Every new invoice + weekly market scrape |
| Source of truth for | Customer allowance tiers | Real TLP paid costs + market commodity prices |

**These systems meet in Phase 2 (see below).** Before that, they are
parallel tracks. Wayne is already deep into his side — the "Phase 4
scraping" and "Phase 5 trend analysis" I originally speculated about here
are literally designed in his workbook's MARKET INDEX sheet and his Flex
Rules documentation. Much of this roadmap is now about *consuming* what
he builds, not building it ourselves.

---

## What Wayne has already designed

Documented verbatim from his workbook's README tab. Worth internalizing
before writing any follow-on code.

### Four-stage estimate pipeline

| Stage | What it is | Pricing source | Valid for | Trigger |
|---|---|---|---|---|
| **Estimate** | Best guess | This table + flex % + fluff buffer | 30 days | Client inquiry |
| **Bid** | Locked number | Actual vendor quotes override table | 30 days | Selections complete AND start within 30 days |
| **Contract** | Signed bid | Locked, change-order only | Project life | Client signature |
| **Actual** | What was paid | Real invoices — feeds the table | Permanent | Invoice received |

**Hard rule:** an estimate cannot become a bid until (1) all selections are
complete and (2) the project starts within 30 days so suppliers can lock.
Our current estimator is purely an Estimate-stage tool. Bid/Contract/Actual
are Phase 2+ territory.

### Flex Rules (materials repricing)

| # | Trigger | Action |
|---|---|---|
| 1 Hold | Market decreased <8% | Do nothing, keep the margin |
| 2 Partial | Market decreased 8–15%, **sustained 45+ days** | Apply 50% of the decrease + flag for review |
| 3 Full | Market decreased >15%, **sustained 60+ days** | Apply full decrease, reset benchmark |
| 4 Lock | Item is in active bid or contract | Never adjust |
| 5 Forward | 3 consecutive months of price **increases** | Add forward projection = trend% × months-until-project-start |
| ⚠ COVID Alert | Vendors reduce lock-in below 14 days | System alert, stop relying on table, get live quotes |

### Cost Type taxonomy

Every line item carries a Cost Type. More granular than our current
`tlpFixed` boolean:

| Cost Type | Where it lives | Example |
|---|---|---|
| Materials | MATERIALS tab + MASTER PRICING TABLE | Lumber package, priced per BF/LF/EA |
| Labor | LABOR tab + MASTER PRICING TABLE | Framing crew, per hour or LS |
| Both | MASTER PRICING TABLE only | Sub who supplies + installs with no breakdown |
| Equipment | MASTER PRICING TABLE only | Dumpster, crane, lift rental |
| Subcontract | MASTER PRICING TABLE only | Fixed-price sub scope, no breakdown known |

Our `pricing.json` only represents `Materials` + `Both` right now. Labor is
implicit in most customer-allowance rates. If we ever want to decompose
allowances into per-room labor + materials, we adopt this taxonomy.

### Material source priority

1. The known-paid table (never scrape what we've already paid for)
2. Menards (LVLs, engineered lumber)
3. Home Depot API (dimensional lumber, hardware, appliances, commodities)
4. Builders FirstSource (full lumber packages, trusses)
5. Live vendor quote — estimator gets it and updates table

Trusses in particular get a 90-day refresh rule because they're
manufactured assemblies, not raw lumber. Don't trust scraped prices for
them.

### Other structures already in his workbook

- **ASSEMBLIES** — composed pricing (e.g. New 110v Outlet = wire + box +
  receptacle + plate + breaker + rough-in labor + trim-out labor + 20%
  O&P). This is how a per-EA price for a complete task gets built. Our
  estimator has no concept of this yet.
- **MARKET INDEX** — weekly commodity-price tracker. Already scaffolded
  for the scraping future-me thought we'd have to design.
- **BENCHMARKS** — $/SF Low/Mid/High per building system. Populated as
  MATERIALS grows.
- **SOURCE LOG** — 92 rows. Every invoice indexed with file path, Cost
  Type, and "entered into master table?" flag. Auditable.
- **Confidence** column (HIGH/MED/LOW) on every cost row. We should
  mirror this concept when we start surfacing TLP-cost-derived allowances.

---

## Phase 2 — The meeting point

This is the phase where the two systems need to talk. Architecturally the
most important phase, because everything downstream depends on the
contract between Wayne's data and ours.

### Goals

- Move `pricing.json` behind a real backend (Cloudflare Worker + D1).
- **Effective-dated rates** — every saved bid locks to the pricing row that
  existed when the bid was created. Wayne's Flex Rules never retroactively
  change a signed contract.
- Admin UI behind auth for editing allowances without touching Excel.
- Split `index.html` → `index.html + app.js + styles.css` so the frontend
  is maintainable.

### The cross-system question

**How does Wayne's cost data become a customer-allowance tier rate?**
This is not obvious and is not yet designed.

Some categories have a natural mapping:
- `tlp-can-6` (TLP-supplied 6" recessed can) → MATERIALS tab row for a
  recessed can + LABOR tab row for rough-in/trim-out → ASSEMBLY row →
  per-EA price. That's the T-all rate (same across tiers, `tlpFixed`).
- `floor-hardwood` T1 → actual-paid hardwood + actual-paid installation
  labor, averaged across recent Kupin-tier jobs.

Other categories don't map:
- `light-chandelier-low` → Home Depot retail price for a $135 chandelier.
  This is a customer-allowance guess, not a TLP cost. T1–T4 are quality
  tiers defined by the retail price bands Wayne targets — not by what TLP
  pays.

The bridge is probably **different strategies per Cost Type**:
- `Materials + Both`-backed categories → pull from Wayne's actual-paid,
  post-Flex, post-Fluff price.
- Pure customer-allowance categories → stay in our spreadsheet, possibly
  with Phase 5 scraping for market refresh.
- `Labor`-dominant categories (framing, trim, drywall) → not in the
  current `pricing.json` at all, because the estimator currently prices
  fixtures/finishes not scopes-of-work.

**Deliverable for Phase 2 design:** a per-category table declaring
(a) data source (Wayne / spreadsheet / scrape), (b) refresh cadence,
(c) Flex Rule eligibility, (d) tier derivation method. Then build once.

### Coordination with Cody

Two AIs on one business. Minimal viable boundary:

- **Cody owns** MATERIALS, LABOR, ASSEMBLIES, MASTER PRICING TABLE, SOURCE
  LOG, MARKET INDEX. He writes the flex logic, runs the weekly scraper,
  handles invoice ingestion.
- **We own** `pricing.json`, `index.html`, the customer-facing flow,
  saved bids, and (Phase 2) the backend admin UI.
- **Interface** (to design): Cody publishes a read-only artifact —
  probably a JSON or CSV snapshot from his workbook, delivered via
  GitHub commit to a branch we can read, or via API. Our backend
  consumes it. No direct write-back from us to Wayne's workbook.

We should talk to Wayne (and through him, Cody) before finalizing this
contract. Premature design here costs us.

---

## Phase 3 — TLP-cost-derived allowances (depends on Phase 2)

Once Cody publishes a stable artifact from Wayne's workbook, wire
specific `pricing.json` categories to pull from it.

- Start with the highest-confidence, highest-coverage categories — likely
  `tlp-*` (TLP-supplied electrical, already flat-rate), then materials
  Wayne has real historical data for.
- Keep manual override capability. If Cody's rollup produces a weird
  number, the admin UI lets us pin a rate until the upstream is fixed.
- Surface Confidence in the UI. "This rate is HIGH-confidence, derived
  from 12 invoices over 6 months" reads different from "This rate is a
  LOW-confidence retail-price guess."

---

## Phase 4 — Allowance scraping (largely Cody's territory)

Wayne's MARKET INDEX is already scaffolded. The work here is:

1. Cody fills in the sources (Home Depot API, Menards, Builders FirstSource,
   commodity indices for lumber/copper/steel).
2. The weekly script runs, Flex Rules apply, adjusted prices flow into the
   published artifact.
3. We consume the artifact (per Phase 3 wiring).

Our responsibility: don't let a broken scraper silently poison estimates.
Show estimators a freshness indicator ("last refreshed 3 days ago — OK"
vs "last refreshed 23 days ago — stale, get a live quote"). Show a
COVID-alert banner when Cody's workbook flags a lock-in window <14 days.

---

## Phase 5 — Forward projection (Wayne's Flex Rule 5)

Already specified: 3 consecutive months of price increases → add
`trend% × months_until_start` to the current price.

Our job on the estimator side is **presentation**:
- Show both the current price and the projected price.
- Explain which rule applied ("Rule 5 Forward: lumber up 12% over 3mo,
  project starts in 2mo, adding 8% to this estimate").
- Let the estimator override with live quotes for any affected line.

---

## What we are explicitly NOT building

- No separate scraping infrastructure. Cody handles that on Wayne's side.
- No ML price prediction model. Flex Rule 5's linear projection is enough
  for now, and futures markets / ENR / RSMeans indices are better sources
  than home-rolled ML for categories where we need a forecast.
- No appliance pricing until Wayne has real data for it. For now
  appliance `t1..t5` remain `null` in `pricing.json`.
- No bid/contract/actual tracking yet — Phase 2's scope — and even then
  only the bid side. Actuals live in Wayne's workbook, not ours.

---

## Dependencies

```
  Phase 1 (done)  →  Phase 2 (meeting point)  →  Phase 3 (wire categories)
                           ↑                           ↓
                   Cody's work              Phase 4 (freshness UI)
                                                       ↓
                                            Phase 5 (projection UI)
```

Phase 2 blocks everything. Before we touch Phase 2 code, we need a
conversation with Wayne about:
1. What artifact Cody can reliably publish from his workbook (and where).
2. Which of the 79 categories he has real cost data for vs. which remain
   customer-allowance guesses.
3. Whether our admin UI should also be able to write back to influence
   his workbook (probably no, one-way is simpler and safer).

---

## Terminology note

Wayne's workbook is called "TLP MASTER PRICING TABLE" and has an internal
sheet of the same name. We originally extracted the inline JS object as
`MASTER_PRICING` from `index.html`. Same name, different things. Worth
renaming ours — likely `ALLOWANCE_PRICING` — in a future commit, along
with the JSON file. Low priority; tracked as a cleanup task rather than
a phase.
