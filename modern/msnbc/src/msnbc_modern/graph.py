from __future__ import annotations

from typing import Any


def build_directed_graph(node_rows: list[dict[str, object]], edge_rows: list[dict[str, object]]) -> Any:
    nx = _require_networkx()
    graph = nx.DiGraph()

    for row in node_rows:
        graph.add_node(
            row['category'],
            category_id=row['category_id'],
            visit_count=row['visit_count'],
            normalized_visit_count=row['normalized_visit_count'],
        )

    for row in edge_rows:
        graph.add_edge(
            row['source_category'],
            row['target_category'],
            edge_count=row['edge_count'],
            normalized_edge_count=row['normalized_edge_count'],
        )

    return graph


def build_undirected_graph(node_rows: list[dict[str, object]], edge_rows: list[dict[str, object]]) -> Any:
    nx = _require_networkx()
    graph = nx.Graph()

    for row in node_rows:
        graph.add_node(
            row['category'],
            category_id=row['category_id'],
            visit_count=row['visit_count'],
            normalized_visit_count=row['normalized_visit_count'],
        )

    for row in edge_rows:
        source = row['source_category']
        target = row['target_category']
        if graph.has_edge(source, target):
            graph[source][target]['edge_count'] += row['edge_count']
            graph[source][target]['normalized_edge_count'] += row['normalized_edge_count']
            continue

        graph.add_edge(
            source,
            target,
            edge_count=row['edge_count'],
            normalized_edge_count=row['normalized_edge_count'],
        )

    return graph


def _require_networkx() -> Any:
    try:
        import networkx as nx
    except ImportError as exc:
        raise ImportError(
            'networkx is required for graph construction. Install it before using msnbc_modern.graph.'
        ) from exc
    return nx
