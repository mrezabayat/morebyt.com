# morebyt.com

Source for [morebyt.com](https://morebyt.com): plain HTML/CSS, no framework.

- `public/` is what Cloudflare Pages serves (no build step).
- `scripts/build_site.py` generates the home, consulting, blog and 404 pages; `public/assets/site.css` holds the shared design (light and dark).
- `scripts/build_roadmap.py` generates `public/roadmap/index.html` and `pdf/print.html`, using the header, footer and sign-up form from `build_site.py`.
- `scripts/build_blog.py` turns `content/blog/<slug>/index.md` (plus its images) into `public/blog/<slug>/`, the blog index and `public/feed.xml`.
- Diagrams are ```` ```mermaid ```` blocks in the posts (first line `%% alt: ...`). The blog build renders them to `diagram-<hash>.svg` with mermaid-cli and the local Chrome (`tools/mermaid.json`, `tools/puppeteer.json`); the SVGs are committed, so Node is only needed when a diagram changes.
- `pdf/print.html` is printed to the roadmap PDF with headless Chrome; the PDF itself is not committed.

```
python3 scripts/build_site.py && python3 scripts/build_roadmap.py
uv run --with markdown --with pygments python scripts/build_blog.py
```
