#!/usr/bin/env python3
"""Builds the static pages of morebyt.com into public/.

    python3 scripts/build_site.py      -> public/index.html, consulting/, blog/, 404.html

The roadmap page has its own generator (build_roadmap.py) but uses the same
head(), header() and footer() from here.
"""
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"

YT = "https://www.youtube.com/@morebyt"
EMAIL = "hello@morebyt.com"
KIT_ACTION = "https://app.kit.com/forms/10219372/subscriptions"
FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600"
         "&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap")
import json as _json
DATA = _json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
NOW = DATA["now_building"]
PLAYLIST_URL = f"https://www.youtube.com/playlist?list={NOW['playlist_id']}"


def nb(text):
    """Keep tokens like CHIP-8 on one line."""
    return re.sub(r"\b([A-Z]+-\d+)\b", r'<span class="nb">\1</span>', escape(text))


MARK_SVG = """<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6">
<rect x="5" y="5" width="14" height="14" rx="1.5"/><rect x="9" y="9" width="6" height="6"/>
<path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/></svg>"""


THEME_HEAD_JS = """<script>
(function(){var r=document.documentElement;
try{var t=localStorage.getItem('morebyt-theme');if(t==='light'||t==='dark')r.dataset.theme=t;}catch(e){}
r.dataset.themeNow=r.dataset.theme||(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');})();
</script>"""

THEME_FOOT_JS = """<script>
(function(){var r=document.documentElement,b=document.querySelector('.theme-toggle'),
mq=window.matchMedia?matchMedia('(prefers-color-scheme: dark)'):{matches:false};
function now(){return r.dataset.theme||(mq.matches?'dark':'light');}
function apply(){var n=now();r.dataset.themeNow=n;
[].forEach.call(document.querySelectorAll('picture source[data-dark]'),function(s){
s.media=r.dataset.theme?(r.dataset.theme==='dark'?'all':'not all'):'(prefers-color-scheme: dark)';});
if(b){b.setAttribute('aria-label',n==='dark'?'Switch to light mode':'Switch to dark mode');b.title=b.getAttribute('aria-label');}}
if(b)b.addEventListener('click',function(){var next=now()==='dark'?'light':'dark';r.dataset.theme=next;
try{localStorage.setItem('morebyt-theme',next);}catch(e){}apply();});
if(mq.addEventListener)mq.addEventListener('change',apply);apply();})();
</script>"""

TOGGLE_BUTTON = ('<button class="theme-toggle" type="button" aria-label="Switch colour theme">'
    '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true">'
    '<circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></svg>'
    '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg></button>')


def head(title, description, path, extra_css="", og_image=None, og_image_alt=None, og_type="website"):
    url = "https://morebyt.com" + path
    css = '<link rel="stylesheet" href="/assets/site.css">' + (
        f'\n<link rel="stylesheet" href="{extra_css}">' if extra_css else "")
    if og_image:
        img = og_image if og_image.startswith("http") else "https://morebyt.com" + og_image
        css += (f'\n<meta property="og:image" content="{img}">'
                '\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">'
                f'\n<meta property="og:image:alt" content="{escape(og_image_alt or title)}">'
                '\n<meta name="twitter:card" content="summary_large_image">'
                f'\n<meta name="twitter:image" content="{img}">')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{THEME_HEAD_JS}
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{og_type}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#F5F7F9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E151C" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
{css}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>"""


def header(current):
    items = [("/roadmap", "Roadmap"), ("/blog", "Blog"), ("/projects", "Projects"), ("/consulting", "Consulting"), (YT, "YouTube")]
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{h}"{cur if h == current else ""}>{n}</a>' for h, n in items)
    return f"""<header class="site-head"><div class="wrap">
  <a class="mark" href="/">{MARK_SVG}morebyt</a>
  <div class="head-right"><nav class="nav" aria-label="Main">{links}</nav>{TOGGLE_BUTTON}</div>
</div></header>"""


def footer():
    return f"""<footer class="site-foot"><div class="wrap">
  <div class="titleblock">
    <div><span>Project</span>Morebyt: build it to understand it</div>
    <div><span>Drawn by</span>Mohammad Reza Bayat</div>
    <div><span>Videos</span><a href="{YT}">youtube.com/@morebyt</a></div>
    <div><span>Contact</span><a href="mailto:{EMAIL}">{EMAIL}</a></div>
  </div>
</div></footer>
{THEME_FOOT_JS}
</body>
</html>
"""


def signup(field_id, button="Send me the roadmap", label="Your email",
           fine="Free. You get the one-page C++ Roadmap 2027 checklist, then an email when a new video or post is out. Unsubscribe any time."):
    return f"""<form class="signup" action="{KIT_ACTION}" method="post">
  <label for="{field_id}">{label}</label>
  <div class="row">
    <input id="{field_id}" name="email_address" type="email" autocomplete="email" required placeholder="you@example.com">
    <button class="btn btn-primary" type="submit">{button}</button>
  </div>
  <p class="fine">{fine}</p>
</form>"""


# ------------------------------------------------------------------ the hero drawing
CHIP8_SVG = """<svg class="drawing" viewBox="0 0 560 450" role="img" aria-labelledby="fig1-t fig1-d">
<title id="fig1-t">Line drawing of a CHIP-8 computer</title>
<desc id="fig1-d">Front view of a small 1970s computer: a monitor showing a game of Pong on a 64 by 32 pixel screen, sitting on a base with a 16-key hexadecimal keypad.</desc>
<defs>
  <marker id="arw" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0 8 4 0 8" fill="none" stroke="currentColor" stroke-width="1.2"/></marker>
</defs>
<g class="ink" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">
  <!-- monitor -->
  <rect class="d" pathLength="1" x="150" y="40" width="260" height="190" rx="12"/>
  <rect class="d" pathLength="1" x="172" y="60" width="216" height="128" rx="6"/>
  <path class="d" pathLength="1" d="M172 204h180"/>
  <circle class="d" pathLength="1" cx="383" cy="214" r="5"/>
  <path class="d" pathLength="1" d="M250 230 238 252h84l-12-22"/>
  <!-- base -->
  <rect class="d" pathLength="1" x="50" y="252" width="460" height="128" rx="8"/>
  <path class="d" pathLength="1" d="M50 362h460"/>
  <path class="d" pathLength="1" d="M76 284h120M76 296h120M76 308h120M76 320h120"/>
  <rect class="d" pathLength="1" x="76" y="334" width="34" height="16" rx="3"/>
  <circle class="d" pathLength="1" cx="132" cy="342" r="5"/>
</g>
<!-- keypad: 4 x 4, COSMAC VIP layout -->
<g class="keys" font-family="IBM Plex Mono, monospace" font-size="12" text-anchor="middle">
  KEYS
</g>
<!-- screen: Pong in fat pixels -->
<g class="px">
  <rect x="190" y="104" width="6" height="30"/><rect x="364" y="126" width="6" height="30"/>
  <rect x="300" y="112" width="6" height="6"/>
  <path d="M280 66v6M280 80v6M280 94v6M280 108v6M280 122v6M280 136v6M280 150v6M280 164v6M280 178v6" stroke="currentColor" stroke-width="3" fill="none"/>
  SCORE
</g>
<!-- dimensions and callouts -->
<g class="dim" fill="none" stroke="currentColor" stroke-width="1">
  <path d="M172 34V20M388 34V20"/><path d="M178 24h204" marker-start="url(#arw)" marker-end="url(#arw)"/>
  <path d="M396 60h22M396 188h22"/><path d="M414 66v116" marker-start="url(#arw)" marker-end="url(#arw)"/>
  <path d="M130 342 92 404H40"/><path d="M436 352l30 52h54"/>
</g>
<g class="note" font-family="IBM Plex Mono, monospace" font-size="13">
  <text x="280" y="14" text-anchor="middle">64 px</text>
  <text x="424" y="128">32 px</text>
  <text x="40" y="422">CPU + 4 KB memory</text>
  <text x="520" y="422" text-anchor="end">16 keys, 0 to F</text>
</g>
</svg>"""


DIGITS = {"1": ["010", "110", "010", "010", "111"], "2": ["111", "001", "111", "100", "111"]}


def score():
    out = []
    for ch, x0 in (("1", 246), ("2", 302)):
        for r, row in enumerate(DIGITS[ch]):
            for c, bit in enumerate(row):
                if bit == "1":
                    out.append(f'<rect x="{x0 + c * 4}" y="{70 + r * 4}" width="4" height="4"/>')
    return "".join(out)


def keypad():
    rows = ["123C", "456D", "789E", "A0BF"]
    out = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            x, y = 330 + c * 40, 270 + r * 22
            out.append(f'<rect class="d" pathLength="1" x="{x}" y="{y}" width="32" height="18" rx="2" fill="none" stroke="currentColor" stroke-width="1.4"/>'
                       f'<text x="{x + 16}" y="{y + 13.5}" fill="currentColor">{ch}</text>')
    return "".join(out)


HOME_CSS = """
<style>
.hero{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:var(--s5);align-items:center;padding:var(--s6) 0 var(--s6)}
.hero h1{margin-bottom:var(--s4)}
.cursor{display:inline-block;width:.55em;height:.09em;background:var(--amber);vertical-align:baseline;margin-left:.06em;animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.who{display:flex;align-items:center;gap:14px;margin:var(--s4) 0 var(--s4)}
.who img{width:64px;height:64px;border-radius:50%;flex:none;border:1px solid var(--rule-2)}
.who p{margin:0;font-size:16px;line-height:1.45}
.who b{font-family:var(--mono);font-weight:600;font-size:15px}
figure{margin:0}
.drawing{display:block;width:100%;color:var(--line)}
.drawing .keys{color:var(--line)}
.drawing .keys text{fill:var(--ink-2)}
.drawing .px{fill:var(--ink);color:var(--ink)}
.drawing .dim{color:var(--ink-2)}
.drawing .note{fill:var(--ink-2)}
.drawing .d{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.8s cubic-bezier(.4,0,.2,1) forwards}
.drawing .px,.drawing .dim,.drawing .note,.drawing .keys text{opacity:0;animation:show .5s 1.4s ease-out forwards}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes show{to{opacity:1}}
@media (prefers-reduced-motion:reduce){.drawing .d{stroke-dashoffset:0}.drawing .px,.drawing .dim,.drawing .note,.drawing .keys text{opacity:1}.cursor{opacity:1}}
figcaption{font:14px/1.5 var(--mono);color:var(--ink-2);margin-top:var(--s2);border-top:1px solid var(--rule);padding-top:var(--s2)}

.eps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--s4) var(--s4)}
.ep a{display:block;text-decoration:none;color:var(--ink)}
.ep img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;border:1px solid var(--rule-2);background:var(--rule)}
.ep .n{display:block;font:500 14px var(--mono);color:var(--ink-2);margin:10px 0 2px}
.ep .t{font-size:18px;line-height:1.35}
.ep a:hover .t{text-decoration:underline;text-underline-offset:3px}
.ep.next .box{display:grid;place-items:center;aspect-ratio:16/9;border:1.5px dashed var(--rule-2);font:500 15px var(--mono);color:var(--ink-2);text-align:center;padding:12px}

.register{width:100%;border-collapse:collapse;font-size:17px;margin-top:var(--s3)}
.register th{font:500 14px var(--mono);color:var(--ink-2);text-align:left;padding:8px 12px 8px 0;border-bottom:1px solid var(--rule-2)}
.register td{padding:14px 12px 14px 0;border-bottom:1px solid var(--rule);vertical-align:top}
.register td:first-child{font-family:var(--mono);font-size:15px;color:var(--ink-2);width:3ch}
.register .st{font:500 14px var(--mono);white-space:nowrap}
.register .now{color:var(--good)}

.split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:var(--s5);align-items:start}
@media (max-width:900px){
  .hero,.split{grid-template-columns:1fr}
  .hero{padding-top:var(--s5)}
  .eps{grid-template-columns:1fr 1fr}
}
@media (max-width:560px){.eps{grid-template-columns:1fr}.register td:last-child,.register th:last-child{display:none}}
</style>"""


def home():
    pl = NOW["playlist_id"]
    eps = "".join(
        f'<li class="ep"><a href="https://www.youtube.com/watch?v={e["id"]}&list={pl}">'
        f'<img src="https://i.ytimg.com/vi/{e["id"]}/mqdefault.jpg" width="320" height="180" loading="lazy" alt="">'
        f'<span class="n">Episode {i}</span><span class="t">{escape(e["title"])}</span></a></li>'
        for i, e in enumerate(NOW["episodes"], 1))
    nxt = NOW.get("next_episode")
    if nxt:
        when = f'<br>{escape(nxt["when"])}' if nxt.get("when") else ""
        eps += (f'<li class="ep next"><div class="box">Episode {len(NOW["episodes"]) + 1}<br>{escape(nxt["title"])}{when}</div></li>')
    builds = "".join(
        f'<tr><td>{i:02d}</td><td>{escape(b["what"])}</td><td class="st{" now" if b["status"] == "Filming now" else ""}">{escape(b["status"])}</td><td class="muted">{escape(b["when"])}</td></tr>'
        for i, b in enumerate(DATA["builds"], 1))
    svg = CHIP8_SVG.replace("KEYS", keypad()).replace("SCORE", score())
    return (head("Morebyt: how computers really work, built from scratch in C++",
                 "Mohammad Reza Bayat builds emulators, operating systems and compilers from scratch in C++ on YouTube, one step at a time.",
                 "/") + HOME_CSS + header("/") + f"""
<main id="main">
<div class="wrap">
  <section class="hero">
    <div>
      <h1>How computers really work<span class="cursor" aria-hidden="true"></span></h1>
      <p class="lede">I build emulators, operating systems and compilers from scratch in C++, and film every step. Follow one build and you'll know what your own code is doing underneath.</p>
      <div class="who">
        <img src="/assets/mohammad.jpg" width="64" height="64" alt="Mohammad Reza Bayat">
        <p><b>Mohammad Reza Bayat</b><br><span class="muted">C++ engineer. I make Morebyt.</span></p>
      </div>
      <div class="actions">
        <a class="btn btn-primary" href="{PLAYLIST_URL}">{nb(NOW["button"])}</a>
        <a class="btn btn-ghost" href="/roadmap">Free C++ roadmap</a>
      </div>
    </div>
    <figure>
      {svg}
      <figcaption>{escape(NOW["hero_caption"])}</figcaption>
    </figure>
  </section>
</div>

<section class="section" aria-labelledby="chip8-h"><div class="wrap">
  <div class="section-head">
    <h2 id="chip8-h">{nb(NOW["title"])}</h2>
    <p class="lede">{escape(NOW["summary"])}</p>
  </div>
  <ol class="eps">{eps}</ol>
  <p style="margin-top:var(--s4)"><a href="{PLAYLIST_URL}">The full playlist on YouTube</a>. Everything else I build is on the <a href="/projects/">projects page</a>.</p>
</div></section>

<section class="section" aria-labelledby="builds-h"><div class="wrap split">
  <div>
    <h2 id="builds-h">What we build next</h2>
    <p class="lede">One machine at a time, from the bottom up. Each build is a series you can follow from an empty folder.</p>
  </div>
  <table class="register">
    <thead><tr><th scope="col">No.</th><th scope="col">Build</th><th scope="col">Status</th><th scope="col">When</th></tr></thead>
    <tbody>{builds}</tbody>
  </table>
</div></section>

<section class="section" aria-labelledby="roadmap-h"><div class="wrap split">
  <div>
    <h2 id="roadmap-h">Learning C++ for a job?</h2>
    <p class="lede">The C++ Roadmap 2027: what to learn in order, what to skip, and where the jobs really are. Read it on the site, or get the one-page checklist by email.</p>
    <p><a href="/roadmap">Read the roadmap</a></p>
  </div>
  <div class="sheet">{signup("email-home")}</div>
</div></section>

<section class="section" aria-labelledby="hire-h"><div class="wrap split">
  <h2 id="hire-h">Need help with C++?</h2>
  <div>
    <p class="lede">I review C++ code, track down slow or crashing programs, mentor learners and run workshops for teams.</p>
    <a class="btn btn-ghost" href="/consulting">See how I can help</a>
  </div>
</div></section>
</main>
""" + footer())


PAGE_CSS = """
<style>
.page{padding:var(--s6) 0 var(--s5);max-width:860px}
.page h1{margin-bottom:var(--s4)}
.services{list-style:none;margin:var(--s5) 0 0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:var(--s4)}
.services h2{font-size:20px;margin-bottom:var(--s2)}
.services p{margin:0;color:var(--ink-2)}
.services .fit{margin-top:var(--s2);font-size:16px}
.steps{margin:var(--s3) 0 0;padding-left:1.4em;max-width:var(--measure)}
.steps li{margin-bottom:var(--s2);padding-left:6px}
.steps li::marker{font-family:var(--mono);color:var(--ink-2)}
.empty{margin-top:var(--s5)}
.empty h2{font-size:22px}
@media (max-width:760px){.services{grid-template-columns:1fr}}
</style>"""

SERVICES = [
    ("C++ code review",
     "I read your code or your pull requests and send back what I'd change and why: ownership and lifetimes, error handling, design, and where modern C++ makes it simpler.",
     "For teams who want a second pair of senior eyes, or solo developers shipping something that matters."),
    ("Performance and debugging",
     "Slow builds, slow programs, crashes that only happen in production, memory that keeps growing. I measure first, find the cause with profilers and sanitizers, and show you the fix.",
     "For a specific problem you've been stuck on."),
    ("One-to-one mentoring",
     "Video calls about what you're learning or building: reviewing your projects, planning what to learn next, or practising for C++ interviews.",
     "For learners and junior engineers."),
    ("Team workshops",
     "Hands-on sessions on modern C++, memory and object lifetime, or how the machine runs your code. Built around your codebase where possible.",
     "For teams moving to modern C++ or onboarding new people."),
]


def consulting():
    svc = "".join(f'<li class="sheet"><h2>{escape(n)}</h2><p>{escape(d)}</p><p class="fit">{escape(f)}</p></li>' for n, d, f in SERVICES)
    subject = "C%2B%2B%20help"
    return (head("C++ consulting and mentoring: Morebyt",
                 "C++ code review, performance and debugging, one-to-one mentoring and team workshops from Mohammad Reza Bayat, a working C++ engineer.",
                 "/consulting/") + PAGE_CSS + header("/consulting") + f"""
<main id="main"><div class="wrap"><div class="page">
  <h1>C++ help from a working engineer</h1>
  <p class="lede">I'm Mohammad Reza Bayat. I write C++ for a living and explain how computers work on the Morebyt channel. If you're stuck on a C++ problem, or want someone to check your work, I can help.</p>
  <ul class="services">{svc}</ul>

  <section class="section" style="margin-top:var(--s6)" aria-labelledby="how-h">
    <h2 id="how-h">How it works</h2>
    <ol class="steps">
      <li>Email me what you need: a few lines about the code, the problem and your deadline.</li>
      <li>We have a short call to check I'm the right person for it.</li>
      <li>I send a fixed price and a date. You only pay for what we agreed.</li>
    </ol>
    <div class="actions" style="margin-top:var(--s4)">
      <a class="btn btn-primary" href="mailto:{EMAIL}?subject={subject}">Email {EMAIL}</a>
    </div>
  </section>
</div></div></main>
""" + footer())


def blog():
    return (head("Blog: Morebyt",
                 "Written versions of the Morebyt videos, with the code: how computers really work, built from scratch in C++.",
                 "/blog/") + PAGE_CSS + header("/blog") + f"""
<main id="main"><div class="wrap"><div class="page">
  <h1>Blog</h1>
  <p class="lede">Written versions of the videos, with the code and the diagrams, so you can read at your own pace and copy what you need.</p>
  <div class="empty sheet">
    <h2>No posts yet</h2>
    <p>The first posts arrive in January 2027, starting with the CHIP-8 series. Join the email list and you'll get each one when it's out, plus the free C++ roadmap checklist.</p>
    {signup("email-blog", button="Join the list")}
  </div>
</div></div></main>
""" + footer())


PROJECT_ICONS = {
    "chip8": '<rect x="18" y="14" width="84" height="50" rx="3"/><rect x="28" y="30" width="4" height="14" fill="currentColor" stroke="none"/><rect x="88" y="38" width="4" height="14" fill="currentColor" stroke="none"/><rect class="acc" x="58" y="36" width="5" height="5" stroke="none"/><path d="M60 18v42" stroke-dasharray="2 4" stroke-width="1.2"/>'
             + "".join(f'<rect x="{30 + c * 16}" y="{74 + r * 13}" width="12" height="9" rx="1" stroke-width="1.2"/>' for r in range(2) for c in range(4)),
    "csmap": '<circle cx="60" cy="54" r="10"/><circle cx="22" cy="24" r="7"/><circle cx="98" cy="22" r="7"/><circle cx="20" cy="88" r="7"/><circle cx="100" cy="90" r="7"/><circle cx="60" cy="12" r="5"/>'
             '<path d="M52 47 28 29M68 47l24-19M52 61 26 83M68 61l26 24M60 44V17M29 24h26M65 12l26 8" stroke-width="1.3"/><circle class="acc" cx="60" cy="54" r="5" stroke="none"/>',
    "chess": "".join(f'<rect x="{20 + c * 20}" y="{12 + r * 20}" width="20" height="20"' + (' fill="currentColor" fill-opacity=".14"' if (r + c) % 2 else "") + "/>" for r in range(4) for c in range(4))
             + '<path class="acc" d="M74 70l14-16" stroke-width="3"/><circle class="acc" cx="90" cy="52" r="4" stroke="none"/>',
}

PROJECTS_CSS = """
<style>
.page{padding:var(--s6) 0 var(--s5)}
.page h1{margin-bottom:var(--s4)}
.plist{list-style:none;margin:var(--s5) 0 0;padding:0}
.plist li{display:grid;grid-template-columns:200px minmax(0,1fr);gap:var(--s4) var(--s5);align-items:start;padding:var(--s4) 0;border-top:1px solid var(--rule)}
.plist li:last-child{border-bottom:1px solid var(--rule)}
.picon{background:var(--sheet);border:1px solid var(--rule-2);aspect-ratio:12/11;color:var(--line);padding:12px}
.picon svg{display:block;width:100%;height:100%}
.picon .acc{fill:var(--amber)} .picon path.acc{stroke:var(--amber);fill:none}
.plist h2{font-size:clamp(20px,2.4vw,24px);margin:0 0 6px}
.plist .st{font:500 14px var(--mono);color:var(--good);margin:0 0 10px}
.plist p{max-width:68ch;color:var(--ink-2)}
.plist .links{display:flex;flex-wrap:wrap;gap:8px 20px;font:500 15px var(--mono);margin:0}
@media (max-width:640px){.plist li{grid-template-columns:96px minmax(0,1fr);gap:var(--s3)}}
</style>"""


def projects():
    items = []
    for pr in DATA["projects"]:
        icon = PROJECT_ICONS.get(pr.get("icon"), PROJECT_ICONS["chip8"])
        links = "".join(f'<a href="{escape(l["url"])}">{escape(l["label"])}</a>' for l in pr.get("links", []))
        items.append(
            f'<li><div class="picon"><svg viewBox="0 0 120 110" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">{icon}</svg></div>'
            f'<div><h2>{nb(pr["name"])}</h2><p class="st">{escape(pr["status"])}</p><p>{escape(pr["text"])}</p>'
            + (f'<p class="links">{links}</p>' if links else "") + "</div></li>")
    return (head("Projects: Morebyt",
                 "Things Mohammad Reza Bayat has built: a CHIP-8 emulator in C++, CS Map, and Logichess, a chess tutor that explains moves.",
                 "/projects/") + PROJECTS_CSS + header("/projects") + f"""
<main id="main"><div class="wrap"><div class="page">
  <h1>Projects</h1>
  <p class="lede">Things I've built, most of them on video. The code is open where it can be, so you can read it, run it and build your own.</p>
  <ul class="plist">{"".join(items)}</ul>
</div></div></main>
""" + footer())


def not_found():
    page = head("Page not found: Morebyt", "This page doesn't exist.", "/404")
    page = re.sub(r'<link rel="canonical"[^>]*>\n', '<meta name="robots" content="noindex">\n', page)
    page = re.sub(r'<meta property="og:url"[^>]*>\n', "", page)
    return (page + PAGE_CSS + header("") + """
<main id="main"><div class="wrap"><div class="page">
  <h1>Nothing at this address</h1>
  <p class="lede">The page may have moved, or the link has a typo.</p>
  <div class="actions"><a class="btn btn-primary" href="/">Go to the home page</a><a class="btn btn-ghost" href="/roadmap">C++ roadmap</a></div>
</div></div></main>
""" + footer())


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#1E4F86" stroke-width="1.8">
<rect x="5" y="5" width="14" height="14" rx="1.5" fill="#F5F7F9"/><rect x="9" y="9" width="6" height="6" fill="#F2A33A" stroke="none"/>
<path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/></svg>"""


def write(rel, text):
    p = PUB / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print("built", p.relative_to(ROOT))


if __name__ == "__main__":
    write("index.html", home())
    write("consulting/index.html", consulting())
    write("projects/index.html", projects())
    # blog/index.html is built by build_blog.py
    write("404.html", not_found())
    write("assets/favicon.svg", FAVICON)
