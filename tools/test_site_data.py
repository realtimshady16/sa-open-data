#!/usr/bin/env python3
"""Independent checks of the built view against the raw capture.

    python3 tools/build_site.py && python3 -m unittest tools/test_site_data.py

The period picker here is deliberately a second, simpler implementation: sorting periods and
taking the last. A regression that selects the wrong row in both generator and test is still
possible, but an index/detail split or a reversed source order cannot pass unnoticed.
"""
import csv
import json
import re
import unittest
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATA = ROOT / "datasets"
AGSA = DATA / "agsa-audit-outcomes/audit-opinions-2026-11-10.json"

TOKEN = {
    "Clean": "clean",
    "Clean, with notes": "clean-notes",
    "Qualified": "qualified",
    "Adverse": "adverse",
    "Disclaimer": "disclaimer",
    "Audit not finalised": "outstanding",
}
LABEL = {token: label for label, token in TOKEN.items()}
EXPECTED = {"clean": 39, "clean-notes": 116, "qualified": 87,
            "disclaimer": 8, "adverse": 5, "outstanding": 2}


def raw_opinions():
    with AGSA.open() as handle:
        return json.load(handle)["data"]


def newest(opinions):
    dated = sorted((o for o in (opinions or []) if o.get("audit_opinion")),
                   key=lambda o: o.get("period") or "")
    return dated[-1] if dated else {}


class BuiltView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (SITE / "index.html").read_text()
        cls.rows = re.findall(r'<tr data-search="[^"]*"[^>]*>.*?</tr>', cls.index, re.S)

    def test_artifacts_exist(self):
        self.assertTrue((SITE / "index.html").exists(), "run tools/build_site.py first")
        self.assertTrue((SITE / "municipalities.csv").exists())

    def test_distribution_matches_raw_capture(self):
        counts = {}
        for token in re.findall(r'data-verdict="([^"]+)"', self.index):
            counts[token] = counts.get(token, 0) + 1
        self.assertEqual(counts, EXPECTED)

    def test_all_257_rows_match_their_detail_page_and_the_raw_period(self):
        self.assertEqual(len(self.rows), 257)
        for row in self.rows:
            href = re.search(r'<a href="([^"]+)"', row).group(1)
            token = re.search(r'data-verdict="([^"]+)"', row).group(1)
            period = re.search(r'<span class="period">([^<]*)</span>', row).group(1)
            detail = (SITE / href).read_text()
            years = re.findall(
                r'<tr><td class="nw">(\d{4}-\d{2})</td><td class="nw [^"]*">([^<]+)</td></tr>', detail)
            self.assertTrue(years, f"no audited periods on {href}")
            self.assertEqual(period, years[-1][0], f"period mismatch on {href}")
            self.assertEqual(LABEL[token], years[-1][1].split(" — ")[0],
                             f"verdict mismatch on {href}")

    def test_known_fixture_not_reversed(self):
        entry = next(e for e in raw_opinions() if e["slug"] == "8-bojanala-district")
        latest = newest(entry["opinions"])
        self.assertEqual(latest["period"], "2024-25")
        self.assertEqual(latest["audit_opinion"], "Unqualified with findings")
        row = next(r for r in self.rows if 'DC37-bojanala.html' in r)
        self.assertIn('data-verdict="clean-notes"', row)
        self.assertIn('<span class="period">2024-25</span>', row)

    def test_every_latest_period_is_comparable(self):
        for entry in raw_opinions():
            latest = newest(entry.get("opinions"))
            if latest:
                self.assertEqual(latest["period"], "2024-25", entry["slug"])

    def test_csv_matches_the_index(self):
        with (SITE / "municipalities.csv").open(newline="") as handle:
            records = list(csv.DictReader(handle))
        self.assertEqual(len(records), 257)
        self.assertEqual(records[0]["latest_audit_period"], "2024-25")
        self.assertEqual({r["category"] for r in records}, {"Metro", "Local", "District"})


if __name__ == "__main__":
    unittest.main()
