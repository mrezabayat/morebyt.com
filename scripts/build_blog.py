#!/usr/bin/env python3
"""Builds the blog: content/blog/<slug>/index.md -> public/blog/<slug>/index.html, plus /blog/ and /feed.xml.

    uv run --with markdown --with pygments python scripts/build_blog.py

Each post folder holds index.md and its images. Front matter (between --- lines):

    title: How a CPU actually works
    description: One sentence for search results and link previews.
    date: 2025-01-17
    updated: 2026-11-21          (optional; only for real content changes)
    tags: C++, design patterns   (comma separated)
    video: gvcfUgpRvsk           (optional YouTube id, embedded at the top)
    cover: photo.jpg             (optional; otherwise cover.svg in the folder is inlined)

Diagrams: ```d2 fenced blocks (first line '# alt: ...'), rendered with the D2 CLI.
Drawings: !drawing[alt text](file.svg) inlines a line-art SVG that follows light/dark mode.
"""
import re
import shutil
import sys
from datetime import date
from html import escape
from pathlib import Path

import markdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site as site  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "content" / "blog"
OUT = ROOT / "public" / "blog"
BASE = "https://morebyt.com"


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path}: missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            meta[k.strip()] = v
    for key in ("title", "description", "date"):
        if key not in meta:
            raise SystemExit(f"{path}: front matter needs '{key}'")
    meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    meta["date"] = date.fromisoformat(meta["date"])
    if meta.get("updated"):
        meta["updated"] = date.fromisoformat(meta["updated"])
    return meta, m.group(2)


def nice(d):
    return f"{d.day} {d.strftime('%B %Y')}"


# ------------------------------------------------------------------ D2 diagrams and inline drawings
# ```d2 blocks are rendered to SVG at build time with the D2 CLI (no JavaScript on the page),
# once with the light site colours and once with the dark ones; <picture> picks the right file.
# The first line of a block must be "# alt: <text>" for the image's alt text.
# SVGs are cached in the post folder as diagram-<hash>-light.svg / -dark.svg and committed,
# so the site builds without D2 when no diagram changed.
TOOLS = ROOT / "tools"
D2_FLAGS = ["--layout", "elk", "--pad", "20"]
D2_RE = re.compile(r"^```d2[ \t]*\n(.*?)\n```[ \t]*$", re.S | re.M)
DRAWING_RE = re.compile(r"^!drawing\[([^\]]+)\]\(([\w.-]+\.svg)\)[ \t]*$", re.M)


def _d2_version():
    import subprocess
    try:
        return subprocess.run(["d2", "--version"], capture_output=True, text=True, check=True).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _diagram_hash(src):
    import hashlib
    h = hashlib.sha256(" ".join(D2_FLAGS).encode() + src.encode())
    for f in ("d2-light.d2", "d2-dark.d2"):
        h.update((TOOLS / f).read_bytes())
    return h.hexdigest()[:12]


def _render_d2(src, out, theme_file, version):
    import subprocess
    import tempfile
    if not version:
        raise SystemExit(f"{out.name} needs rendering but the d2 command is not installed (brew install d2)")
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "d.d2"
        f.write_text((TOOLS / theme_file).read_text(encoding="utf-8") + "\n" + src + "\n", encoding="utf-8")
        r = subprocess.run(["d2", *D2_FLAGS, str(f), str(out)], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"D2 render failed for {out.name}:\n{r.stderr}")


def _fix_svg_size(path):
    """D2 writes no width/height on the root <svg>; add them so <img> has a real intrinsic size."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r'(<\?xml[^>]*\?>)?(<svg\b[^>]*?)(>)', text)
    if m and " width=" not in m.group(2):
        vb = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)"', m.group(2))
        if vb:
            w, h = round(float(vb.group(1))), round(float(vb.group(2)))
            text = text[:m.end(2)] + f' width="{w}" height="{h}"' + text[m.end(2):]
            path.write_text(text, encoding="utf-8")


def _svg_size(path):
    m = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)"', path.read_text(encoding="utf-8")[:2000])
    return (round(float(m.group(1))), round(float(m.group(2)))) if m else (None, None)


def diagrams(slug, body):
    folder = SRC / slug
    used = set()
    version = None

    def repl(m):
        nonlocal version
        src = m.group(1).strip()
        alt_m = re.match(r"#\s*alt:\s*(.+)", src.splitlines()[0])
        if not alt_m:
            raise SystemExit(f"{slug}: every d2 block needs a first line '# alt: ...'")
        key = _diagram_hash(src)
        light, dark = folder / f"diagram-{key}-light.svg", folder / f"diagram-{key}-dark.svg"
        used.update({light.name, dark.name})
        for out, theme in ((light, "d2-light.d2"), (dark, "d2-dark.d2")):
            if not out.exists():
                version = version or _d2_version()
                print("rendering", slug, out.name)
                _render_d2(src, out, theme, version)
        _fix_svg_size(light)
        _fix_svg_size(dark)
        w, h = _svg_size(light)
        size = f' width="{w}" height="{h}"' if w else ""
        return (f'\n<figure class="diagram"><a href="{light.name}" title="Open the full-size diagram">'
                f'<picture><source data-dark srcset="{dark.name}" media="(prefers-color-scheme: dark)">'
                f'<img src="{light.name}" alt="{escape(alt_m.group(1).strip())}"{size}></picture></a>'
                f'<figcaption>Tap the diagram to open it full size.</figcaption></figure>\n')

    body = D2_RE.sub(repl, body)
    for old in list(folder.glob("diagram-*.svg")):
        if old.name not in used:
            old.unlink()
    return body


def drawings(slug, body):
    """!drawing[alt text](file.svg) inlines a line drawing so it follows the site colours."""
    def repl(m):
        f = SRC / slug / m.group(2)
        if not f.exists():
            raise SystemExit(f"{slug}: drawing {m.group(2)} not found")
        svg = f.read_text(encoding="utf-8").strip()
        svg = svg.replace("<svg ", f'<svg role="img" aria-label="{escape(m.group(1))}" ', 1)
        return f'\n<figure class="drawing">{svg}</figure>\n'
    return DRAWING_RE.sub(repl, body)


def render_md(body):
    md = markdown.Markdown(
        extensions=["fenced_code", "codehilite", "tables", "toc", "attr_list", "sane_lists", "footnotes"],
        extension_configs={"codehilite": {"guess_lang": False, "css_class": "hl"},
                           "toc": {"permalink": False, "toc_depth": "2-3"}})
    html = md.convert(body)
    # lazy-load images that are not first
    html = re.sub(r"<img (?![^>]*loading=)", '<img loading="lazy" ', html)
    return html, md.toc_tokens


def minutes(body):
    words = len(re.findall(r"\w+", re.sub(r"```.*?```", "", body, flags=re.S)))
    return max(1, round(words / 230))


POST_CSS = """
<style>
.post header{margin-bottom:var(--s5)}
.post h1{font-size:clamp(30px,5vw,46px);margin-bottom:var(--s3)}
.prose{font-size:19px;line-height:1.7}
.prose h2{font-size:clamp(23px,3vw,28px);margin:var(--s6) 0 var(--s3)}
.prose h3{font-size:20px;margin:var(--s5) 0 var(--s2)}
.prose p,.prose ul,.prose ol,.prose table,.prose blockquote,.prose pre{margin:0 0 var(--s4)}
.prose li{margin-bottom:6px}
.prose img{display:block;margin:var(--s4) auto;max-height:560px;background:#fff;border:1px solid var(--rule);padding:8px}
.prose figure.diagram{margin:var(--s4) 0}
.prose figure.diagram picture{display:block}
.prose figure.diagram img{max-height:none;height:auto;padding:12px;background:var(--sheet);border-color:var(--rule-2)}
.prose figure.drawing{margin:var(--s4) 0;padding:var(--s3);background:var(--sheet);border:1px solid var(--rule-2);color:var(--line)}
.prose figure.drawing svg{display:block;width:100%;height:auto}
.prose figure.drawing .acc{fill:var(--amber)}
.prose figure.drawing path.acc{stroke:var(--amber)}
.prose figure.drawing .t{fill:var(--ink);stroke:none;font-family:var(--mono)}
.prose figure.drawing .m{fill:var(--ink-2);stroke:none;font-family:var(--mono)}
.prose figure.diagram a{display:block}
.prose figure.diagram figcaption{font:13px var(--mono);color:var(--ink-2);margin-top:6px}
@media (min-width:641px){.prose figure.diagram figcaption{display:none}}
.prose blockquote{border-left:3px solid var(--amber);padding:2px 0 2px var(--s3);color:var(--ink-2)}
.prose table{border-collapse:collapse;width:100%;font-size:16px;display:block;overflow-x:auto}
.prose th,.prose td{border-bottom:1px solid var(--rule);padding:8px 12px 8px 0;text-align:left;vertical-align:top}
.prose th{font:600 14px var(--mono);color:var(--ink-2);border-bottom-color:var(--rule-2)}
.prose :not(pre)>code{font-size:.84em;background:var(--sheet);border:1px solid var(--rule);border-radius:3px;padding:.05em .3em;overflow-wrap:anywhere}
.prose pre{font:15px/1.55 var(--mono);background:var(--sheet);border:1px solid var(--rule-2);padding:var(--s3);overflow-x:auto;tab-size:4}
.prose hr{border:0;border-top:1px solid var(--rule);margin:var(--s5) 0}
.video{position:relative;aspect-ratio:16/9;margin:0 0 var(--s5);border:1px solid var(--rule-2)}
.video iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.after{margin-top:var(--s6)}
/* code colours: variables in site.css follow the theme */
.hl .k,.hl .kd,.hl .kt,.hl .kr,.hl .kn,.hl .cp{color:var(--hl-kw)}
.hl .s,.hl .s1,.hl .s2,.hl .sc,.hl .cpf{color:var(--hl-str)}
.hl .c,.hl .c1,.hl .cm{color:var(--hl-com);font-style:italic}
.hl .m,.hl .mi,.hl .mf,.hl .mh{color:var(--hl-num)}
.hl .nf,.hl .nc{color:var(--hl-fn)}
</style>"""

LAYOUT_CSS = """
<style>
.post-wrap{padding-top:var(--s6);padding-bottom:var(--s5)}
@media (max-width:1099px){.post{margin:0 auto}}
.post-grid{display:block}
.post{max-width:780px;min-width:0}
.cover{margin:0 0 var(--s4);background:var(--sheet);border:1px solid var(--rule-2);aspect-ratio:16/9;color:var(--line);position:relative}
.cover svg,.cover img{display:block;width:100%;height:100%;object-fit:cover}
.cover .acc,.thumb .acc{fill:var(--amber)}
.cover::before,.cover::after{content:"";position:absolute;width:12px;height:12px;border:2px solid var(--line)}
.cover::before{top:-1px;left:-1px;border-right:0;border-bottom:0}
.cover::after{bottom:-1px;right:-1px;border-left:0;border-top:0}
.post header{margin-bottom:var(--s5)}
.meta{display:flex;flex-wrap:wrap;gap:4px 18px;font:14px/1.6 var(--mono);color:var(--ink-2);margin:0}
.prose h2{scroll-margin-top:24px}
.toc-side{display:none}
.toc-top{margin:0 0 var(--s5);border:1px solid var(--rule-2);background:var(--sheet)}
.toc-top summary{cursor:pointer;padding:12px 16px;font:600 15px var(--mono);list-style-position:inside}
.toc-top nav{padding:0 16px 12px}
.toc ol{list-style:none;margin:0;padding:0}
.toc li{margin:0}
.toc a{display:block;padding:6px 0 6px 12px;border-left:2px solid var(--rule);color:var(--ink-2);text-decoration:none;font:14px/1.4 var(--mono)}
.toc a:hover{color:var(--ink)}
.toc a[aria-current="true"]{color:var(--ink);border-left-color:var(--line)}
.toc-title{font:600 14px var(--mono);color:var(--ink);margin:0 0 10px}
@media (min-width:1100px){
  .post-grid{display:grid;grid-template-columns:minmax(0,780px) 240px;gap:56px;justify-content:space-between}
  .toc-side{display:block;position:sticky;top:24px;align-self:start;max-height:calc(100vh - 48px);overflow:auto;padding-top:4px}
  .toc-top{display:none}
}
</style>"""

LIST_CSS = """
<style>
.page{padding:var(--s6) 0 var(--s5)}
.page h1{margin-bottom:var(--s4)}
.page .lede{margin-bottom:0}
.posts{list-style:none;margin:var(--s5) 0 0;padding:0}
.posts li{display:grid;grid-template-columns:300px minmax(0,1fr);gap:var(--s4) var(--s5);align-items:center;padding:var(--s4) 0;border-top:1px solid var(--rule)}
.posts li:last-child{border-bottom:1px solid var(--rule)}
.thumb{display:block;background:var(--sheet);border:1px solid var(--rule-2);aspect-ratio:16/9;color:var(--line)}
.thumb svg,.thumb img{display:block;width:100%;height:100%;object-fit:cover}
.posts li:hover .thumb{border-color:var(--line)}
.posts h2{font-size:clamp(20px,2.2vw,24px);margin:0 0 8px}
.posts h2 a{color:var(--ink);text-decoration:none}
.posts h2 a:hover{text-decoration:underline;text-underline-offset:4px}
.posts p{margin:0 0 8px;color:var(--ink-2);max-width:68ch}
.posts .meta{font:14px var(--mono);color:var(--ink-2);display:flex;flex-wrap:wrap;gap:4px 18px}
.join{margin-top:var(--s6);max-width:760px}
@media (max-width:760px){.posts li{grid-template-columns:1fr;gap:var(--s3)}}
</style>"""

DEFAULT_COVER = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 270" fill="none" stroke="currentColor" stroke-width="1.6">'
                 '<rect x="120" y="60" width="240" height="150" rx="4"/><path d="M120 180h240M260 180v30M150 92h120M150 112h170M150 132h90" stroke-width="1.2"/>'
                 '<rect class="acc" x="280" y="188" width="64" height="14" stroke="none"/></svg>')


def cover_markup(slug, meta):
    """Inline SVG cover (follows the site colours), or the post's own image from `cover:`."""
    if meta.get("cover"):
        return f'<img src="/blog/{slug}/{escape(meta["cover"])}" alt="" loading="lazy">'
    f = SRC / slug / "cover.svg"
    svg = f.read_text(encoding="utf-8").strip() if f.exists() else DEFAULT_COVER
    return svg.replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)


OG_VERSION = "1"


def og_image(slug, meta):
    """1200x630 PNG for link previews, rendered once with headless Chrome and cached."""
    import hashlib
    import subprocess
    import tempfile
    art = cover_markup(slug, meta) if not meta.get("cover") else ""
    key = hashlib.sha256((OG_VERSION + meta["title"] + art + meta.get("cover", "")).encode()).hexdigest()[:12]
    folder = SRC / slug
    name = f"og-{key}.png"
    for old in folder.glob("og-*.png"):
        if old.name != name:
            old.unlink()
    if (folder / name).exists():
        return name
    if meta.get("cover"):
        visual = f'<img src="file://{folder / meta["cover"]}" style="width:100%;height:100%;object-fit:cover">'
    else:
        visual = art
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{site.FONTS}">
<style>html,body{{margin:0;width:1200px;height:630px;background:#F5F7F9;font-family:'IBM Plex Mono',monospace;color:#14212E}}
.f{{position:absolute;inset:36px;border:2px solid #9FB0C1;background:#fff;display:grid;grid-template-columns:1fr 470px;align-items:center}}
.t{{padding:0 0 0 56px}} h1{{font-size:54px;line-height:1.12;font-weight:600;margin:0 0 28px;letter-spacing:-.01em}}
.b{{font-size:22px;color:#44546A}} .b b{{color:#1E4F86;font-weight:600}}
.v{{height:300px;color:#1E4F86;padding-right:40px}} .v svg{{width:100%;height:100%}} .acc{{fill:#F2A33A}}
.k1,.k2{{position:absolute;width:18px;height:18px;border:3px solid #1E4F86}} .k1{{top:34px;left:34px;border-right:0;border-bottom:0}} .k2{{bottom:34px;right:34px;border-left:0;border-top:0}}</style></head>
<body><div class="f"><div class="t"><h1>{escape(meta["title"])}</h1><div class="b"><b>morebyt.com</b>/blog</div></div><div class="v">{visual}</div></div><i class="k1"></i><i class="k2"></i></body></html>"""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "og.html"
        src.write_text(html, encoding="utf-8")
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
               "--window-size=1200,630", "--virtual-time-budget=6000", f"--screenshot={folder / name}", f"file://{src}"]
        subprocess.run(cmd, check=True, capture_output=True)
    print("rendered", slug, name)
    return name


CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

TOC_JS = """<script>
(function(){
  var links=[].slice.call(document.querySelectorAll('.toc-side a'));
  if(!links.length||!('IntersectionObserver' in window))return;
  var map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a;});
  var heads=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));}).filter(Boolean);
  function set(id){links.forEach(function(a){a.removeAttribute('aria-current');});if(map[id])map[id].setAttribute('aria-current','true');}
  var io=new IntersectionObserver(function(){
    var cur=heads[0];heads.forEach(function(h){if(h.getBoundingClientRect().top<140)cur=h;});set(cur.id);
  },{rootMargin:'0px 0px -60% 0px',threshold:[0,1]});
  heads.forEach(function(h){io.observe(h);});
  window.addEventListener('scroll',function(){var cur=heads[0];heads.forEach(function(h){if(h.getBoundingClientRect().top<140)cur=h;});set(cur.id);},{passive:true});
})();
</script>"""


def toc_markup(tokens):
    h2 = [t for t in tokens if t.get("level") == 2] or [c for t in tokens for c in t.get("children", []) if c.get("level") == 2]
    if len(h2) < 3:
        return "", ""
    items = "".join(f'<li><a href="#{t["id"]}">{t["name"]}</a></li>' for t in h2)
    side = f'<aside class="toc toc-side"><nav aria-label="On this page"><p class="toc-title">On this page</p><ol>{items}</ol></nav></aside>'
    top = f'<details class="toc toc-top"><summary>On this page</summary><nav aria-label="On this page"><ol>{items}</ol></nav></details>'
    return side, top


def post_page(slug, meta, body):
    html, tokens = render_md(body)
    side, top = toc_markup(tokens)
    url = f"/blog/{slug}/"
    upd = f'<span>Updated <time datetime="{meta["updated"]}">{nice(meta["updated"])}</time></span>' if meta.get("updated") else ""
    video = (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{escape(meta["video"])}" '
             f'title="Video: {escape(meta["title"])}" loading="lazy" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe></div>'
             if meta.get("video") else "")
    og = og_image(slug, meta)
    ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"BlogPosting",'
          f'"headline":{_json(meta["title"])},"description":{_json(meta["description"])},'
          f'"image":"{BASE}{url}{og}",'
          f'"datePublished":"{meta["date"]}","dateModified":"{meta.get("updated") or meta["date"]}",'
          f'"author":{{"@type":"Person","name":"Mohammad Reza Bayat","url":"{BASE}/"}},'
          f'"mainEntityOfPage":"{BASE}{url}"}}</script>')
    head = site.head(f'{meta["title"]}: Morebyt', meta["description"], url,
                     og_image=f"{url}{og}", og_image_alt=meta.get("cover_alt") or meta["title"], og_type="article")
    head = head.replace("</head>", ld + "\n</head>")
    return (head + POST_CSS + LAYOUT_CSS + site.header("/blog") + f"""
<main id="main"><div class="wrap post-wrap"><div class="post-grid">
<article class="post">
  <header>
    <div class="cover">{cover_markup(slug, meta)}</div>
    <h1>{escape(meta["title"])}</h1>
    <p class="meta"><span>Mohammad Reza Bayat</span><time datetime="{meta["date"]}">{nice(meta["date"])}</time>{upd}<span>{minutes(body)} min read</span></p>
  </header>
  {top}
  {video}
  <div class="prose">
{html}
  </div>
  <div class="after sheet">
    <h2 style="font-size:20px">Get the next post by email</h2>
    {site.signup("email-post", button="Join the list")}
  </div>
</article>
{side}
</div></div></main>
{TOC_JS if side else ""}
""" + site.footer())


def _json(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def index_page(posts):
    items = "".join(
        f'<li><a class="thumb" href="/blog/{slug}/" tabindex="-1" aria-hidden="true">{cover_markup(slug, m)}</a>'
        f'<div><h2><a href="/blog/{slug}/">{escape(m["title"])}</a></h2><p>{escape(m["description"])}</p>'
        f'<p class="meta"><time datetime="{m["date"]}">{nice(m["date"])}</time>'
        f'{"<span>" + escape(", ".join(m["tags"])) + "</span>" if m["tags"] else ""}</p></div></li>'
        for slug, m, _ in posts)
    return (site.head("Blog: Morebyt",
                      "Written versions of the Morebyt videos and longer posts on C++, software design and how computers work.",
                      "/blog/") + LIST_CSS + site.header("/blog") + f"""
<main id="main"><div class="wrap"><div class="page">
  <h1>Blog</h1>
  <p class="lede">Posts on C++, software design and how computers work underneath. From January 2027, every build video gets a written version here too, with the code.</p>
  <ul class="posts">{items}</ul>
  <div class="join sheet">
    <h2 style="font-size:20px">Get new posts by email</h2>
    {site.signup("email-blog", button="Join the list")}
  </div>
</div></div></main>
""" + site.footer())


def feed(posts):
    entries = "".join(
        f"<item><title>{escape(m['title'])}</title><link>{BASE}/blog/{slug}/</link>"
        f"<guid>{BASE}/blog/{slug}/</guid><pubDate>{m['date'].strftime('%a, %d %b %Y')} 08:00:00 +0000</pubDate>"
        f"<description>{escape(m['description'])}</description></item>"
        for slug, m, _ in posts)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f"<title>Morebyt</title><link>{BASE}/blog/</link><description>How computers really work, built from scratch in C++.</description>"
            f"{entries}</channel></rss>\n")


STATIC_PAGES = ["/", "/career/", "/career/cpp-roadmap/", "/projects/", "/blog/", "/consulting/"]


def sitemap(posts):
    urls = [f"<url><loc>{BASE}{u}</loc></url>" for u in STATIC_PAGES]
    urls += [f"<url><loc>{BASE}/blog/{slug}/</loc><lastmod>{m.get('updated') or m['date']}</lastmod></url>"
             for slug, m, _ in posts]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n</urlset>\n")


def main():
    posts = []
    for d in sorted(p for p in SRC.iterdir() if (p / "index.md").exists()):
        meta, body = parse(d / "index.md")
        body = drawings(d.name, diagrams(d.name, body))
        if meta.get("draft") == "true":
            continue
        posts.append((d.name, meta, body))
    posts.sort(key=lambda x: x[1]["date"], reverse=True)

    for slug, meta, body in posts:
        out = OUT / slug
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        og_image(slug, meta)  # render the link-preview PNG before copying files
        for f in (SRC / slug).iterdir():
            if f.name not in ("index.md", "cover.svg") and f.is_file():
                shutil.copy2(f, out / f.name)
        (out / "index.html").write_text(post_page(slug, meta, body), encoding="utf-8")
        print("built", out.relative_to(ROOT))
    (OUT / "index.html").write_text(index_page(posts), encoding="utf-8")
    (ROOT / "public" / "feed.xml").write_text(feed(posts), encoding="utf-8")
    (ROOT / "public" / "sitemap.xml").write_text(sitemap(posts), encoding="utf-8")
    (ROOT / "public" / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    print(f"built public/blog/index.html and feed.xml ({len(posts)} posts)")


if __name__ == "__main__":
    main()
