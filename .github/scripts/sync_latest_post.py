#!/usr/bin/env python3
"""
Syncs the "Latest post" card in index.html to whatever is actually the
newest post in the dcatlin9.github.io blog repo.

Runs on a schedule (see .github/workflows/sync-latest-post.yml) with no
credentials beyond the repo's own default GITHUB_TOKEN. Reads the blog
repo's _posts/ directory over the public GitHub API (no auth needed,
since that repo is public), finds the most recent post by its filename
date prefix, pulls title/date/summary out of its front matter, and
rewrites the card in index.html to match. Exits non-zero (failing the
Action run, which surfaces as a visible failure rather than silent
staleness) if the expected HTML markers or front matter fields aren't
found, so a manual template change gets noticed rather than ignored.
"""

import json
import re
import sys
import urllib.request
from datetime import datetime

BLOG_REPO = "dcatlin9/dcatlin9.github.io"
BLOG_SITE_URL = "https://dcatlin9.github.io"
INDEX_HTML_PATH = "index.html"

POST_FILENAME_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$")
FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)

CARD_BLOCK_RE = re.compile(
    r'(<!-- latest-post:start.*?-->\s*'
    r'<p class="rail-title">)(.*?)(</p>\s*'
    r'<p class="rail-date">)(.*?)(</p>\s*'
    r'<p class="rail-summary">)(.*?)(</p>.*?'
    r'<a class="btn btn-primary" href=")(.*?)("[^>]*>.*?</a>\s*'
    r'<!-- latest-post:end -->)',
    re.DOTALL,
)


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "sync-latest-post-script"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_text(url, accept=None):
    headers = {"User-Agent": "sync-latest-post-script"}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def html_escape(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def get_latest_post_filename():
    entries = fetch_json(f"https://api.github.com/repos/{BLOG_REPO}/contents/_posts")
    post_files = [e["name"] for e in entries if POST_FILENAME_RE.match(e["name"])]
    if not post_files:
        print("ERROR: no post files found in _posts/", file=sys.stderr)
        sys.exit(1)
    # Filenames are YYYY-MM-DD-slug.md, so a plain sort is a correct date sort.
    post_files.sort()
    return post_files[-1]


def parse_front_matter(raw_text):
    match = FRONT_MATTER_RE.match(raw_text)
    if not match:
        print("ERROR: could not find front matter block in latest post", file=sys.stderr)
        sys.exit(1)
    fm_text = match.group(1)
    fields = {}
    for line in fm_text.splitlines():
        m = re.match(r'^(\w+):\s*(.*)$', line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        fields[key] = value
    return fields


def build_permalink(filename):
    m = POST_FILENAME_RE.match(filename)
    year, month, day, slug = m.groups()
    return f"{BLOG_SITE_URL}/{year}/{month}/{day}/{slug}/"


def format_display_date(date_field):
    # date field looks like "2026-09-28 08:00:00 -0700"
    date_part = date_field.split()[0]
    dt = datetime.strptime(date_part, "%Y-%m-%d")
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


def main():
    latest_filename = get_latest_post_filename()
    # Fetched via the Contents API with the raw media type, not
    # raw.githubusercontent.com directly — that CDN layer caches content
    # for several minutes per path, which would make a 30-minute poll
    # occasionally read stale front matter right after a fresh push.
    contents_url = f"https://api.github.com/repos/{BLOG_REPO}/contents/_posts/{latest_filename}"
    post_text = fetch_text(contents_url, accept="application/vnd.github.v3.raw")
    fields = parse_front_matter(post_text)

    for required in ("title", "date", "summary"):
        if required not in fields:
            print(f"ERROR: latest post is missing '{required}' in front matter", file=sys.stderr)
            sys.exit(1)

    new_title = html_escape(fields["title"])
    new_date = format_display_date(fields["date"])
    new_summary = html_escape(fields["summary"])
    new_href = build_permalink(latest_filename)

    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    match = CARD_BLOCK_RE.search(html)
    if not match:
        print(
            "ERROR: could not find the latest-post card block in index.html "
            "(markers or structure may have changed) — update this script's "
            "CARD_BLOCK_RE to match before this can sync again",
            file=sys.stderr,
        )
        sys.exit(1)

    old_title, old_date, old_summary, old_href = (
        match.group(2), match.group(4), match.group(6), match.group(8)
    )

    if (old_title, old_date, old_summary, old_href) == (new_title, new_date, new_summary, new_href):
        print("Latest post card is already up to date. Nothing to do.")
        print("changed=false")
        return

    new_block = (
        match.group(1) + new_title +
        match.group(3) + new_date +
        match.group(5) + new_summary +
        match.group(7) + new_href +
        match.group(9)
    )
    new_html = html[:match.start()] + new_block + html[match.end():]

    with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"Updated latest-post card to: {fields['title']!r} ({new_href})")
    print("changed=true")


if __name__ == "__main__":
    main()
