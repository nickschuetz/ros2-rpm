#!/usr/bin/env python3
"""scripts/check-upstream-issues.py

Reads docs/UPSTREAM-ISSUES.md, extracts every ros2/rviz (and other
project) issue / PR link from the "## Open" section, queries the GitHub
API for the current state, and reports any that have closed.

Intended to run nightly via .github/workflows/upstream-issues.yml. When
something we were waiting on closes, the workflow opens an issue in this
repo (or comments on an existing tracking issue) so we know to revisit
the corresponding deferral.

Usage:
  python3 scripts/check-upstream-issues.py            # human report
  python3 scripts/check-upstream-issues.py --json     # machine-readable

Exit code 0 always; the workflow reads the JSON output to decide whether
to post a notification.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TRACKING_FILE = Path(__file__).resolve().parent.parent / "docs" / "UPSTREAM-ISSUES.md"

# GitHub URL patterns we extract.  Both /issues/N and /pull/N go to
# /repos/<owner>/<repo>/issues/N on the API.
URL_RE = re.compile(
    r"https://github\.com/([\w.-]+)/([\w.-]+)/(?:issues|pull)/(\d+)"
)


def parse_open_section(text: str) -> list[tuple[str, str, str]]:
    """Return (owner, repo, number) tuples for every link in the Open section."""
    in_open = False
    in_closed = False
    found: set[tuple[str, str, str]] = set()
    for line in text.splitlines():
        if line.startswith("## Open"):
            in_open, in_closed = True, False
            continue
        if line.startswith("## Closed"):
            in_open, in_closed = False, True
            continue
        if line.startswith("## Maintenance"):
            in_open = in_closed = False
            continue
        if in_open:
            for m in URL_RE.finditer(line):
                found.add(m.groups())
    return sorted(found)


def fetch_issue_state(owner: str, repo: str, number: str, token: str | None) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
    req = Request(url, headers={"Accept": "application/vnd.github+json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except (HTTPError, URLError) as e:
        return {"_error": str(e)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true", help="Emit JSON")
    p.add_argument(
        "--token",
        default=None,
        help="GitHub token (otherwise reads $GITHUB_TOKEN env var)",
    )
    args = p.parse_args()

    import os

    token = args.token or os.environ.get("GITHUB_TOKEN")

    text = TRACKING_FILE.read_text()
    targets = parse_open_section(text)
    if not targets:
        print("No tracked upstream issues in docs/UPSTREAM-ISSUES.md")
        return 0

    results: list[dict] = []
    for owner, repo, number in targets:
        info = fetch_issue_state(owner, repo, number, token)
        if "_error" in info:
            results.append({
                "owner": owner,
                "repo": repo,
                "number": number,
                "url": f"https://github.com/{owner}/{repo}/issues/{number}",
                "state": "error",
                "error": info["_error"],
            })
            continue
        results.append({
            "owner": owner,
            "repo": repo,
            "number": number,
            "url": info.get("html_url", ""),
            "title": info.get("title", ""),
            "state": info.get("state", "unknown"),
            "is_pr": "pull_request" in info,
            "merged_at": (info.get("pull_request") or {}).get("merged_at"),
            "closed_at": info.get("closed_at"),
        })

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    # Human-readable report
    print(f"Tracking {len(results)} upstream issue(s) / PR(s):\n")
    for r in results:
        state = r.get("state", "?")
        marker = {
            "open": "[OPEN]",
            "closed": "[CLOSED]",
            "error": "[ERROR]",
        }.get(state, f"[{state}]")
        title = r.get("title", "?")
        kind = "PR" if r.get("is_pr") else "issue"
        line = f"  {marker:9}  {r['owner']}/{r['repo']} {kind} #{r['number']}: {title}"
        if state == "closed":
            line += f"\n              -> closed {r.get('closed_at')}"
            if r.get("merged_at"):
                line += f" (merged)"
        print(line)
    print()
    closed = [r for r in results if r.get("state") == "closed"]
    if closed:
        print(f"{len(closed)} item(s) have closed since last check; revisit the deferral they gated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
