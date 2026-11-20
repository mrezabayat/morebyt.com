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
.post{max-width:72ch;padding:var(--s6) 0 var(--s5)}
.post header{margin-bottom:var(--s5)}
.post h1{font-size:clamp(30px,5vw,46px);margin-bottom:var(--s3)}
.meta{font:14px/1.6 var(--mono);color:var(--ink-2)}
.meta a{color:var(--ink-2)}
.prose{font-size:19px;line-height:1.7}
.prose h2{font-size:clamp(23px,3vw,28px);margin:var(--s6) 0 var(--s3)}
.prose h3{font-size:20px;margin:var(--s5) 0 var(--s2)}
.prose p,.prose ul,.prose ol,.prose table,.prose blockquote,.prose pre{margin:0 0 var(--s4)}
.prose li{margin-bottom:6px}
.prose img{display:block;margin:var(--s4) auto;max-height:560px;background:#fff;border:1px solid var(--rule);padding:8px}
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
/* code colours: light */
.hl .k,.hl .kd,.hl .kt,.hl .kr,.hl .kn,.hl .cp{color:#7a2e8a}
.hl .s,.hl .s1,.hl .s2,.hl .sc,.hl .cpf{color:#1f6a3a}
.hl .c,.hl .c1,.hl .cm{color:#6a7785;font-style:italic}
.hl .m,.hl .mi,.hl .mf,.hl .mh{color:#a3501a}
.hl .nf,.hl .nc{color:#1E4F86}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .hl .k,:root:not([data-theme="light"]) .hl .kd,:root:not([data-theme="light"]) .hl .kt,:root:not([data-theme="light"]) .hl .kr,:root:not([data-theme="light"]) .hl .kn,:root:not([data-theme="light"]) .hl .cp{color:#d6a3f0}
:root:not([data-theme="light"]) .hl .s,:root:not([data-theme="light"]) .hl .s1,:root:not([data-theme="light"]) .hl .s2,:root:not([data-theme="light"]) .hl .sc,:root:not([data-theme="light"]) .hl .cpf{color:#8fd9a8}
:root:not([data-theme="light"]) .hl .c,:root:not([data-theme="light"]) .hl .c1,:root:not([data-theme="light"]) .hl .cm{color:#8b99a8}
:root:not([data-theme="light"]) .hl .m,:root:not([data-theme="light"]) .hl .mi,:root:not([data-theme="light"]) .hl .mf,:root:not([data-theme="light"]) .hl .mh{color:#f0b07a}
:root:not([data-theme="light"]) .hl .nf,:root:not([data-theme="light"]) .hl .nc{color:#8DB6E6}}
</style>"""

LIST_CSS = """
<style>
.page{padding:var(--s6) 0 var(--s5);max-width:860px}
.page h1{margin-bottom:var(--s4)}
.posts{list-style:none;margin:var(--s5) 0 0;padding:0}
.posts li{padding:var(--s4) 0;border-top:1px solid var(--rule)}
.posts li:last-child{border-bottom:1px solid var(--rule)}
.posts h2{font-size:22px;margin:0 0 6px}
.posts h2 a{color:var(--ink);text-decoration:none}
.posts h2 a:hover{text-decoration:underline;text-underline-offset:4px}
.posts p{margin:0 0 6px;color:var(--ink-2)}
.posts .meta{font:14px var(--mono);color:var(--ink-2)}
.join{margin-top:var(--s6)}
</style>"""


def post_page(slug, meta, body):
    html, _ = render_md(body)
    url = f"/blog/{slug}/"
    upd = f' · updated <time datetime="{meta["updated"]}">{nice(meta["updated"])}</time>' if meta.get("updated") else ""
    video = (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{escape(meta["video"])}" '
             f'title="Video: {escape(meta["title"])}" loading="lazy" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe></div>'
             if meta.get("video") else "")
    ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"BlogPosting",'
          f'"headline":{_json(meta["title"])},"description":{_json(meta["description"])},'
          f'"datePublished":"{meta["date"]}","dateModified":"{meta.get("updated") or meta["date"]}",'
          f'"author":{{"@type":"Person","name":"Mohammad Reza Bayat","url":"{BASE}/"}},'
          f'"mainEntityOfPage":"{BASE}{url}"}}</script>')
    head = site.head(f'{meta["title"]}: Morebyt', meta["description"], url).replace(
        '<meta property="og:type" content="website">', '<meta property="og:type" content="article">')
    head = head.replace("</head>", ld + "\n</head>")
    return (head + POST_CSS + site.header("/blog") + f"""
<main id="main"><div class="wrap"><article class="post">
  <header>
    <h1>{escape(meta["title"])}</h1>
    <p class="meta">By Mohammad Reza Bayat · <time datetime="{meta["date"]}">{nice(meta["date"])}</time>{upd} · {minutes(body)} min read</p>
  </header>
  {video}
  <div class="prose">
{html}
  </div>
  <div class="after sheet">
    <h2 style="font-size:20px">Get the next post by email</h2>
    {site.signup("email-post", button="Join the list")}
  </div>
</article></div></main>
""" + site.footer())


def _json(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def index_page(posts):
    items = "".join(
        f'<li><h2><a href="/blog/{slug}/">{escape(m["title"])}</a></h2><p>{escape(m["description"])}</p>'
        f'<p class="meta"><time datetime="{m["date"]}">{nice(m["date"])}</time>'
        f'{" · " + escape(", ".join(m["tags"])) if m["tags"] else ""}</p></li>'
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


def main():
    posts = []
    for d in sorted(p for p in SRC.iterdir() if (p / "index.md").exists()):
        meta, body = parse(d / "index.md")
        if meta.get("draft") == "true":
            continue
        posts.append((d.name, meta, body))
    posts.sort(key=lambda x: x[1]["date"], reverse=True)

    for slug, meta, body in posts:
        out = OUT / slug
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        for f in (SRC / slug).iterdir():
            if f.name != "index.md" and f.is_file():
                shutil.copy2(f, out / f.name)
        (out / "index.html").write_text(post_page(slug, meta, body), encoding="utf-8")
        print("built", out.relative_to(ROOT))
    (OUT / "index.html").write_text(index_page(posts), encoding="utf-8")
    (ROOT / "public" / "feed.xml").write_text(feed(posts), encoding="utf-8")
    print(f"built public/blog/index.html and feed.xml ({len(posts)} posts)")


if __name__ == "__main__":
    main()
