# MSNBC Network Analysis Modernization

This project revisits an older notebook-based MSNBC browsing analysis and rebuilds it as a modular, testable Python pipeline.

The core modernization goal is not just to reproduce charts or NetworkX output. The real engineering problem is transforming rudimentary anonymous browsing sequences into structured session, node, and edge datasets that can support graph analysis downstream.

## Why This Project Matters

The original MSNBC dataset is not a clean clickstream event table. It is a compact sequence-based representation that requires interpretation before it becomes analytically useful.

This project demonstrates how to move from:

- ambiguous raw browsing sequences
- to structured session-level metrics
- to visit counts and entry behavior
- to transition tables
- to weighted graph-ready nodes and edges

That makes it a strong data-engineering and graph-modeling portfolio piece.

## What This Modern Python Version Covers

- raw `.seq.gz` parsing
- category metadata extraction
- session-level record creation
- total visit counts per user
- first visited category per user
- per-user category visit counts in long and wide forms
- aggregate category frequencies
- entry frequencies
- transition extraction
- weighted edge derivation
- graph-ready node and edge exports
- unit and pipeline tests

## Project Layout

```text
modern/msnbc/
  README.md
  pyproject.toml
  python-implementation-notes.md
  .gitignore
  docs/
    case-study.md
    architecture-and-roadmap.md
    project-map.md
  src/
    msnbc_modern/
      parser.py
      pipeline.py
      graph.py
  tests/
    test_parser.py
  data/
    derived/
```

## Quick Start

Setup:

```bash
cd modern/msnbc
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

From this package directory, run the pipeline on the included synthetic example:

```bash
mkdir -p data/raw
gzip -c examples/sample.seq > data/raw/sample.seq.gz
.venv/bin/msnbc-modern \
  --input data/raw/sample.seq.gz \
  --output-dir data/derived
```

Run tests:

```bash
.venv/bin/pytest tests
```

For the original dataset, the historical project cites the [UCI MSNBC dataset](https://archive.ics.uci.edu/dataset/133/msnbc+com+anonymous+web+data). A copy used by the original project is available at the pinned historical revision:

```bash
curl --fail --location \
  'https://raw.githubusercontent.com/jcmacmwu23/Data_Projects/84820b7f3f779ba78965c2a47148961e2650e991/MSNBC%20Network%20Analysis/msnbc990928.seq.gz' \
  --output data/raw/msnbc990928.seq.gz
.venv/bin/msnbc-modern \
  --input data/raw/msnbc990928.seq.gz \
  --output-dir data/derived
```

Expected SHA-256 for that historical gzip file: `d0ad0edf726fe265f956b43d2d02bf07b58b5c27df3fdbc7b02b7195061374a2`.

Generated files can be large and are ignored by Git. The full dataset is retained in memory during parsing. The dataset must contain at least one adjacent transition. Install `.[graph]` to use the optional NetworkX helpers; the core CSV pipeline has no third-party runtime dependencies.

## Outputs

The current pipeline produces:

- `category_lookup.csv`
- `sessions.csv`
- `visits_per_user_long.csv`
- `visits_per_user_wide.csv`
- `category_frequency.csv`
- `entry_frequency.csv`
- `transitions.csv`
- `edge_weights.csv`
- `graph_nodes.csv`
- `graph_edges.csv`

## How To Review This Project

If you want to understand the project quickly, read in this order:

1. `README.md`
2. `docs/case-study.md`
3. `src/msnbc_modern/parser.py`
4. `src/msnbc_modern/pipeline.py`
5. `tests/test_parser.py`
6. `python-implementation-notes.md`

## Current Status

What is complete:

- modern Python implementation of the original transformation logic
- reproducible local test setup
- editable package install
- CLI entrypoint
- derived graph-ready outputs

What is still worth improving:

- streaming input parsing to avoid retaining all sessions in memory (transition writing and edge aggregation already share a single pass)
- richer graph analytics/reporting layer
- SQL version
- PySpark version
- Neo4j export/query layer
- architecture diagrams and scale-out design

## Supporting Docs

- `docs/case-study.md`
- `docs/project-map.md`
- `docs/architecture-and-roadmap.md`
- `python-implementation-notes.md`
