# coastal-agentics.github.io

The public website for **Coastal Agentics**, a Savannah, Georgia company that trains robots on the Georgia coast, alongside the people and industries that will work with them.

Served by GitHub Pages at <https://coastal-agentics.github.io> from the root of the `main` branch.

## What's here

| File | Purpose |
| --- | --- |
| `index.html` | The whole site: hero, what we do, what we believe, Saltmarsh (research tool), projects (field experiments), work with us, footer |
| `style.css` | All styles. System fonts, no framework |
| `logo.svg` | The mark: a solid C and a triangular A that overlap, with a hairline wave knocked out of both |
| `logo-wordmark.svg` | The mark plus "Coastal Agentics" |
| `favicon.svg` | The mark without the wave, cropped for 16 to 32px browser tabs |
| `og-image.png` | 1200x630 social preview card |
| `404.html` | Not-found page. Self-contained (inline CSS and SVG) because Pages serves it at any missing path |
| `.nojekyll` | Tells Pages to serve the files as-is |
| `CARD.md` | Provenance card |

## Principles

- No build step, no framework, no trackers, no external requests except outbound links.
- Relative links throughout, so the site also works from a subpath or a local folder. The one exception is the home link on `404.html`, which points to `/`.
- Palette (tonal grey-blue, from the logo): C `#436A95`, A `#5F88B7`, overlap `#34557B`, background `#EEF2F6`, text `#1F3147`.
- Social meta tags (`og:*`, `twitter:*`) use absolute URLs, because crawlers require them.

## Local preview

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

## Editing

Edit `index.html` directly. Keep the copy faithful to the Coastal Agentics manifesto, and update `CARD.md` when the sources change.
