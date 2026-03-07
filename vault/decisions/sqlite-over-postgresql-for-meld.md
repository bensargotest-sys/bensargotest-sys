---
title: SQLite over PostgreSQL for MELD
date: '2026-02-22'
---
Chose SQLite for MELD nodes. Synchronous, single-file, no daemon. WAL mode for concurrency. All DB ops via db.prepare() directly. Deployed to all 4 nodes Feb 21.
