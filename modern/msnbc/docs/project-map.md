# Project Map

## Purpose Of Each File

### Root

- `README.md`
  Main portfolio-facing project overview and quick-start guide.

- `pyproject.toml`
  Package metadata, optional dependencies, pytest config, and CLI entrypoint registration.

- `python-implementation-notes.md`
  Technical notes on what the Python implementation does and where performance still needs improvement.

- `.gitignore`
  Keeps local environment and cache artifacts out of version control.

### Source Code

- `src/msnbc_modern/parser.py`
  Core transformation logic: raw parsing, validation, session derivation, visit counts, transitions, and edge aggregation.

- `src/msnbc_modern/pipeline.py`
  CLI-driven export pipeline that writes the derived CSV outputs.

- `src/msnbc_modern/graph.py`
  Lightweight helpers for turning node/edge rows into NetworkX graph objects.

### Tests

- `tests/test_parser.py`
  Unit tests and a small pipeline integration test that validate the transformation contract.

### Derived Data

- `data/derived/`
  Output artifacts produced by the current pipeline run.

### Docs

- `docs/case-study.md`
  Portfolio-facing narrative for the project.

- `docs/project-map.md`
  This file. A quick reference for how the project is organized.

- `docs/architecture-and-roadmap.md`
  Design notes on the current architecture, known bottlenecks, and future roadmap.

## Recommended Review Order

If you are reading this project for the first time:

1. `README.md`
2. `docs/case-study.md`
3. `tests/test_parser.py`
4. `src/msnbc_modern/parser.py`
5. `src/msnbc_modern/pipeline.py`
6. `python-implementation-notes.md`
7. `docs/architecture-and-roadmap.md`

