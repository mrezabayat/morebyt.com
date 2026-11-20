# morebyt.com

Source for [morebyt.com](https://morebyt.com): plain HTML/CSS, no framework.

- `public/` is what Cloudflare Pages serves (no build step).
- `content/site.json` holds what the home page and `/projects` show (current series, episodes, what's next, projects). `scripts/update_home_videos.py` refreshes the episode list from the YouTube playlist.
- `scripts/build_site.py` generates the home, consulting, blog and 404 pages; `public/assets/site.css` holds the shared design (light and dark).
- `scripts/build_roadmap.py` generates `public/roadmap/index.html` and `pdf/print.html`, using the header, footer and sign-up form from `build_site.py`.
- `scripts/build_blog.py` turns `content/blog/<slug>/index.md` (plus its images) into `public/blog/<slug>/`, the blog index and `public/feed.xml`.
- Each post folder can hold a `cover.svg` (line art, inlined so it follows light/dark mode) or set `cover:` / `cover_alt:` in the front matter to use its own image. The build also renders a 1200x630 `og-<hash>.png` for link previews with the local Chrome.
- Diagrams are ```` ```d2 ```` blocks in the posts (first line `# alt: ...`). The blog build renders each one twice with the D2 CLI (`brew install d2`), using `tools/d2-light.d2` and `tools/d2-dark.d2`, into `diagram-<hash>-light.svg` / `-dark.svg`; a `<picture>` element picks the right one. The SVGs are committed, so D2 is only needed when a diagram changes.
- Line drawings: `!drawing[alt text](file.svg)` inlines an SVG so it follows light/dark mode (use `stroke="currentColor"`, class `acc` for amber, `t`/`m` for text).
- `pdf/print.html` is printed to the roadmap PDF with headless Chrome; the PDF itself is not committed.

```
python3 scripts/build_site.py && python3 scripts/build_roadmap.py
uv run --with markdown --with pygments python scripts/build_blog.py
```
