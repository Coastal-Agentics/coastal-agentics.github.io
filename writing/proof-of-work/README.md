# Coastal Agentics: Proof of Work

A numbered series of test write-ups. The series landing page is `/writing/proof-of-work/`. Each entry is `/writing/proof-of-work/{number}-{slug}.html`, titled `Proof of Work #{number}: {title}`, listed newest first. There is a series RSS feed at `/writing/proof-of-work/feed.xml`, and the same items appear in `/writing/feed.xml`.

These pages are first staged on GitHub Pages (`coastal-agentics.github.io`). They are not copied to coastalagentics.com until that is approved.

## How to add the next entry

1. Copy `template.yml` to `entries/NNN.yml`, where NNN is the next number, zero-padded to three digits (`002.yml`, `003.yml`, …).
2. Fill every field. `number` is the public number in the title. `date` is the America/New_York date of the write-up. `mode` is `simulation` or `real`. `control` is one or more of `pretrained`, `scripted`, or `trained`.
3. Put only recorded results in `worked`, `failed`, the `lede`, and each section `body`. Copy figures from the week's results files. Do not invent speeds, counts, or causes. If a cause is not in the results, say so.
4. Add branded clips under `clips`, and cite their ids from the sections that need them. Label every clip as a simulation or as real, and say whether the motion is pretrained, scripted, or trained here.
5. From this directory, run:

   ```sh
   python3 render.py
   ```

   That rebuilds the post page, this series index, both RSS feeds, `/writing/index.html`, and the "Latest from Proof of Work" strip on the homepage (between the `pow-latest` markers in `/index.html`). The strip uses the entry's optional `still` field, or the poster of its first clip.
6. Preview locally (`python3 -m http.server` from the site root). Leave `draft: true` until the post is approved. Draft entries get a note on the post page and are left out of the public indexes and feeds. Do not open a pull request or copy files to the public site unless asked.

## Fields

The template lists them in full: `number`, `date`, `robot_or_system`, `mode` (sim or real), `control` (pretrained / scripted / trained), `worked`, `failed`, `next`, `clips`, plus `slug`, `title`, `author`, `lede`, `sections`, `sources`, and `draft`. The public byline is `Coastal Agentics`.
