# Architecture And Roadmap

## Current Architecture

Current implementation pattern:

raw `.seq.gz` file  
-> parse metadata and sessions  
-> derive session metrics  
-> derive visit counts  
-> write transitions while accumulating edge counts  
-> export weighted edges  
-> export CSV artifacts  
-> optional graph construction via NetworkX helpers

## Current Strengths

- simple and understandable flow
- no notebook dependency
- explicit tests
- CLI entrypoint
- editable package install
- graph-ready outputs
- improved validation over the original notebook implementation
- reduced duplicated work in the transition/edge phase

## Current Bottleneck

The main remaining performance costs are now narrower than before.

Today the code still:

1. holds the full parsed dataset in memory before all downstream exports complete
2. builds the wide per-user output in pure Python
3. emits very large CSV outputs through per-row dictionary writing

Those are acceptable for the current portfolio stage, but they are the most obvious next targets if we want to push further on scale.

## Best Next Refactor

The strongest next engineering improvements would be:

1. move toward a more streaming-first dataset flow
2. reduce memory pressure from the full retained `ParsedDataset`
3. evaluate whether `visits_per_user_wide.csv` should remain a default artifact or become optional
4. add runtime metrics or logging for large runs

## Future Roadmap

### Near Term

- add tests around graph helpers
- add lightweight data-quality checks and summary logging
- decide which derived artifacts are mandatory vs optional

### Medium Term

- add SQL translation for the core transformations
- add PySpark implementation
- add project comparison notes: Python vs SQL vs PySpark

### Longer Term

- add Neo4j import-ready outputs
- add Cypher examples
- add scale-out architecture for high-volume clickstream ingestion
- add cloud-oriented design notes for S3 / Glue / curated graph datasets

## Portfolio Positioning

This project is strongest when framed as:

- a graph data-engineering modernization project
- a “then vs now” engineering story
- a bridge from earlier exploratory notebook work to more production-oriented design
