# coastal-agentics.github.io

The public website for **Coastal Agentics**, a Savannah, Georgia company that teaches and demonstrates decentralized agent systems on edge devices.

Served by GitHub Pages at <https://coastal-agentics.github.io> from the root of the `main` branch.

## What's here

| File | Purpose |
| --- | --- |
| `index.html` | The whole site: hero, what we do and believe, Saltmarsh, projects, footer |
| `style.css` | All styles. System fonts, no framework |
| `logo.svg` | The mark: a C wrapped around an A whose crossbar is a wave |
| `logo-wordmark.svg` | The mark plus "Coastal Agentics" |
| `favicon.svg` | The mark on a sand tile, for browser tabs |
| `404.html` | Not-found page. Self-contained (inline CSS and SVG) because Pages serves it at any missing path |
| `.nojekyll` | Tells Pages to serve the files as-is |
| `CARD.md` | Provenance card |

## Principles

- No build step, no framework, no trackers, no external requests except outbound links.
- Relative links throughout, so the site also works from a subpath or a local folder. The one exception is the home link on `404.html`, which points to `/`.
- Palette: deep marsh green `#1E3D36`, sand `#F5F0E6`, one ochre accent `#C8793A`.

## Local preview

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

## Editing

Edit `index.html` directly. Keep the copy faithful to the Coastal Agentics manifesto, and update `CARD.md` when the sources change.
