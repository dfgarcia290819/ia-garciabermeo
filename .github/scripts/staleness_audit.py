#!/usr/bin/env python3
"""Report archived or inactive GitHub repositories linked from README.md."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_URL = re.compile(
    r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)"
    r"(?:[/#?][^\s)\"']*)?",
    re.IGNORECASE,
)
NON_REPOSITORY_OWNERS = {"topics", "search", "marketplace", "settings", "sponsors", "orgs"}


def extract_repositories(text: str) -> list[tuple[str, str]]:
    repositories: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for match in REPO_URL.finditer(text):
        owner, name = match.group(1), re.sub(r"\.git$", "", match.group(2))
        if owner.lower() in NON_REPOSITORY_OWNERS:
            continue
        key = owner.lower(), name.lower()
        if key not in seen:
            seen.add(key)
            repositories.append((owner, name))
    return repositories


def fetch_repository(owner: str, name: str, token: str | None) -> dict:
    request = urllib.request.Request(f"https://api.github.com/repos/{owner}/{name}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", "legaltech-colombia-staleness-audit")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return {"error": f"HTTP {error.code}"}
    except urllib.error.URLError as error:
        return {"error": str(error.reason)}


def main() -> None:
    months = int(os.getenv("STALE_MONTHS", "18"))
    cutoff = datetime.now(timezone.utc) - timedelta(days=months * 30)
    repositories = extract_repositories(Path("README.md").read_text(encoding="utf-8"))
    findings: list[str] = []

    for owner, name in repositories:
        data = fetch_repository(owner, name, os.getenv("GITHUB_TOKEN"))
        slug = f"{owner}/{name}"
        if "error" in data:
            findings.append(f"- `{slug}` - no se pudo comprobar: {data['error']}")
        elif data.get("archived"):
            findings.append(f"- [{slug}]({data.get('html_url', '')}) - archivado")
        elif pushed_at := data.get("pushed_at"):
            pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            if pushed < cutoff:
                findings.append(f"- [{slug}]({data.get('html_url', '')}) - ultima actividad {pushed_at}")

    report = "# Auditoria de actividad\n\n" + (
        "\n".join(findings) if findings else "No se encontraron alertas."
    ) + "\n"
    Path("staleness-report.md").write_text(report, encoding="utf-8")
    if output := os.getenv("GITHUB_OUTPUT"):
        with Path(output).open("a", encoding="utf-8") as file:
            file.write(f"finding_count={len(findings)}\n")


if __name__ == "__main__":
    main()
