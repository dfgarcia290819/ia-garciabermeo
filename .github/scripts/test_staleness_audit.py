"""Tests for staleness_audit.py using only the Python standard library."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("staleness_audit.py")
SPEC = importlib.util.spec_from_file_location("staleness_audit", SCRIPT)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class ExtractRepositoriesTests(unittest.TestCase):
    def test_extracts_and_normalizes_repository_urls(self) -> None:
        text = """
        [Uno](https://github.com/Org/Repo)
        [Dos](https://github.com/org/repo.git)
        [Archivo](https://github.com/Owner/Project/blob/main/README.md)
        """

        self.assertEqual(
            AUDIT.extract_repositories(text),
            [("Org", "Repo"), ("Owner", "Project")],
        )

    def test_ignores_github_search_and_topic_urls(self) -> None:
        text = """
        https://github.com/topics/legaltech
        https://github.com/search?q=legaltech
        https://github.com/real-owner/real-repository
        """

        self.assertEqual(
            AUDIT.extract_repositories(text),
            [("real-owner", "real-repository")],
        )

    def test_ignores_duplicate_repository_urls_case_insensitively(self) -> None:
        text = """
        https://github.com/Owner/Repository
        https://github.com/owner/repository/issues
        """

        self.assertEqual(
            AUDIT.extract_repositories(text),
            [("Owner", "Repository")],
        )


if __name__ == "__main__":
    unittest.main()
