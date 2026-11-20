---
title: 27 projects every senior engineer should build once
description: Twenty-seven hard projects, from an OS kernel and a compiler to a TCP/IP stack and a ray tracer, with what each one teaches you and where to start.
date: 2025-09-27
updated: 2026-11-20
tags: projects, systems programming, career
---

After a few years in the job, most of us know our own stack well and everything under it only vaguely. We call the database, the network and the compiler, but we have never had to build one. The fastest way I know to fix that is to build a small, bad version of the thing yourself. You won't ship it. You will understand the real one much better afterwards.

Here are 27 projects I'd recommend, three per area. None of them is a weekend job. Each one puts you in front of problems a CRUD app never shows you. For each I've noted what it teaches and a good place to start. Many people collect similar lists; the [build-your-own-x](https://github.com/codecrafters-io/build-your-own-x) repository is the biggest, with tutorials for most of these.

If you're earlier in your career and want projects that get you hired, the [C++ Roadmap 2027](/roadmap/#projects) has a shorter list aimed at that.

## Operating systems and storage

1. **An operating system kernel.** A bootloader, a memory manager and a scheduler that switches between two processes. You learn what the CPU actually does when it boots, how virtual memory works, and why a bad pointer in kernel code takes the whole machine down. Start with the [OSDev wiki](https://wiki.osdev.org/) and MIT's teaching kernel [xv6](https://pdos.csail.mit.edu/6.828/2024/xv6.html). I'm building a tiny OS on [the Morebyt channel](https://www.youtube.com/@morebyt) from February 2027.

2. **A database engine.** A B-tree on disk, a simple query parser and transactions. After this you will never forget an index again, because you will have felt what a full table scan costs. The [Let's Build a Simple Database](https://cstack.github.io/db_tutorial/) tutorial gets you to a working SQLite clone.

3. **A web server.** Parse HTTP requests, serve files, handle many connections at once. The interesting part is concurrency: threads first, then an event loop with `epoll` or `kqueue`, and measuring the difference. [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112) is the HTTP/1.1 spec you'll be reading.

## Compilers and languages

4. **A compiler for a small language.** Tokens, a parser, a syntax tree and code generation, even if the target is just C or a simple assembly. You stop seeing compiler errors as noise and start seeing the stage that produced them. Robert Nystrom's [Crafting Interpreters](https://craftinginterpreters.com/) is the best free guide I know. A compiler series is on the Morebyt plan for August 2027.

5. **A virtual machine.** Run the bytecode your compiler emits, on a stack machine or a register machine. You'll see why the JVM and Python's interpreter are designed the way they are. The second half of Crafting Interpreters builds exactly this.

6. **A regex engine.** Turn a pattern into an automaton and match strings with it. Russ Cox's article [Regular Expression Matching Can Be Simple And Fast](https://swtch.com/~rsc/regexp/regexp1.html) explains why the backtracking approach most languages use can take exponential time, and how to avoid it.

## Algorithms, search and games

7. **A chess engine.** Move generation, minimax with alpha-beta pruning, then a transposition table. Getting move generation completely correct is harder than it sounds and teaches you to test against known positions. The [Chess Programming Wiki](https://www.chessprogramming.org/) covers every technique.

8. **A small search engine.** Crawl a set of pages, build an inverted index and rank results with TF-IDF or BM25. The free book [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/) explains both.

9. **A reinforcement learning agent for Snake or Tetris.** Write the game, then an agent that learns to play it. Expect to spend more time on the reward function than on the learning code. Sutton and Barto's [Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book.html) is free online.

## Networking and distributed systems

10. **A distributed key-value store with Raft.** Three nodes that agree on the same data even when one dies. It teaches you what "the network is unreliable" means in practice. Read the [Raft paper and visualisation](https://raft.github.io/) first.

11. **A BitTorrent client.** Talk to a tracker, connect to peers, download pieces in parallel and check their hashes. The original protocol, [BEP 3](https://www.bittorrent.org/beps/bep_0003.html), is short enough to read in an evening.

12. **A TCP/IP stack.** Handle Ethernet frames, IP and TCP yourself on a TUN/TAP device. You'll implement the handshake, retransmission and windows, and ordinary network bugs will start to make sense. The current TCP spec is [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293).

## Graphics and media

13. **A video player.** Demux a file, decode the frames with a library like FFmpeg's libav, and keep audio and video in sync. The sync is the hard part, and it's where you learn how much timing work a player does for you.

14. **A ray tracer.** Shoot rays, bounce them off spheres, get a picture. For the effort it takes, it's the most satisfying project on this list. [Ray Tracing in One Weekend](https://raytracing.github.io/) takes you from nothing to soft shadows and glass.

15. **A small game engine.** A game loop, rendering, input and simple physics. You'll learn about fixed time steps and why engines separate the update rate from the frame rate. Jason Gregory's book *Game Engine Architecture* is the standard reference.

## Security and cryptography

16. **A TLS 1.3 handshake.** Implement the handshake against a real server, using an existing library for the cryptographic primitives. You learn what the padlock in your browser actually checks. The spec is [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446). Treat this as a learning project only; never use home-made TLS for real traffic.

17. **A toy blockchain.** Blocks, hashes, proof of work and a few nodes that agree on the longest chain. It's a compact way to learn about hashing, Merkle trees and consensus. Start with the [Bitcoin paper](https://bitcoin.org/bitcoin.pdf), which is nine pages long.

18. **A password manager.** An encrypted vault, a key derived from a master password, and safe handling of secrets in memory. Use a vetted library such as [libsodium](https://doc.libsodium.org/) and a slow key-derivation function like Argon2; the lesson is in using cryptography correctly, not inventing it.

## Developer tools

19. **A version control system.** Blobs, trees, commits and branches stored the way Git stores them. Once you've written it, Git's odd commands suddenly have obvious meanings. [Write yourself a Git](https://wyag.thb.lt/) walks through it in Python, and it's easy to follow in C++.

20. **A code formatter or linter.** Parse real source code into a syntax tree and print it back out, or walk the tree looking for patterns. You'll find out how much of a language's grammar you never had to think about.

21. **A debugger.** Start a process, set a breakpoint by writing a trap instruction into its memory, read registers and step through code. Sy Brand's [Writing a Linux Debugger](https://blog.tartanllama.xyz/writing-a-linux-debugger-setup/) series shows how `ptrace` makes this possible.

## Data systems

22. **A recommendation engine.** Collaborative filtering on a public ratings dataset, then a look at why the results are so often obvious. The data handling teaches as much as the maths.

23. **A real-time analytics pipeline.** Events in, aggregates out, a dashboard that updates every second. You'll meet back-pressure, late events and windows, the same problems Kafka and stream processors solve.

24. **A time-series database.** Store metrics compactly and query them by time range. Facebook's [Gorilla paper](https://www.vldb.org/pvldb/vol8/p1816-teller.pdf) describes the compression tricks that make this work.

## Classic challenges

25. **An emulator.** CHIP-8 first, then a Game Boy or NES if you get hooked. You write a CPU, memory, a screen and a keyboard in software, which is about the most direct way to learn how a computer runs a program. I filmed a [complete CHIP-8 emulator in C++](https://www.youtube.com/playlist?list=PLd0lXMskqFUU), one part per episode.

26. **A Doom-style raycaster.** The 2.5D trick behind Wolfenstein 3D: cast one ray per screen column and draw a wall slice. [Lode's raycasting tutorial](https://lodev.org/cgtutor/raycasting.html) gets you to textured walls quickly.

27. **A fluid simulation.** Smoke or water on a grid. The maths looks frightening, but Jos Stam's paper *Real-Time Fluid Dynamics for Games* (2003) reduces it to a few short functions, and the results look great.

## Where to start

Pick the one that matches the layer you understand least. If databases feel like magic, build the database. If you've never wondered how your program reaches the CPU, start with the emulator, because it's the smallest project here that still covers a whole machine.

Keep the first version small and finish it. A working toy teaches more than an ambitious design that stops halfway, and it gives you something real to talk about in your next interview.
