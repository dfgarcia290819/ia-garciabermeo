"""Tests for the Lychee link-checker configuration."""

from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
CONFIG = tomllib.loads((ROOT / "lychee.toml").read_text(encoding="utf-8"))
EXCLUDES = [re.compile(pattern) for pattern in CONFIG["exclude"]]


def is_excluded(url: str) -> bool:
    return any(pattern.search(url) for pattern in EXCLUDES)


class LycheeConfigTests(unittest.TestCase):
    def test_excludes_bot_hostile_official_portals(self) -> None:
        urls = [
            "https://www.archivogeneral.gov.co/",
            "https://www.corteconstitucional.gov.co/relatoria/",
            "https://www.datos.gov.co/",
            "https://www.legalapp.gov.co/",
            "https://www.mintic.gov.co/",
            "https://www.secretariasenado.gov.co/",
            "https://www.secretariasenado.gov.co/senado/basedoc/ley_1581_2012.html",
            "https://www.sic.gov.co/",
            "https://www.suin-juriscol.gov.co/",
        ]

        self.assertTrue(all(is_excluded(url) for url in urls))

    def test_does_not_exclude_other_links(self) -> None:
        self.assertFalse(is_excluded("https://github.com/dfgarcia290819/ia-garciabermeo"))
        self.assertFalse(is_excluded("https://www.consejodeestado.gov.co/"))


if __name__ == "__main__":
    unittest.main()
