"""Builds the C++ Roadmap 2027 web page and the printable checklist from one data set.

    python3 scripts/build_roadmap.py  -> public/roadmap/index.html, pdf/print.html
    then render the PDF with Chrome (see render_pdf.sh)

Content source: ../roadmap-research/COMBINED-Cpp-Roadmap-2027.md (edit the data here when it changes).
"""
import html, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site as site

HERE = Path(__file__).resolve().parent.parent   # repo root
UPDATED = "20 Nov 2026"
SIGNUP_ACTION = "https://app.kit.com/forms/10219372/subscriptions"   # Kit form "C++ Roadmap 2027" (uid 4b3a0fbf69)
YT = "https://www.youtube.com/@morebyt"

def t(s):
    """escape text, then turn `code` into <code>"""
    s = html.escape(s)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)

# ---------------------------------------------------------------- data
STAGES = [
 dict(n=1, title="Tools and core language", weeks="4–6 weeks",
      goal="Compile, run, debug and commit a small program from the terminal.",
      learn=["A current GCC, Clang or Visual Studio", "Warnings on: `-std=c++20 -Wall -Wextra`", "Types, `const`, references", "`string`, `vector`, `struct`, `enum class`", "What the preprocessor, compiler and linker do", "A debugger: breakpoints and call stacks", "Git from day one"],
      skip=["Turbo C++ and old college IDEs", "`bits/stdc++.h`", "“Predict the output” UB puzzles", "C-style `char*` strings"],
      prove="A word counter that reads a file, prints the top 20 words, refuses a missing file and builds with zero warnings.",
      check=["Compile with C++20 and all warnings on — zero warnings", "Use references, `const`, `string`, `vector`, `struct`, `enum class`", "Split code into headers and sources; explain what the linker does", "Step through a crash in a debugger; read the call stack", "Commit daily; push to GitHub with a README"]),
 dict(n=2, title="Memory, lifetime and RAII", weeks="6–8 weeks",
      goal="Know when every object is created, copied, moved and destroyed, and who owns it.",
      learn=["Stack vs heap, pointers vs references", "RAII and the Rule of Zero/Five", "Copy vs move (`std::move` is only a cast)", "`unique_ptr` by default; what `shared_ptr` costs", "Dangling: `string_view`, `span`, iterators", "Virtual functions and destructors", "Undefined behaviour you can name", "`-fsanitize=address,undefined` on every debug build"],
      skip=["Custom allocators and placement `new`", "Design-pattern catalogues", "`shared_ptr` instead of deciding who owns it"],
      prove="Your own `Vector<T>` with copy, move, growth and tests — clean under AddressSanitizer and UBSan.",
      check=["Explain stack vs heap, pointer vs reference", "Apply RAII and the Rule of Zero/Five", "Explain `std::move` (it's only a cast)", "`unique_ptr` by default; know what `shared_ptr` costs", "Every debug build runs AddressSanitizer + UBSan", "Build your own `Vector<T>`, sanitizer-clean"]),
 dict(n=3, title="Standard library and modern C++", weeks="6–8 weeks", dsa=True,
      goal="Solve problems with the standard library and read template code without fear.",
      learn=["Containers and their real costs", "Iterator invalidation rules", "Algorithms and lambdas", "`optional`, `variant`, `string_view`, `span`", "Templates constrained with concepts", "C++17 → C++20 → C++23 where your compiler has it", "One error policy: exceptions or `std::expected`"],
      skip=["SFINAE and metaprogramming tricks", "Coroutine internals", "Modules and C++26 features"],
      prove="A generic `LRUCache<K, V>` with a concept-constrained key, `std::expected` errors and tests.",
      check=["Choose the right container; know iterator invalidation", "Use algorithms and lambdas instead of raw loops", "Write a template constrained with a concept", "Use `optional`, `variant`, `span`, `string_view`, `expected`", "2–3 DSA problems a week in clean C++"]),
 dict(n=4, title="A project a stranger can build", weeks="3–4 weeks", dsa=True,
      goal="Anyone can clone your repo, build it with one command and see the tests pass.",
      learn=["Target-based CMake with presets", "One package manager: vcpkg or Conan 2", "GoogleTest or Catch2 through CTest", "clang-format and clang-tidy", "Standard-library hardening in debug builds", "GitHub Actions: build, test, sanitize"],
      skip=["Bazel and Meson", "Learning both package managers", "Cross-compiling (unless embedded)"],
      prove="Your earlier code with CMake presets, one dependency, tests and a green CI badge on two operating systems.",
      check=["Target-based CMake; one-command build", "One dependency through vcpkg or Conan", "Unit tests with GoogleTest or Catch2", "clang-format, clang-tidy, standard-library hardening on", "CI: build + tests + sanitizers on every push"]),
 dict(n=5, title="How the machine works", weeks="6–8 weeks", dsa=True,
      goal="Explain why code is fast or slow — and prove it with numbers.",
      learn=["Caches, cache lines, locality", "Alignment, padding, structs of arrays", "Reading assembly on Compiler Explorer", "Processes, threads, virtual memory, system calls", "TCP, sockets, `epoll`/`kqueue`", "Google Benchmark, `perf`, flame graphs"],
      skip=["Writing assembly by hand", "Lock-free anything", "Optimising what you haven't profiled"],
      prove="A published benchmark: `vector` vs `list` vs `map`, and row- vs column-first loops, explained with cache-miss counts.",
      check=["Explain caches, cache lines, alignment and padding", "Read simple assembly on Compiler Explorer", "Explain processes, threads, virtual memory, system calls", "Write a TCP server with sockets", "Profile, benchmark and publish a write-up"]),
 dict(n=6, title="Concurrency", weeks="5–6 weeks", dsa=True,
      goal="Multithreaded code that's correct first and fast second.",
      learn=["`jthread`, `mutex`, `scoped_lock`, `condition_variable`, `atomic`", "Data race (UB) vs race condition (logic bug)", "Deadlock and lock order", "ThreadSanitizer in its own build", "False sharing", "Acquire/release basics"],
      skip=["General lock-free structures", "`memory_order_relaxed` tricks", "Async frameworks and GPU code"],
      prove="A bounded queue and thread pool, clean under ThreadSanitizer, with a throughput or latency graph.",
      check=["Use threads, mutexes, condition variables, atomics correctly", "Explain data race vs race condition, deadlock, false sharing", "A thread pool + queue that's clean under ThreadSanitizer"]),
 dict(n=7, title="Reading other people's code", weeks="4–6 weeks", dsa=True,
      goal="Find your way around code you didn't write, and get a change merged.",
      learn=["Build fmt, spdlog, Catch2, DuckDB or llama.cpp from source", "clangd “go to definition”", "`git log -p`, `blame`, `bisect`", "Read the tests first", "Follow CONTRIBUTING; keep PRs small"],
      skip=["Chromium, LLVM or Unreal as a first patch", "Typo-only pull requests"],
      prove="One merged pull request that fixes a real bug or adds a missing test.",
      check=["Build an open-source C++ project from source", "Get one meaningful pull request merged"]),
 dict(n=8, title="Specialise and get hired", weeks="8–12 weeks", dsa=True,
      goal="Look like a junior in one industry — not a tourist in five.",
      learn=["The extra skills for one industry", "Enough Python for scripts and tests", "Interview DSA from a known list", "Explaining your projects out loud", "The interview questions below"],
      skip=["Rust at the same time", "Certificates", "A second industry", "An unfinished engine, OS or compiler as your only project"],
      prove="One flagship project with benchmarks and a write-up you can defend for 20 minutes.",
      check=["Pick one industry and learn its extra skills", "Enough Python for build scripts and test tools", "One flagship project with benchmarks and a write-up", "~150 DSA problems in clean C++", "10 interview questions out loud + one design problem in 45 min", "One-page CV with numbers; 2–4 repos that build", "Apply by job title; ask engineers for referrals"]),
]

# Design thread + AI-agent lane, per stage. `add` = extra checklist items.
EXTRA = {
 1: dict(design="Not yet. Write small, clear functions; name things well.",
         hand="Nothing. Use AI as a tutor: “explain this error”.", keep="Every line of code. This is where understanding comes from."),
 2: dict(design="Ownership design: draw who owns what, and for how long, before you code.",
         hand="Nothing. Ask it to quiz you on lifetimes.", keep="All the code — and the sanitizer reports.",
         add=["Draw who owns what before you code"]),
 3: dict(design="Interfaces that are hard to misuse: strong types, `span`/`string_view` parameters, `[[nodiscard]]`, one error policy.",
         hand="Explaining template and concept errors.", keep="Designing the interfaces and writing the templates."),
 4: dict(design="Module boundaries: library vs app, one direction for dependencies, code you can test on its own.",
         hand="CMake, CI and boilerplate — a good first agent task.", keep="Reviewing every line it wrote.",
         add=["AGENTS.md with the build, test and sanitizer gate"]),
 5: dict(design="Data-oriented design: lay data out for how it's used.",
         hand="Explaining assembly and profiler output.", keep="Measuring. It can't benchmark your machine for you."),
 6: dict(design="Concurrency design: which thread owns which data; decide it once.",
         hand="A first draft of the thread pool.", keep="ThreadSanitizer and the review — agents write data races."),
 7: dict(design="Read how real projects draw their boundaries — and where they don't.",
         hand="A guided tour of a big codebase.", keep="Understanding what you read; writing the fix."),
 8: dict(design="Write a one-page DESIGN.md before building the flagship.",
         hand="Building the flagship from your design.", keep="The design, the review — and defending it alone, laptop closed.",
         add=["Write a one-page DESIGN.md before the flagship", "Find a lifetime or design bug in an AI-written PR"]),
}
for _s in STAGES:
    _e = EXTRA[_s["n"]]
    _s.update(design=_e["design"], hand=_e["hand"], keep=_e["keep"])
    _s["check"] = _s["check"] + _e.get("add", [])

STANDARDS = [
 ("C++17", "Most job code", "read it"),
 ("C++20", "Your default", "write it"),
 ("C++23", "Where your compiler has it", "use bits"),
 ("C++26", "Not a standard yet", "know the news"),
]

# door: 1 (very hard) .. 5 (most realistic)
JOBS = [
 ("Embedded, automotive, chips", "Firmware, drivers, car computers, chip software", "C too, RTOS, CAN/SPI/I2C, datasheets, heap-free C++", 4, "Large, steady"),
 ("Robotics and autonomy", "Sensor drivers, perception, planning, control", "ROS 2, Linux, linear algebra, Python", 3, "Growing"),
 ("Databases and infrastructure", "Storage engines, query execution, networking", "Linux I/O, concurrency, B-trees/LSM, SQL", 2, "Biggest C++ role group"),
 ("AI runtimes and inference", "llama.cpp, ONNX Runtime, TensorRT, GPU kernels", "Python bindings, SIMD, CUDA, profiling", 2, "Fastest-growing"),
 ("Simulation, HPC, CAD, EDA", "Solvers, CAD kernels, chip-design tools", "Numerical methods, MPI/OpenMP/CUDA", 3, "Growing (India semis)"),
 ("Defence and aerospace", "Vehicles, sensors, simulation, control", "Systems + embedded skills", 2, "Big in the US · citizens only"),
 ("Networking and telecom", "Routers, 5G, packet processing", "TCP/IP in depth, Linux networking, DPDK", 3, "Big in India"),
 ("Security", "Fuzzing, hardening, endpoint agents", "OS internals, sanitizers, fuzzers, assembly", 2, "Rising with regulation"),
 ("Audio and video", "Plugins, codecs, players, WebRTC", "DSP, real-time rules, FFmpeg, JUCE", 2, "Small, steady"),
 ("Games", "Unreal C++, engines, tools, rendering", "3D maths, Unreal or a graphics API", 2, "Shaky · layoffs"),
 ("Browsers", "Chromium, WebKit, Gecko, V8", "Huge codebases, security, some Rust", 1, "Flat"),
 ("Low-latency trading", "Market data, order gateways, risk", "Linux tuning, networking, maths", 1, "Few seats · top pay"),
]

TRENDS = [
 ("C++26 isn't a standard yet", "It was finished in March 2026, then the ISO ballot failed in October over Contracts. The committee is deciding the next step.", "Learn C++20. Turn on hardening. Know what reflection and Contracts are — don't study them."),
 ("Memory safety and Rust", "New security-critical code is moving to memory-safe languages. But C++ postings outnumber Rust about 6 to 1, and 58% of jobs asking for Rust also ask for C++.", "Learn C++ first. Write safe-by-default C++. Learn to read Rust once you're job-ready."),
 ("Hardening now, profiles later", "Cheap bounds checks you can switch on today (~0.3% cost at Google). Compiler-enforced “safety profiles” are aimed at C++29.", "`-D_GLIBCXX_ASSERTIONS` · libc++ hardening mode · `_MSVC_STL_HARDENING=1`"),
 ("AI agents write the code", "Agents are good inside a box — a function, a fix — and weak at deciding where the boxes go. Their C++ compiles and can still use freed memory or race. Interviews push back with in-person rounds.", "Write Stages 1–3 by hand. Then: you design, the agent types, tests and sanitizers judge, you review. Never ship code you can't explain with the laptop closed."),
]

PROJECTS = [
 ("Word counter / log analyser", "Beginner", "You finish and ship", False),
 ("Your own Vector<T>", "Beginner+", "Ownership, copy, move", False),
 ("CHIP-8 emulator", "Beginner+", "How a CPU really runs code", True),
 ("Memory allocator", "Intermediate", "Alignment, fragmentation, measuring", True),
 ("HTTP or Redis-style server", "Intermediate", "Sockets, non-blocking I/O, safe parsing", True),
 ("Thread pool + bounded queue", "Intermediate", "Concurrency that's actually correct", False),
 ("Crash-safe storage engine", "Strong", "Durability and binary formats", False),
 ("Tiny language / compiler", "Strong", "Holding a whole program in your head", True),
 ("One industry flagship", "Strong", "You fit the job you want", False),
 ("A merged pull request", "Any level", "You can read code and survive review", False),
]

QUESTIONS = [
 "What does `std::move` actually do, and what state is a moved-from object in?",
 "Explain RAII. When do you write a destructor and copy/move operations — and when none of them?",
 "Value vs `unique_ptr` vs `shared_ptr` vs `weak_ptr`: when do you use each, and what does `shared_ptr` cost?",
 "How do virtual functions work underneath? Why does a base class need a virtual destructor?",
 "What happens when `vector::push_back` runs out of capacity? What becomes invalid?",
 "`map` vs `unordered_map`: complexity, ordering, and when is the hash map slower?",
 "What is undefined behaviour? Give three examples and how you'd catch them.",
 "Two threads increment one counter. What's wrong, and what's the smallest fix?",
 "Why is looping over a `vector` much faster than over a `std::list`?",
 "Here are 30 lines that crash. Find the bug.",
 "Design it: an LRU cache, a logger, a rate limiter or a thread-safe queue — the types, who owns what, the interface.",
]

RESOURCES = [
 ("learncpp.com", "https://www.learncpp.com", "Free", "The best structured modern-C++ course"),
 ("cppreference.com", "https://en.cppreference.com", "Free", "The reference — learn to read it"),
 ("Compiler Explorer", "https://godbolt.org", "Free", "See the assembly your code becomes"),
 ("A Tour of C++, 3rd ed. — Stroustrup", None, "Book", "The shortest complete map of modern C++"),
 ("Effective Modern C++ — Meyers", None, "Book", "Move semantics, smart pointers, lambdas"),
 ("A Philosophy of Software Design — Ousterhout", None, "Book", "Short; the best book on keeping design simple"),
 ("C++ Software Design — Iglberger", None, "Book", "Design in modern C++ terms, for Stages 3–8"),
 ("C++ Concurrency in Action — Williams", None, "Book", "For Stage 6"),
 ("Computer Systems: A Programmer's Perspective", "https://csapp.cs.cmu.edu/", "Book · free labs", "For Stage 5"),
 ("CppCon “Back to Basics” + C++ Weekly", "https://www.youtube.com/@CppCon", "Free", "One-hour talks on each core topic"),
 ("An Introduction to Modern CMake", "https://cliutils.gitlab.io/modern-cmake/", "Free", "CMake without the 2005 habits"),
 ("Beej's Guide to Network Programming", "https://beej.us/guide/bgnet/", "Free", "Sockets, for Stage 5"),
]

TOTAL_CHECKS = sum(len(s["check"]) for s in STAGES)

# ---------------------------------------------------------------- shared bits
CSS_TOKENS = """
"""

def door_meter(n):
    return '<span class="door" aria-label="junior door %d of 5">%s</span>' % (
        n, "".join('<i class="%s"></i>' % ("on" if i < n else "") for i in range(5)))

# ---------------------------------------------------------------- web page
def web():
    stages = []
    for s in STAGES:
        learn = "".join(f"<li>{t(x)}</li>" for x in s["learn"])
        skip = "".join(f"<li>{t(x)}</li>" for x in s["skip"])
        checks = "".join(
            f'<li><label><input type="checkbox" data-id="s{s["n"]}-{i}"><span>{t(c)}</span></label></li>'
            for i, c in enumerate(s["check"]))
        dsa = '<span class="dsa-tag" title="Data structures and algorithms practice runs alongside from Stage 3">+ DSA 2–3/wk</span>' if s.get("dsa") else ""
        stages.append(f"""
<li class="stage" id="stage-{s['n']}">
  <div class="node" aria-hidden="true"><span>{s['n']:02d}</span></div>
  <article class="card">
    <header>
      <p class="kicker">Stage {s['n']}, {t(s['weeks'])} {dsa}</p>
      <h3>{t(s['title'])}</h3>
      <p class="goal">{t(s['goal'])}</p>
    </header>
    <div class="cols">
      <div><h4>Learn</h4><ul class="learn">{learn}</ul></div>
      <div><h4>Skip for now</h4><ul class="skip">{skip}</ul></div>
    </div>
  </article>
  <aside class="spec">
    <p class="kicker">Fig. {s['n']}: prove it</p>
    <p class="prove">{t(s['prove'])}</p>
    <div class="design"><h4>Design</h4><p>{t(s['design'])}</p></div>
    <div class="ai"><h4>With an AI agent</h4><p><b class="hand">Hand off</b> {t(s['hand'])}</p><p><b class="keep">Keep</b> {t(s['keep'])}</p></div>
    <div class="checks"><h4>Checklist <span class="count" data-stage="{s['n']}">0/{len(s['check'])}</span></h4><ul>{checks}</ul></div>
  </aside>
</li>""")

    std = "".join(f'<li class="std std-{i}"><b>{a}</b><span>{b}</span><em>{c}</em></li>' for i, (a, b, c) in enumerate(STANDARDS))
    jobs = "".join(f"""
<li class="job"><h3>{t(n)}</h3><p>{t(w)}</p><p class="extra"><b>Extra:</b> {t(x)}</p>
<div class="meta"><span class="lbl">Junior door</span>{door_meter(d)}<span class="sig">{t(sig)}</span></div></li>""" for n, w, x, d, sig in JOBS)
    trends = "".join(f'<li class="trend"><p class="kicker">Trend {i+1}</p><h3>{t(a)}</h3><p>{t(b)}</p><p class="todo"><b>Do:</b> {t(c)}</p></li>' for i, (a, b, c) in enumerate(TRENDS))
    film = f'<a class="film" href="{YT}/playlists" title="There is a Morebyt build series for this">Morebyt series</a>'
    projects = "".join(
        f'<li class="proj"><span class="lvl">{t(l)}</span><b>{t(n)}</b><span class="why">{t(w)}</span>{film if f else ""}</li>'
        for n, l, w, f in PROJECTS)
    qs = "".join(f"<li>{t(q)}</li>" for q in QUESTIONS)
    res = "".join(
        (f'<li><a href="{u}" rel="noopener">{t(n)}</a>' if u else f"<li><span class=nm>{t(n)}</span>")
        + f' <span class="tag">{t(k)}</span><span class="why">{t(w)}</span></li>' for n, u, k, w in RESOURCES)

    signup = site.signup("email", button="Send me the PDF", label="Your email",
                         fine="Free. The one-page printable checklist, plus an email when the roadmap changes. Unsubscribe any time.")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{site.THEME_HEAD_JS}
<title>C++ Roadmap 2027: Morebyt</title>
<meta name="description" content="A free C++ roadmap for 2027: what to learn, in order, what to skip, and where the C++ jobs actually are. From a working C++ engineer.">
<meta property="og:title" content="C++ Roadmap 2027: what to learn, what to skip, where the jobs are">
<meta property="og:description" content="8 stages, 10 projects, 12 industries and the interview questions — free, from Morebyt.">
<meta property="og:type" content="article">
<meta property="og:url" content="https://morebyt.com/roadmap/">
<link rel="canonical" href="https://morebyt.com/roadmap/">
<meta name="theme-color" content="#F5F7F9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E151C" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{site.FONTS}">
<link rel="stylesheet" href="/assets/site.css">
<style>
{CSS_TOKENS}
html{{scroll-behavior:smooth}}
code{{font:.86em var(--mono);background:var(--paper);border:1px solid var(--rule);border-radius:4px;padding:0 .3em;white-space:nowrap}}
.kicker{{font:500 14px/1.4 var(--mono);color:var(--ink-2);margin:0 0 8px}}

.lede{{color:var(--ink-2);max-width:62ch;margin:0 0 28px}}
section{{padding:72px 0 8px}}

.brand{{font-weight:700;font-size:20px;text-decoration:none;letter-spacing:.02em}}
.top nav a{{font:13px var(--mono);margin-left:18px;color:var(--ink-2);text-decoration:none}}
.top nav a:hover{{color:var(--ink)}}

/* hero */
.hero{{display:grid;grid-template-columns:1.25fr .9fr;gap:40px;align-items:center;padding:64px 0 24px}}
.hero h1{{font-size:clamp(40px,7vw,76px)}}
.hero h1 span{{display:block;font:500 clamp(18px,2.4vw,24px)/1.35 var(--serif);color:var(--ink-2);letter-spacing:0;margin-top:14px}}
.byline{{font:15px var(--mono);color:var(--ink-2);margin:18px 0 0}}
.box{{border:1.5px solid var(--rule-2);background:var(--sheet);border-radius:6px;padding:22px;position:relative}}
.box::before,.box::after{{content:"";position:absolute;width:12px;height:12px;border:2px solid var(--line)}}
.box::before{{top:-2px;left:-2px;border-right:0;border-bottom:0}}
.box::after{{bottom:-2px;right:-2px;border-left:0;border-top:0}}
.box h2{{font-size:22px;margin-bottom:4px}}
.box > p{{color:var(--ink-2);margin:0 0 14px;font-size:15px}}

/* tl;dr */
.tldr{{border-left:3px solid var(--amber);padding:6px 0 6px 18px;font-size:clamp(18px,2.2vw,21px);max-width:70ch;margin:24px 0 0}}

/* standards bar */
.stds{{list-style:none;padding:0;margin:28px 0 0;display:grid;grid-template-columns:repeat(4,1fr);border:1.5px solid var(--rule-2);border-radius:6px;overflow:hidden}}
.std{{padding:16px;border-right:1px solid var(--rule)}}
.std:last-child{{border-right:0}}
.std b{{display:block;font:700 24px var(--mono)}}
.std span{{display:block;color:var(--ink-2);font-size:14px}}
.std em{{display:inline-block;margin-top:8px;font:600 12px var(--mono);font-style:normal;padding:3px 7px;border-radius:3px;border:1px solid var(--rule-2)}}
.std-1{{background:color-mix(in srgb,var(--amber) 16%,transparent)}} .std-1 em{{background:var(--amber);color:var(--on-amber);border-color:var(--amber)}}
.std-3{{opacity:.62}} .std-3 b{{text-decoration:line-through;text-decoration-thickness:2px}}

/* progress */
.progress{{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--paper) 92%,transparent);backdrop-filter:blur(6px);border-bottom:1px solid var(--rule);}}
.progress .wrap{{display:flex;gap:14px;align-items:center;padding-top:10px;padding-bottom:10px;font:13px var(--mono);color:var(--ink-2)}}
.bar{{flex:1;height:8px;border:1px solid var(--rule-2);border-radius:5px;overflow:hidden}}
.bar i{{display:block;height:100%;width:0;background:var(--good);transition:width .3s}}
.progress button{{font:12px var(--mono);background:none;border:1px solid var(--rule-2);color:var(--ink-2);border-radius:3px;padding:3px 8px;cursor:pointer}}

/* the map */
.map{{list-style:none;padding:0;margin:8px 0 0;position:relative}}
.map::before{{content:"";position:absolute;left:50%;top:0;bottom:0;border-left:2px dashed var(--rule-2)}}
.stage{{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:72px;margin:0 0 28px}}
.stage .node{{position:absolute;left:50%;top:22px;transform:translateX(-50%);width:56px;height:56px;border-radius:50%;
  background:var(--paper);border:2px solid var(--ink);display:grid;place-items:center;font:700 18px var(--mono);z-index:1}}
.stage:nth-child(odd) .card{{grid-column:1;grid-row:1}}
.stage:nth-child(even) .card{{grid-column:2;grid-row:1}}
.stage:nth-child(odd) .spec{{grid-column:2;grid-row:1}}
.stage:nth-child(even) .spec{{grid-column:1;grid-row:1}}
.spec{{align-self:start;margin-top:22px;border:1.5px dashed var(--rule-2);border-radius:6px;padding:16px 18px;background:var(--sheet)}}
.spec .prove{{margin:0 0 12px;font-size:15.5px}}
.design,.ai{{border-top:1px dashed var(--rule);padding:10px 0 8px}}
.design p,.ai p{{margin:0 0 4px;font-size:14.5px;color:var(--ink-2)}}
.ai b{{display:inline-block;min-width:68px;font:600 12px var(--mono);padding:2px 6px;border-radius:3px;margin-right:6px}}
.ai .hand{{color:var(--good);background:color-mix(in srgb,var(--good) 14%,transparent)}}
.ai .keep{{color:var(--ink);background:color-mix(in srgb,var(--amber) 30%,transparent)}}
.flow{{list-style:none;padding:0;margin:8px 0 0;display:grid;grid-template-columns:repeat(4,1fr);gap:0;counter-reset:f}}
.flow li{{position:relative;border:1.5px solid var(--rule-2);border-right:0;padding:18px 18px 16px;background:var(--sheet)}}
.flow li:last-child{{border-right:1.5px solid var(--rule-2)}}
.flow li:not(:last-child)::after{{content:"";position:absolute;right:-11px;top:50%;width:20px;height:20px;transform:translateY(-50%) rotate(45deg);border-top:1.5px solid var(--rule-2);border-right:1.5px solid var(--rule-2);background:var(--paper);z-index:1}}
.flow b{{display:block;font:600 14px var(--mono);color:var(--line);margin-bottom:4px}}
.flow h3{{font-size:19px;margin-bottom:6px}}
.flow p{{margin:0;font-size:14.5px;color:var(--ink-2)}}
.spec ul{{margin:0;padding:0;list-style:none;font-size:14.5px}}
.spec li{{padding:3px 0}}
.card{{border:1.5px solid var(--rule-2);background:var(--sheet);border-radius:6px;padding:22px 22px 14px;position:relative}}
.stage:nth-child(odd) .card::after,.stage:nth-child(even) .card::after{{content:"";position:absolute;top:49px;width:44px;border-top:2px solid var(--rule-2)}}
.stage:nth-child(odd) .card::after{{right:-46px}}
.stage:nth-child(even) .card::after{{left:-46px}}
.card h3{{font-size:25px}}
.goal{{color:var(--ink-2);margin:6px 0 14px}}
.dsa-tag{{display:inline-block;white-space:nowrap;margin:2px 0 0 8px;color:var(--good);border:1px solid var(--good);border-radius:3px;padding:1px 6px;letter-spacing:.06em}}
.cols{{display:grid;grid-template-columns:1.3fr 1fr;gap:18px}}
h4{{font:600 14px var(--mono);color:var(--ink-2);margin:0 0 6px}}
.card ul{{margin:0;padding:0;list-style:none;font-size:15px}}
.card li{{padding:3px 0 3px 16px;position:relative}}
.learn li::before{{content:"+";position:absolute;left:0;color:var(--good);font-family:var(--mono)}}
.skip li{{color:var(--ink-2)}}
.skip li::before{{content:"×";position:absolute;left:0;color:var(--warn);font-family:var(--mono)}}
.checks{{border-top:1px dashed var(--rule);padding-top:10px}}
.count{{margin-left:6px;color:var(--good);letter-spacing:0}}
.checks label{{display:flex;gap:10px;align-items:flex-start;cursor:pointer}}
.checks li{{padding-left:0}}
.checks input{{margin-top:5px;accent-color:var(--good);width:16px;height:16px;flex:none}}
.checks input:checked + span{{color:var(--ink-2);text-decoration:line-through}}

/* jobs */
.jobs,.trends,.projs{{list-style:none;padding:0;margin:0;display:grid;gap:14px}}
.jobs{{grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}}
.job,.trend{{border:1px solid var(--rule-2);border-radius:6px;padding:16px;background:var(--sheet)}}
.job h3{{font-size:19px;margin-bottom:6px}}
.job p{{margin:0 0 6px;font-size:14.5px;color:var(--ink-2)}}
.job .extra b{{color:var(--ink)}}
.meta{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:10px;font:12px var(--mono);color:var(--ink-2)}}
.door{{display:inline-flex;gap:3px}}
.door i{{width:14px;height:8px;border:1px solid var(--rule-2);border-radius:2px}}
.door i.on{{background:var(--good);border-color:var(--good)}}
.sig{{margin-left:auto;color:var(--line)}}
.note{{font-size:13px;color:var(--ink-2);margin:14px 0 0;max-width:80ch}}

.trends{{grid-template-columns:repeat(auto-fill,minmax(250px,1fr))}}
.trend h3{{font-size:20px;margin-bottom:8px}}
.trend p{{font-size:14.5px;color:var(--ink-2);margin:0 0 10px}}
.trend .todo{{color:var(--ink);border-top:1px dashed var(--rule-2);padding-top:10px;margin:0}}

.projs{{grid-template-columns:1fr}}
.proj{{display:grid;grid-template-columns:120px 1fr 1.2fr auto;gap:14px;align-items:center;padding:12px 14px;border:1px solid var(--rule);border-radius:5px;background:var(--sheet)}}
.proj .lvl{{font:500 13px var(--mono);color:var(--ink-2)}}
.proj b{{font-size:17px}}
.proj .why{{color:var(--ink-2);font-size:14.5px}}
.film{{font:600 12px var(--mono);color:var(--on-amber);background:var(--amber);padding:4px 8px;border-radius:3px;text-decoration:none;white-space:nowrap}}

.qs{{margin:0;padding-left:1.4em;columns:2;column-gap:40px}}
.qs li{{break-inside:avoid;margin:0 0 12px;font-size:15.5px}}
.qs li::marker{{font-family:var(--mono);color:var(--ink-2)}}

.res{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:1fr 1fr;gap:0 40px}}
.res li{{padding:10px 0;border-bottom:1px dashed var(--rule);font-size:15.5px}}
.res .tag{{font:11px var(--mono);border:1px solid var(--rule-2);border-radius:3px;padding:1px 6px;margin-left:6px;color:var(--ink-2)}}
.res .why{{display:block;color:var(--ink-2);font-size:14px}}

.end{{margin:72px 0 0;padding:28px;display:grid;grid-template-columns:1.2fr 1fr;gap:28px;align-items:center}}

@media (max-width:860px){{
  .hero,.end{{grid-template-columns:1fr}}
  .stds{{grid-template-columns:1fr 1fr}}
  .std:nth-child(2){{border-right:0}} .std:nth-child(-n+2){{border-bottom:1px solid var(--rule)}}
  .map::before{{left:19px}}
  .stage{{grid-template-columns:1fr;gap:0;padding-left:52px}}
  .stage .node{{left:19px;top:16px;width:38px;height:38px;font-size:14px}}
  .card{{padding:18px 16px 12px}} .card h3{{font-size:22px}}
  .stage:nth-child(odd) .card,.stage:nth-child(even) .card{{grid-column:1;grid-row:1}}
  .stage:nth-child(odd) .spec,.stage:nth-child(even) .spec{{grid-column:1;grid-row:2;margin-top:10px}}
  .stage:nth-child(odd) .card::after,.stage:nth-child(even) .card::after{{left:-16px;right:auto;width:14px;top:35px}}
  .cols{{grid-template-columns:1fr}}
  .flow{{grid-template-columns:1fr}}
  .flow li{{border-right:1.5px solid var(--rule-2);border-bottom:0}}
  .flow li:last-child{{border-bottom:1.5px solid var(--rule-2)}}
  .flow li:not(:last-child)::after{{right:auto;left:50%;top:auto;bottom:-11px;transform:translateX(-50%) rotate(135deg)}}
  .card,.spec{{min-width:0}}
  code{{white-space:normal;overflow-wrap:anywhere}}
  .proj{{grid-template-columns:1fr;gap:4px}}
  .qs{{columns:1}}
  .res{{grid-template-columns:1fr}}
}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}} .bar i{{transition:none}}}}
</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
{site.header("/roadmap")}
<main id="main">
<div class="wrap">

  <div class="hero">
    <div>
      <p class="kicker">Free, updated {UPDATED}</p>
      <h1>C++ Roadmap 2027<span>What to learn, in order. What to skip. Where the jobs actually are.</span></h1>
      <p class="byline">By Mohammad Reza Bayat, C++ engineer. Videos at <a href="{YT}">youtube.com/@morebyt</a></p>
    </div>
    <div class="box" id="get">
      <h2>Get the 1-page checklist</h2>
      <p>All {TOTAL_CHECKS} steps on one printable page — tick them off as you go.</p>
      {signup}
    </div>
  </div>

  <p class="tldr">Learn C++ the way companies use it. Spend your time on <b>object lifetime, tools and how the machine works</b> — not syntax. Build <b>a few finished projects</b> a stranger can clone and build. Pick <b>one industry</b>. Let AI agents type, but <b>you</b> own the design and the review — an agent can't tell you who owns the memory. That's what the interview is about.</p>

  <ul class="stds" aria-label="Which C++ standard to learn">{std}</ul>
</div>

<div class="progress" aria-live="polite">
  <div class="wrap"><span>Your progress</span><div class="bar"><i id="bar"></i></div><span id="done">0 / {TOTAL_CHECKS}</span><button id="reset" type="button">reset</button></div>
</div>

<div class="wrap">
  <section id="agents">
    <p class="kicker">Sheet 0: how to work in 2027</p>
    <h2>You design. The agent types. The tests judge.</h2>
    <p class="lede">AI agents now write much of the code. They're good inside a box and weak at deciding where the boxes go — and their C++ compiles even when it uses freed memory. So the junior skill of 2027 is design and review. Stages 1–3: write everything by hand. From Stage 4 on, work like this:</p>
    <ol class="flow">
      <li><b>1. You</b><h3>Design</h3><p>A one-page DESIGN.md: the types, who owns what, the interfaces, how errors and threads work.</p></li>
      <li><b>2. Agent</b><h3>Build</h3><p>The agent writes code inside your design, following your AGENTS.md.</p></li>
      <li><b>3. Tools</b><h3>Gate</h3><p>Tests, warnings, sanitizers and CI must pass. No exceptions.</p></li>
      <li><b>4. You</b><h3>Review</h3><p>Read every line. Find where it left the design. Explain it with the laptop closed.</p></li>
    </ol>
  </section>

  <section id="map">
    <p class="kicker">Sheet 1: the map</p>
    <h2>8 stages, about 10–14 months</h2>
    <p class="lede">At about 10 hours a week, if you can already program (6–9 months if you code for a living). Start data-structures-and-algorithms practice at Stage 3 and keep it going. Tick items as you go — your progress stays in this browser.</p>
    <ol class="map">{''.join(stages)}</ol>
  </section>

  <section id="jobs">
    <p class="kicker">Sheet 2: where the jobs are</p>
    <h2>The seats aren't where the hype is</h2>
    <p class="lede">Trading and game engines get the attention. The job ads say the seats are in embedded, robotics, chips, infrastructure and AI runtimes. Pick one of these and learn its extra skills.</p>
    <ul class="jobs">{jobs}</ul>
    <p class="note">Junior door = how realistic it is to get in as a junior (my judgment). Signals from job-ad snapshots, Nov 2026: 37,046 live postings required C++ vs about 6,000 for Rust (Alion); C++ is #4 on TIOBE (8.35%). Python is also required in 60% of C++ postings — learn enough of it.</p>
  </section>

  <section id="trends">
    <p class="kicker">Sheet 3: what's changing</p>
    <h2>4 things a 2027 learner must know</h2>
    <ul class="trends">{trends}</ul>
  </section>

  <section id="projects">
    <p class="kicker">Sheet 4: projects that get you hired</p>
    <h2>Five finished beats eight abandoned</h2>
    <p class="lede">Every project: builds in one command, has tests, runs sanitizers in CI, and has one measured number in the README. Skip to-do apps and tutorial clones.</p>
    <ul class="projs">{projects}</ul>
  </section>

  <section id="interview">
    <p class="kicker">Sheet 5: the interview</p>
    <h2>10 questions and one design problem</h2>
    <ol class="qs">{qs}</ol>
    <p class="note">Search job titles, not “C++ developer”: embedded or firmware engineer, systems software engineer, graduate software engineer, robotics software engineer. Internships beat certificates. Never write “C/C++” on your CV.</p>
  </section>

  <section id="resources">
    <p class="kicker">Sheet 6: resources</p>
    <h2>The short list</h2>
    <ul class="res">{res}</ul>
  </section>

  <div class="box end">
    <div><h2>Take the checklist with you</h2><p style="color:var(--ink-2);margin:0">One printable page, all {TOTAL_CHECKS} steps. You'll also get an email when the roadmap changes — for example when C++26 is finally settled.</p></div>
    {site.signup("email2", button="Send me the PDF", fine="Free. Unsubscribe any time.")}
  </div>


</div>
</main>

<script>
(function(){{
  var KEY='morebyt-roadmap-2027', state={{}};
  try{{ state=JSON.parse(localStorage.getItem(KEY)||'{{}}')||{{}}; }}catch(e){{ state={{}}; }}
  var boxes=[].slice.call(document.querySelectorAll('.checks input'));
  function save(){{ try{{ localStorage.setItem(KEY, JSON.stringify(state)); }}catch(e){{}} }}
  function render(){{
    var done=0;
    boxes.forEach(function(b){{ b.checked=!!state[b.dataset.id]; if(b.checked) done++; }});
    document.getElementById('done').textContent=done+' / '+boxes.length;
    document.getElementById('bar').style.width=(100*done/boxes.length)+'%';
    [].forEach.call(document.querySelectorAll('.count'),function(c){{
      var n=c.dataset.stage, all=document.querySelectorAll('input[data-id^="s'+n+'-"]'), k=0;
      [].forEach.call(all,function(b){{ if(b.checked) k++; }});
      c.textContent=k+'/'+all.length;
    }});
  }}
  boxes.forEach(function(b){{ b.addEventListener('change',function(){{ state[b.dataset.id]=b.checked; save(); render(); }}); }});
  document.getElementById('reset').addEventListener('click',function(){{ state={{}}; save(); render(); }});
  render();
}})();
</script>
""" + site.footer()

# ---------------------------------------------------------------- printable checklist (PDF)
def printable():
    blocks = []
    for s in STAGES:
        items = "".join(f"<li>{t(c)}</li>" for c in s["check"])
        blocks.append(f"""<div class="blk"><div class="hd"><span class="no">{s['n']:02d}</span><b>{t(s['title'])}</b><em>{t(s['weeks'])}</em></div><ul>{items}</ul></div>""")
    std = "".join(f'<li class="s{i}"><b>{a}</b> {b}</li>' for i, (a, b, c) in enumerate(STANDARDS))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>C++ Roadmap 2027 — Checklist · Morebyt</title>
<style>
@page{{size:A4;margin:0}}
:root{{--ink:#0f3d73;--ink-2:#3a5f8f;--grid:rgba(15,61,115,.08);--grid-2:rgba(15,61,115,.16);--accent:#e8a400;
  --sans:"Avenir Next","Avenir","Segoe UI",system-ui,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}}
*{{box-sizing:border-box}}
html,body{{margin:0;width:210mm;height:297mm}}
body{{color:var(--ink);font:8.3pt/1.24 var(--sans);background:#fff;
  background-image:linear-gradient(var(--grid-2) .6px,transparent .6px),linear-gradient(90deg,var(--grid-2) .6px,transparent .6px),
  linear-gradient(var(--grid) .4px,transparent .4px),linear-gradient(90deg,var(--grid) .4px,transparent .4px);
  background-size:20mm 20mm,20mm 20mm,4mm 4mm,4mm 4mm;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}}
.sheet{{position:absolute;inset:9mm;border:1.4pt solid var(--ink);padding:7mm 7mm 5mm;display:flex;flex-direction:column}}
.sheet::before{{content:"";position:absolute;inset:1.6mm;border:.5pt solid var(--ink);pointer-events:none}}
header{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1pt solid var(--ink);padding-bottom:4mm}}
h1{{margin:0;font-size:27pt;line-height:1;letter-spacing:-.01em}}
.sub{{margin:1.6mm 0 0;font-size:10pt;color:var(--ink-2)}}
.mono{{font:7.4pt var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-2)}}
.right{{text-align:right}}
.right{{white-space:nowrap}} .right b{{display:block;font-size:11pt;letter-spacing:.02em;margin-bottom:.6mm}}
.stds{{list-style:none;margin:3.5mm 0 0;padding:0;display:grid;grid-template-columns:repeat(4,1fr);border:.8pt solid var(--ink)}}
.stds li{{padding:1.3mm 2.4mm;border-right:.6pt solid var(--ink);font-size:8.2pt;color:var(--ink-2)}}
.stds li:last-child{{border-right:0}}
.stds b{{font:700 10.5pt var(--mono);color:var(--ink);margin-right:1mm}}
.stds .s1{{background:rgba(232,164,0,.18)}}
.stds .s3 b{{text-decoration:line-through}}
.grid{{column-count:2;column-gap:5mm;margin-top:3.6mm;padding-bottom:3mm}}
.blk{{break-inside:avoid;background:rgba(255,255,255,.9);border:.8pt solid var(--ink);padding:1.7mm 2.6mm 1.3mm;margin:0 0 2.6mm}}
.hd{{display:flex;align-items:center;gap:2mm;border-bottom:.5pt dashed var(--ink-2);padding-bottom:1.4mm;margin-bottom:1.2mm}}
.no{{font:700 8.5pt var(--mono);width:6.6mm;height:6.6mm;border:1pt solid var(--ink);border-radius:50%;display:grid;place-items:center;flex:none}}
.hd b{{font-size:9.8pt}}
.hd em{{margin-left:auto;font:normal 7.2pt var(--mono);color:var(--ink-2);white-space:nowrap}}
ul.ck{{}}
.blk ul{{list-style:none;margin:0;padding:0}}
.blk li{{position:relative;padding:.35mm 0 .35mm 5mm}}
.blk li::before{{content:"";position:absolute;left:0;top:.9mm;width:2.8mm;height:2.8mm;border:.8pt solid var(--ink);border-radius:.6mm;background:#fff}}
code{{font:7.6pt var(--mono)}}
.rules{{margin-top:auto;display:grid;grid-template-columns:repeat(4,1fr);border:.8pt solid var(--ink);background:rgba(255,255,255,.88)}}
.rules div{{padding:1.6mm 2.4mm;border-right:.6pt solid var(--ink);font-size:7.8pt}}
.rules div:last-child{{border-right:0}}
.rules b{{display:block;font:700 7.2pt var(--mono);letter-spacing:.1em;text-transform:uppercase;margin-bottom:.6mm}}
.tb{{margin-top:3mm;display:grid;grid-template-columns:1.5fr 1fr 1fr .8fr;border:.8pt solid var(--ink);background:#fff}}
.tb div{{padding:1.6mm 2.4mm;border-right:.6pt solid var(--ink)}}
.tb div:last-child{{border-right:0}}
.tb span{{display:block;font:6.4pt var(--mono);letter-spacing:.12em;color:var(--ink-2)}}
.tb b{{font-size:9pt}}
</style></head>
<body><div class="sheet">
<header>
  <div><div class="mono">Morebyt · Build it to understand it</div><h1>C++ Roadmap 2027</h1><p class="sub">What to learn, in order. Tick a box when you can do it without a tutorial.</p></div>
  <div class="right mono"><b>{TOTAL_CHECKS} steps · 10–14 months</b>at ~10 hours a week<br>+ DSA practice from stage 3</div>
</header>
<ul class="stds">{std}</ul>
<div class="grid">{''.join(blocks)}</div>
<div class="rules">
  <div><b>Every project</b>Builds in one command, has tests, sanitizers in CI, one measured number.</div>
  <div><b>Pick one lane</b>Embedded, robotics, infrastructure, AI runtimes, simulation — not five.</div>
  <div><b>Search titles</b>Firmware, embedded, systems software, graduate engineer.</div>
  <div><b>Agent rule</b>You design, the agent types, tests judge. Never ship what you can't explain.</div>
</div>
<div class="tb">
  <div><span>FULL ROADMAP, JOBS AND PROJECTS</span><b>morebyt.com/roadmap</b></div>
  <div><span>VIDEOS</span><b>youtube.com/@morebyt</b></div>
  <div><span>DRAWN BY</span><b>Mohammad Reza Bayat</b></div>
  <div><span>REV</span><b>{UPDATED}</b></div>
</div>
</div></body></html>"""

if __name__ == "__main__":
    out = HERE / "public" / "roadmap"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(web(), encoding="utf-8")
    (HERE / "pdf" / "print.html").write_text(printable(), encoding="utf-8")
    print("built", out / "index.html", HERE / "pdf" / "print.html", "checks:", TOTAL_CHECKS)
