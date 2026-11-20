# morebyt.com

Source for [morebyt.com](https://morebyt.com): plain HTML/CSS, no framework.

- `public/` is what Cloudflare Pages serves (no build step).
- `scripts/build_roadmap.py` generates `public/roadmap/index.html` and `pdf/print.html`.
- `pdf/print.html` is printed to the roadmap PDF with headless Chrome; the PDF itself is not committed.

```
python3 scripts/build_roadmap.py
```
