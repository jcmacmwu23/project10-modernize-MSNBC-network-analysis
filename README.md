# Project 10 — Modernizing MSNBC Network Analysis

An evolution from exploratory notebooks to a modular Python pipeline for turning anonymous browsing sequences into weighted navigation graphs.

## How the analysis evolved

During exploratory data analysis, I found that the most informative aspect of the dataset was not the individual page visits but the transitions between pages within user sessions. That observation led me to model the cleaned clickstream as a graph, enabling navigation analysis through graph algorithms rather than traditional tabular aggregation alone. The graph representation emerged from understanding the data; it was not predetermined.

**Raw clickstream → clean and organize → inspect patterns → notice transitions → recognize graph structure → build nodes and weighted edges → graph analysis.**

This was an independent personal project using the public MSNBC dataset. My earlier Xbox experience provided general background in web analytics, but this project was not an attempt to recreate proprietary Xbox work. It does not use Xbox data, code, or internal systems.

The [original Data_Projects repository](https://github.com/jcmacmwu23/Data_Projects/tree/84820b7f3f779ba78965c2a47148961e2650e991/MSNBC%20Network%20Analysis) remains the historical reference. This separate repository preserves the original notebooks and revisits their transformations using engineering practices developed through later production experience.

## Historical → modern

| Historical notebooks | Modern implementation |
| --- | --- |
| Exploratory cleaning, metrics, and graph visualization | Separate parsing, validation, export, and graph modules |
| Interactive notebook execution | Installable package and command-line entry point |
| Intermediate files passed between notebooks | Ten reproducible CSV exports with explicit schemas |
| Inspection of analysis results | Pytest coverage of parsing, metrics, transitions, and pipeline outputs |

```text
legacy/                  Original processing and analysis notebooks
modern/msnbc/
  src/msnbc_modern/       Parser, CSV pipeline, optional NetworkX helpers
  tests/                 Unit and pipeline tests
  examples/              Small synthetic input for a standalone demo
  docs/                  Case study, project map, architecture and roadmap
  pyproject.toml         Package metadata and dependencies
```

## Reproduce locally

Use Python 3.11 or newer. From the repository root:

```bash
cd modern/msnbc
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
mkdir -p data/raw
gzip -c examples/sample.seq > data/raw/sample.seq.gz
.venv/bin/msnbc-modern --input data/raw/sample.seq.gz --output-dir data/derived
```

The demo is synthetic and needs no external dataset. See the [modern implementation guide](modern/msnbc/README.md) for the full historical dataset, output files, and optional graph dependency. Raw data, generated CSVs, environments, caches, and local working notes are excluded from Git.

## Modeling choices and limits

- Nodes represent **page categories**, not individual URLs. The input preserves category order but has no event timestamps.
- `user_id` is a locally assigned sequence identifier, not a persistent user identity.
- Directed edges count adjacent category transitions within each sequence; repeated categories produce self-loops. No transition crosses a sequence boundary.
- `normalized_edge_count` is the edge count divided by **all transitions**, rounded to ten decimal places. It is not an outgoing transition probability per source node.
- The transition CSV and edge counts are produced in one pass, but the parser still holds all sessions in memory. The current pipeline requires at least one transition in the dataset.

The modern scope currently covers Python transformations, CSV exports, and optional NetworkX graph construction. SQL, PySpark, Neo4j, richer graph reporting, and cloud deployment remain [roadmap items](modern/msnbc/docs/architecture-and-roadmap.md), not implemented features. Legacy findings and plots are preserved for historical context; the modern pipeline does not yet reproduce every notebook analysis.

## Read further

- [Legacy preservation notes](legacy/README.md)
- [Case study](modern/msnbc/docs/case-study.md)
- [Architecture and roadmap](modern/msnbc/docs/architecture-and-roadmap.md)
- [Implementation notes](modern/msnbc/python-implementation-notes.md)
