"""Paths and constants for the pricing build pipeline."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUT_PATH = REPO_ROOT / "pricing.json"

ALLOWANCE_XLSX = DATA_DIR / "Allowance_Pricing_Levels.xlsx"
BLANK_XLSM = DATA_DIR / "BLANK_Allowances_3_5_2024.xlsm"

TIERS = ("t1", "t2", "t3", "t4", "t5")

TAX_RATE = 1.0925
