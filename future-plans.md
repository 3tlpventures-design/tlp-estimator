# TLP Estimator — Future Plans

Forward-looking roadmap. Phase 1 (pricing.json loaded at runtime from
Dad-editable spreadsheets) is done. Everything below is directional — each
phase will get its own concrete plan + atomic-commit sequence before we
start building.

---

## Vision (from Wayne)

> "I'm building it for now so once I get through this past two years of data
> it will be a badass pricing table built off our real cost. Should tighten
> the shit out of estimating. Scheduling, coordinating. This sheet I built
> is gonna be built with a code that runs on routines to scrape the internet
> for pricing to keep up with commodities, to watch trends in the pricing of
> the commodities to put in an increase or decrease factor with a cushion to
> keep from lowering prices too quickly — but to take into consideration the
> cost of a commodity 3 months in the future that would help ensure the
> estimate price last known could be increased by that predict item."

Translated:

1. Replace guess-work with 2 years of real TLP job-cost data.
2. Automate price updates for commodity-driven line items.
3. Smooth out price changes (hysteresis) so estimates don't whipsaw.
4. Forward-project prices ~3 months so estimates reflect *build-time* cost,
   not *estimate-time* cost.

---

## Core architectural decision: TLP cost basis vs. customer allowances

Not every line item should be scraped from the internet. Two classes:

| Class | Examples | Source of truth | Auto-update? |
|---|---|---|---|
| **TLP cost basis** — what TLP charges | Labor, TLP-supplied electrical (`tlp-*` today — cans, dimmers, bulbs, smoke detectors), TLP-stocked hardware (hinge stops, wall stops, sliding door hardware) | Wayne's real job-cost data (the 2-year rollup) | **No.** Human-reviewed only. Proprietary. |
| **Customer allowances** — budget for items the customer picks and buys from a retailer | Light fixtures, plumbing fixtures, cabinets, appliances, flooring, countertops, tile | Market pricing (commodity indices + retailer signals) | **Yes** — eventually. |

The `tlpFixed: true` flag in `pricing.json` already marks TLP cost basis
entries (7 today). That flag becomes the gate: scraped updates will only
touch entries *without* `tlpFixed`.

**Non-negotiable:** scraped market data must never overwrite TLP's real
cost data. Pipelines will have separate inputs (Wayne's spreadsheet vs.
commodity feed) and the merger is one-way — TLP cost basis always wins.

---

## Phase 2 — Backend + persistence (from original plan)

Lands the storage layer the later phases need.

- Cloudflare Worker serves `/api/pricing` (authenticated) and `/api/bids`.
- D1 database behind it. Bids persist server-side so multiple devices /
  users see the same data.
- Split `index.html` into `index.html + app.js + styles.css`.
- Admin page behind auth for editing pricing without touching Excel.
- **Effective-dated rates** — every bid locks to the pricing row that
  existed when the bid was created. Future rate changes never retroactively
  alter old bids. This is the schema change that unlocks everything below.

Scope discipline: Phase 2 does not touch scraping, ML, or predictions. It
just moves the current Phase 1 artifacts behind an API with history.

---

## Phase 3 — Ingest 2 years of TLP job-cost data

Turn Wayne's actual past jobs into the TLP cost basis table.

- Decide the schema: what makes a "cost point" (job, date, category, tier,
  actual rate, quantity, location)?
- Import pipeline — likely another Excel → normalized-table pipeline, same
  shape as the Phase 1 pricing loader but landing into D1 instead of a JSON.
- Rollup rules: how do we go from N historical data points per category to
  one rate per tier? Probably weighted by recency, maybe filter outliers,
  maybe per-region if the data supports it. These are judgment calls Wayne
  should own — the pipeline just needs to expose the knobs.
- **Output:** the `tlpFixed` / TLP-cost rows in `pricing.json` get replaced
  by data-backed rates. Customer-allowance rows unchanged.

Risk to watch: garbage-in. If past job data has bad categorization or
mismatched units, the rollup propagates the mess. Build validation and a
"show me the source rows behind this rate" UI early.

---

## Phase 4 — Allowance scraping

Automate price updates for customer-allowance categories only.

- **Sources.** Start narrow — pick 2–3 categories with the most scrape-able
  data (appliances on Home Depot / Lowe's, lumber index, copper/aluminum for
  wiring and plumbing). Build one scraper, learn what breaks, then expand.
- **Schedule.** Nightly or weekly. Store raw observations in a time-series
  table — `(category, source, date, observed_rate)`. The scraper writes raw
  data only; it never writes directly to `pricing.json`.
- **Review gate before promotion to live pricing.** A scraped price doesn't
  update an allowance until a human (or a trend-analysis job, see Phase 5)
  approves it. Guards against scraper errors, ToS-driven site changes, and
  one-off price glitches.
- **Legal / ToS.** Some retailers prohibit scraping. Prefer APIs, affiliate
  feeds, commodity index providers, or public datasets where available.
  Retailer-site scraping is a last resort and needs rate-limiting plus UA
  identification.

---

## Phase 5 — Trend analysis + forward projection

This is the "badass" layer Wayne described. Also the hardest to get right.

### Increase/decrease with a cushion

Concept: prices can go up quickly but should come down slowly. Asymmetric
smoothing protects margin.

- Rolling window (probably 90 days).
- Price goes up: apply immediately (up to a cap per cycle to avoid shocks).
- Price goes down: apply only after sustained movement (e.g. 60 days below
  the current rate by >5%). A "cushion" threshold Wayne tunes.
- Never let a single data point move the rate. Always require multiple
  observations from independent sources before acting.

### 3-month forward projection

Concept: the estimate is written today, but the material gets bought in 3
months. Use the forward price, not the current price.

- For tracked commodities with futures markets (lumber, copper, steel,
  aluminum, natural gas), read the 3-month forward directly from a futures
  feed. This is the clean path.
- For items without futures markets (most finished goods), the simplest
  approach is an empirical lead-indicator: if commodity X moved Y% over the
  last 90 days and finished-good Z historically follows X with a lag, roll Z
  forward by the expected lag-adjusted delta.
- **Don't confuse "forecast" with "truth."** Always show the estimator the
  raw current price *and* the projected price so they know how much of the
  rate is model output. Never hide the projection logic.

### Risks

- Commodity prediction is a humbling problem. Building our own model is
  likely not worth it — prefer off-the-shelf forward prices or
  expert-published indices (ENR, RSMeans).
- Over-tuning the cushion / projection math to past data risks the classic
  backtest trap: looks great on history, breaks on live data.
- If scraping and prediction are on the critical path of estimating, a
  broken scraper can silently poison estimates. Build a manual override and
  a "pricing table is stale / unhealthy" UI signal before turning automation
  on.

---

## What we are explicitly NOT building yet

- No scraping, no ML, no futures feeds during Phase 1 or Phase 2.
- No appliance-category pricing until we have either real job data (Phase 3)
  or a trustworthy data source for customer-allowance defaults (Phase 4).
  For now appliance `t1..t5` stay `null` in `pricing.json`.
- No separate mobile app. Responsive-friendly `index.html` covers the field
  use case for now.

---

## Dependencies / order of operations

```
  Phase 1 (done)  →  Phase 2  →  Phase 3
                                    ↓
                               Phase 4  →  Phase 5
```

- Phase 3 (TLP cost data) depends on Phase 2's effective-dated schema.
- Phase 4 (scraping) depends on Phase 2's storage + Phase 3's category split
  between TLP-cost and customer-allowance rows.
- Phase 5 (prediction) depends on Phase 4's time-series of observations.

Each phase should land as its own set of small atomic commits, with
round-trip or behavioral tests preventing regressions in the phases before
it. Same rules as Phase 1.
