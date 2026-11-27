#!/usr/bin/env python3
"""Render Proof of Work entries to static HTML and RSS.

Usage, from this directory:

    python3 render.py

Reads entries/*.yml (except the template), writes one HTML page per entry,
the series landing page, the series feed, writing/index.html, writing/feed.xml,
and the 'Latest from Proof of Work' strip on the homepage (between the pow-latest markers).
Newest entries are listed first. Draft entries are rendered with a note, but
they are left out of the public indexes and RSS feeds until `draft` is false.
"""
from __future__ import annotations

from datetime import date, datetime, timezone, timedelta
from email.utils import format_datetime
from pathlib import Path
import html
import re
import sys

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # site root
ENTRIES = HERE / "entries"
ET = timezone(timedelta(hours=-5), name="EST")

MONTHS = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def load_entries() -> list[dict]:
    items = []
    for path in sorted(ENTRIES.glob("*.yml")):
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict) or not data.get("number"):
            raise SystemExit(f"Entry {path.name} needs a positive number.")
        data["_path"] = path
        data["_date"] = date.fromisoformat(str(data["date"]))
        data["_filename"] = f"{data['number']}-{data['slug']}.html"
        items.append(data)
    items.sort(key=lambda e: (e["number"], e["_date"]), reverse=True)
    return items


def display_date(d: date) -> str:
    return f"{d.day} {MONTHS[d.month]} {d.year}"


def rss_date(d: date) -> str:
    return format_datetime(datetime(d.year, d.month, d.day, 18, 0, tzinfo=ET))


def e(text: object) -> str:
    return html.escape(str(text), quote=True)


def paras(text: str) -> str:
    blocks = [p.strip() for p in re.split(r"\n\s*\n", text or "") if p.strip()]
    return "\n".join(f"      <p>{e(p).replace(chr(10), ' ')}</p>" for p in blocks)


def film(clip: dict) -> str:
    src = clip["src"]
    label = clip["label"]
    title = clip["title"]
    credit = clip.get("credit") or ""
    return f'''      <figure class="film">
        <div class="film-frame">
          <video
            data-coastal-video
            muted
            playsinline
            preload="none"
            poster="{e(src)}.jpg"
            controls
            aria-label="{e(label)}">
            <source src="{e(src)}.webm" type="video/webm">
            <source src="{e(src)}.mp4" type="video/mp4">
            {e(label)}
          </video>
          <p class="film-badge" aria-hidden="true">Simulation</p>
          <button class="video-toggle" type="button"><span data-label>Play</span></button>
        </div>
        <h2>{e(title)}</h2>
        <p class="credit">{e(credit)}</p>
      </figure>'''


def header(prefix: str, current: str) -> str:
    def link(name: str, path: str) -> str:
        # Writing pages sit under Proof of Work in the nav.
        cur = ' aria-current="page"' if current == name or (current == "Writing" and name == "Proof of Work") else ""
        return f'<a href="{path}"{cur}>{name}</a>'

    return f'''  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header wrap">
    <a class="brand" href="{prefix}" aria-label="Coastal Agentics home">
      <img src="{prefix}logo.svg" alt="" aria-hidden="true" width="64" height="64">
      <span class="brand-name">Coastal Agentics</span>
    </a>
    <nav aria-label="Primary">
      {link("Work", prefix + "#work")}
      {link("Proof of Work", prefix + "writing/proof-of-work/")}
      {link("Videos", prefix + "videos/")}
      <a href="https://coastal-agentics.github.io/arena/tbd/">Play the sim</a>
      <a class="nav-cta" href="{prefix}#work-with-us">Contact</a>
    </nav>
  </header>'''


def footer(prefix: str) -> str:
    return f'''  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div class="footer-brand">
        <img src="{prefix}logo.svg" alt="" aria-hidden="true" width="40" height="40">
        <div>
          <a class="footer-name" href="{prefix}">Coastal Agentics</a>
          <p>Behavioral design for agents</p>
        </div>
      </div>
      <div class="footer-meta">
        <p>Savannah, Georgia</p>
        <p>Founded October 1, 2026</p>
        <p><a href="https://github.com/Coastal-Agentics">GitHub</a></p>
      </div>
    </div>
  </footer>'''


def head(title: str, desc: str, canonical: str, css: str, extra: str = "") -> str:
    depth = 0 if not css.startswith("..") else css.count("..")
    fav = "../" * depth + "favicon.svg" if depth else "favicon.svg"
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="icon" href="{fav}" type="image/svg+xml">
  <meta name="theme-color" content="#FFFFFF">
  <meta name="color-scheme" content="light">
  <link rel="canonical" href="{e(canonical)}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Coastal Agentics">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{e(canonical)}">
  <meta property="og:image" content="https://coastal-agentics.github.io/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(title)}">
  <meta name="twitter:description" content="{e(desc)}">
  <link rel="stylesheet" href="{css}">
  {extra}
</head>'''


def post_url(entry: dict) -> str:
    return f"https://coastal-agentics.github.io/writing/proof-of-work/{entry['_filename']}"


def series_title(entry: dict) -> str:
    return f"Proof of Work #{entry['number']}: {entry['title']}"


def clip_map(entry: dict) -> dict[str, dict]:
    return {c["id"]: c for c in entry.get("clips") or []}


def render_post(entry: dict) -> str:
    prefix = "../../"
    title = series_title(entry)
    desc = " ".join((entry.get("lede") or "").split())
    clips = clip_map(entry)
    hero = next((c for c in entry.get("clips") or [] if c.get("hero")), None)
    control = ", ".join(entry.get("control") or [])
    mode = entry["mode"].capitalize() if entry.get("mode") else "Simulation"
    extra = (
        '<link rel="alternate" type="application/rss+xml" title="Coastal Agentics: Proof of Work" href="feed.xml">\n'
        '  <script src="../../home.js" defer></script>'
    )
    parts = [
        head(title, desc, post_url(entry), "../../style.css", extra),
        "<body>",
        header(prefix, "Writing"),
        '  <main id="main" class="wrap">',
        '    <article class="article">',
        '      <a class="back-link" href="./">← Proof of Work</a>',
    ]
    if entry.get("draft"):
        parts.append('      <p class="draft-note">Preview draft. Not published.</p>')
    parts += [
        f'      <p class="post-meta">Proof of Work #{entry["number"]} · {display_date(entry["_date"])} · {e(entry.get("author") or "Coastal Agentics")} · {e(mode)} · {e(control)}</p>',
        f"      <h1>{e(title)}</h1>",
        f'      <p class="lede">{e(" ".join((entry.get("lede") or "").split()))}</p>',
        '      <div class="facts">',
        "        <div>",
        "          <h2>What worked</h2>",
        f"          <p>{e(' '.join((entry.get('worked') or '').split()))}</p>",
        "        </div>",
        "        <div>",
        "          <h2>What failed</h2>",
        f"          <p>{e(' '.join((entry.get('failed') or '').split()))}</p>",
        "        </div>",
        "        <div>",
        "          <h2>Next step</h2>",
        f"          <p>{e(' '.join((entry.get('next') or '').split()))}</p>",
        "        </div>",
        "      </div>",
    ]
    if hero:
        parts.append(film(hero))
    for section in entry.get("sections") or []:
        parts.append(f'      <h2>{e(section["heading"])}</h2>')
        parts.append(paras(section.get("body") or ""))
        for cid in section.get("clips") or []:
            if cid not in clips:
                raise SystemExit(f"Entry {entry['number']} section {section['heading']!r} cites unknown clip {cid!r}.")
            parts.append(film(clips[cid]))
    if entry.get("sources"):
        parts.append('      <div class="sources">')
        parts.append("        <p>Numbers on this page were copied from the test results, not rounded beyond the figures stated.</p>")
        for src in entry["sources"]:
            label = src.get("label") or src.get("note") or src.get("path") or ""
            parts.append(f'        <p>{e(label)}</p>')
        parts.append("      </div>")
    parts += [
        "    </article>",
        "  </main>",
        footer(prefix),
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(parts)


def teaser(entry: dict) -> str:
    text = " ".join((entry.get("lede") or entry.get("worked") or "").split())
    if not text:
        return entry["title"]
    # first sentence
    parts = re.split(r"(?<=\.)\s+", text, maxsplit=1)
    return parts[0]


def render_series_index(entries: list[dict]) -> str:  # noqa: F811
    prefix = "../../"
    desc = "A running record of tests from Coastal Agentics: what we tried, what held, and what failed."
    extra = '<link rel="alternate" type="application/rss+xml" title="Coastal Agentics: Proof of Work" href="feed.xml">'
    items = []
    for entry in entries:
        items.append(
            f'''        <li>
          <time datetime="{entry['_date'].isoformat()}">Proof of Work #{entry['number']} · {display_date(entry['_date'])}</time>
          <h2><a href="{e(entry['_filename'])}">{e(entry['title'])}</a></h2>
          <p>{e(teaser(entry))}</p>
        </li>'''
        )
    intro = (
        "Coastal Agentics: Proof of Work is a running record of what we tried, what held, "
        "and what failed, as we train behavior and bring up new systems. Each entry is numbered. "
        "Every clip is a simulation until we say otherwise, and we say whether the motion was "
        "pretrained, scripted, or trained here. The work stays in our files, with a date and a name on it."
    )
    return f'''{head("Coastal Agentics: Proof of Work", desc, "https://coastal-agentics.github.io/writing/proof-of-work/", "../../style.css", extra)}
<body>
{header(prefix, "Writing")}
  <main id="main">
    <section class="page-hero wrap">
      <p class="section-kicker">A series</p>
      <h1 class="wide">Proof of Work</h1>
      <p class="page-lede">{e(intro)}</p>
    </section>
    <section class="section section-tight wrap">
      <ol class="post-list">
{chr(10).join(items)}
      </ol>
    </section>
  </main>
{footer(prefix)}
</body>
</html>
'''


def render_writing_index(entries: list[dict]) -> str:
    prefix = "../"
    desc = "Notes from Coastal Agentics in Savannah, Georgia, including the Proof of Work series."
    extra = (
        '<link rel="alternate" type="application/rss+xml" title="Coastal Agentics Writing" href="feed.xml">\n'
        '  <link rel="alternate" type="application/rss+xml" title="Coastal Agentics: Proof of Work" href="proof-of-work/feed.xml">'
    )
    latest = entries[0] if entries else None
    items = []
    for entry in entries:
        items.append(
            f'''        <li>
          <time datetime="{entry['_date'].isoformat()}">Proof of Work #{entry['number']} · {display_date(entry['_date'])}</time>
          <h2><a href="proof-of-work/{e(entry['_filename'])}">{e(entry['title'])}</a></h2>
          <p>{e(teaser(entry))}</p>
        </li>'''
        )
    card = ""
    if latest:
        card = f'''    <section class="wrap">
      <div class="series-card">
        <p class="section-kicker">A series</p>
        <h2><a href="proof-of-work/">Coastal Agentics: Proof of Work</a></h2>
        <p>A running record of what we tried, what held, and what failed, as we train behavior and bring up new systems. Latest: Proof of Work #{latest['number']}.</p>
        <a class="text-link" href="proof-of-work/">Read the series <span aria-hidden="true">→</span></a>
      </div>
    </section>
'''
    return f'''{head("Writing · Coastal Agentics", desc, "https://coastal-agentics.github.io/writing/", "../style.css", extra)}
<body>
{header(prefix, "Writing")}
  <main id="main">
    <section class="page-hero wrap">
      <p class="section-kicker">Writing</p>
      <h1>Notes from the coast.</h1>
      <p class="page-lede">Short posts on the work, written in plain language. The first series is Proof of Work, a numbered record of tests.</p>
    </section>
{card}    <section class="section section-tight wrap">
      <ol class="post-list">
{chr(10).join(items)}
      </ol>
    </section>
  </main>
{footer(prefix)}
</body>
</html>
'''


def rss(channel_title: str, channel_link: str, channel_desc: str, entries: list[dict], item_link) -> str:
    items = []
    for entry in entries:
        link = item_link(entry)
        items.append(
            f'''    <item>
      <title>{e(series_title(entry))}</title>
      <link>{e(link)}</link>
      <guid>{e(link)}</guid>
      <pubDate>{rss_date(entry["_date"])}</pubDate>
      <author>{e(entry.get("author") or "Coastal Agentics")}</author>
      <description>{e(" ".join((entry.get("lede") or "").split()))}</description>
    </item>'''
        )
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{e(channel_title)}</title>
    <link>{e(channel_link)}</link>
    <description>{e(channel_desc)}</description>
    <language>en-us</language>
{chr(10).join(items)}
  </channel>
</rss>
'''


HOME_START = "<!-- pow-latest:start (generated by writing/proof-of-work/render.py; edit the entry YAML, not this block) -->"
HOME_END = "<!-- pow-latest:end -->"


def entry_still(entry: dict) -> str:
    """Site-root path of the homepage strip still.

    Uses `still` from the entry if set (a path from this folder, like clip
    `src`), otherwise the poster of the entry's first clip. The image is
    decorative there: the title link beside it carries the meaning.
    """
    clips = entry.get("clips") or []
    still = entry.get("still") or (clips[0]["src"] + ".jpg" if clips else "../../og-image.png")
    return still.replace("../../", "")


def render_home_strip(latest: dict) -> str:
    still = entry_still(latest)
    return f'''{HOME_START}
    <section class="pow-latest wrap" aria-labelledby="pow-latest-title">
      <a class="pow-still" href="writing/proof-of-work/{e(latest['_filename'])}" tabindex="-1" aria-hidden="true">
        <img src="{e(still)}" alt="" width="640" height="360" loading="lazy" decoding="async">
      </a>
      <div class="pow-copy">
        <p class="section-kicker">Latest from Proof of Work</p>
        <p class="post-meta"><time datetime="{latest['_date'].isoformat()}">Proof of Work #{latest['number']} · {display_date(latest['_date'])}</time></p>
        <h2 id="pow-latest-title"><a href="writing/proof-of-work/{e(latest['_filename'])}">{e(latest['title'])}</a></h2>
        <p>{e(teaser(latest))}</p>
        <div class="pow-actions">
          <a class="btn" href="writing/proof-of-work/{e(latest['_filename'])}">Read #{latest['number']}</a>
          <a class="text-link" href="writing/proof-of-work/">All entries</a>
          <a class="text-link" href="writing/proof-of-work/feed.xml">RSS</a>
        </div>
      </div>
    </section>
    {HOME_END}'''


def update_home(latest: dict) -> bool:
    home = ROOT / "index.html"
    text = home.read_text()
    start = text.find(HOME_START)
    end = text.find(HOME_END)
    if start < 0 or end < 0:
        print("index.html has no pow-latest markers; homepage strip not updated", file=sys.stderr)
        return False
    new = text[:start] + render_home_strip(latest) + text[end + len(HOME_END):]
    if new != text:
        home.write_text(new)
    return True


def main() -> int:
    entries = load_entries()
    if not entries:
        print("No entries found in entries/*.yml", file=sys.stderr)
        return 1
    # Remove previously rendered post pages in this folder (keep index, feed, readme, template, render)
    for path in HERE.glob("*.html"):
        if path.name != "index.html":
            # only delete numbered post pages
            if re.match(r"^\d+-.+\.html$", path.name):
                path.unlink()
    for entry in entries:
        dest = HERE / entry["_filename"]
        dest.write_text(render_post(entry))
        print("wrote", dest.relative_to(ROOT))
    published = [en for en in entries if not en.get("draft")]
    (HERE / "index.html").write_text(render_series_index(published))
    print("wrote", (HERE / "index.html").relative_to(ROOT))
    (HERE / "feed.xml").write_text(
        rss(
            "Coastal Agentics: Proof of Work",
            "https://coastal-agentics.github.io/writing/proof-of-work/",
            "A numbered record of tests: what we tried, what held, and what failed.",
            published,
            post_url,
        )
    )
    print("wrote", (HERE / "feed.xml").relative_to(ROOT))
    writing = ROOT / "writing"
    (writing / "index.html").write_text(render_writing_index(published))
    print("wrote", (writing / "index.html").relative_to(ROOT))
    (writing / "feed.xml").write_text(
        rss(
            "Coastal Agentics Writing",
            "https://coastal-agentics.github.io/writing/",
            "Notes from Coastal Agentics in Savannah, Georgia.",
            published,
            lambda en: f"https://coastal-agentics.github.io/writing/proof-of-work/{en['_filename']}",
        )
    )
    print("wrote", (writing / "feed.xml").relative_to(ROOT))
    if published and update_home(published[0]):
        print("wrote", (ROOT / "index.html").relative_to(ROOT), "(Latest from Proof of Work strip)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
