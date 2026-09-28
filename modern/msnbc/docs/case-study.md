# Case Study

## Project Framing

This modernization project revisits an older MSNBC browsing analysis and rebuilds it in a more production-minded format.

The key portfolio message is:

> The difficult work was not the final graph visualization. The difficult work was turning ambiguous sequence-based browsing data into structured analytical entities and relationships.

## Original Problem

The MSNBC dataset does not arrive as a standard event table such as:

`user_id | timestamp | page_category | session_id`

Instead, it arrives as compact browsing sequences that use numeric category ids. That means several layers of interpretation are required before useful downstream analysis is possible.

## Modernization Goal

The graph model emerged during exploratory data analysis: transitions between pages within sessions proved more informative than individual visits alone. Recognizing those relationships led to category nodes and weighted navigation edges. This independent project uses public MSNBC data; it was not an attempt to recreate proprietary Xbox work or systems.

The modernization goal is to preserve the original analytical reasoning while improving:

- code modularity
- validation
- reproducibility
- packaging
- testability
- project storytelling

## Data Transformation Story

The current Python pipeline expresses the following flow:

1. Read raw `.seq.gz` source data.
2. Parse the category-id lookup from the metadata header.
3. Parse each anonymous browsing sequence into a session record.
4. Derive session-level metrics such as total visits and first visited category.
5. Derive per-user visit counts.
6. Derive aggregate node weights from category visitation counts.
7. Derive directed transitions between consecutive categories.
8. Aggregate transitions into weighted edges.
9. Export graph-ready datasets for downstream use.

## Why This Is A Strong Portfolio Project

This project shows several things at once:

- data modeling under ambiguous raw inputs
- practical Python data-engineering skills
- graph-oriented transformation logic
- production-minded modernization of older work
- ability to tell a clear “then vs now” engineering story

## Recommended Interview Narrative

A strong way to describe this project is:

> I revisited an older browsing-sequence analysis project and rebuilt it as a modular Python pipeline. The main engineering challenge was converting a rudimentary raw format into structured session, node, and edge datasets that could support graph analysis downstream.

## What Comes Next

The Python implementation is now a solid foundation.

The strongest next extensions are:

- stream input parsing to reduce session retention (transition writing and edge aggregation already use a single pass)
- add SQL equivalents for the core transformations
- add a PySpark implementation for scale
- add Neo4j/Cypher outputs
- add a short architecture doc for large-scale event processing
