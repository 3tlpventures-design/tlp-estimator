"""Round-trip test: pipeline output must match the captured MASTER_PRICING oracle."""
import json
import re
from pathlib import Path

from scripts.build_pricing import main
from scripts.config import OUTPUT_PATH

ORACLE_PATH = Path(__file__).parent / "expected_pricing.json"
TIERS = ("t1", "t2", "t3", "t4", "t5")


def test_round_trip_matches_oracle():
    assert main() == 0
    generated = json.loads(OUTPUT_PATH.read_text())
    expected = json.loads(ORACLE_PATH.read_text())

    missing_cats = set(expected) - set(generated)
    extra_cats = set(generated) - set(expected)
    assert not missing_cats, f"Missing categories: {sorted(missing_cats)}"
    assert not extra_cats, f"Unexpected categories: {sorted(extra_cats)}"

    mismatches = []
    for cat_id, expected_entry in expected.items():
        for tier in TIERS:
            exp = expected_entry.get(tier)
            got = generated[cat_id].get(tier)
            if exp != got:
                mismatches.append(f"{cat_id}.{tier}: expected {exp!r} got {got!r}")
    assert not mismatches, "\n".join(mismatches[:20])


def test_no_raw_prices_in_stdout(capsys):
    """Coke-recipe guardrail — the build script must not echo raw prices."""
    main()
    captured = capsys.readouterr().out
    assert not re.search(r"\$\d", captured), "Build script leaked a $-price"
    assert not re.search(r"\b\d+\.\d{2}\b", captured), (
        "Build script leaked a decimal price-shaped number"
    )
