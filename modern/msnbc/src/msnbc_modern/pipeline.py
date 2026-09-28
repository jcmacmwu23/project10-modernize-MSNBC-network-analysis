from __future__ import annotations

import argparse
from collections import Counter
import csv
from pathlib import Path
from typing import Iterable

from msnbc_modern.parser import (
    ParsedDataset,
    build_category_frequency_rows,
    build_category_lookup_rows,
    build_entry_frequency_rows,
    category_name,
    iter_session_rows,
    iter_visit_count_rows,
    iter_visit_count_wide_rows,
    normalized_value,
    parse_msnbc_file,
)


def write_csv(path: Path, rows: Iterable[dict[str, object]], *, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        row_count = 0
        for row in rows:
            writer.writerow(row)
            row_count += 1

    if row_count == 0:
        raise ValueError(f'No rows available for output file: {path}')


def write_transitions_and_collect_edge_weights(
    dataset: ParsedDataset,
    transitions_path: Path,
) -> list[dict[str, object]]:
    transitions_path.parent.mkdir(parents=True, exist_ok=True)
    transition_counts: Counter[tuple[str, str]] = Counter()
    transition_row_count = 0

    with transitions_path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                'user_id',
                'step_index',
                'source_id',
                'source_category',
                'target_id',
                'target_category',
            ],
        )
        writer.writeheader()

        for session in dataset.sessions:
            for step_index, (source_id, target_id) in enumerate(session.transitions, start=1):
                writer.writerow(
                    {
                        'user_id': session.user_id,
                        'step_index': step_index,
                        'source_id': source_id,
                        'source_category': category_name(dataset.categories, source_id),
                        'target_id': target_id,
                        'target_category': category_name(dataset.categories, target_id),
                    }
                )
                transition_counts[(source_id, target_id)] += 1
                transition_row_count += 1

    if transition_row_count == 0:
        raise ValueError(f'No rows available for output file: {transitions_path}')

    total_transitions = sum(transition_counts.values())
    edge_rows: list[dict[str, object]] = []
    for source_id, target_id in sorted(transition_counts, key=lambda pair: (int(pair[0]), int(pair[1]))):
        edge_count = transition_counts[(source_id, target_id)]
        edge_rows.append(
            {
                'source_id': source_id,
                'source_category': category_name(dataset.categories, source_id),
                'target_id': target_id,
                'target_category': category_name(dataset.categories, target_id),
                'edge_count': edge_count,
                'normalized_edge_count': normalized_value(edge_count, total_transitions),
            }
        )

    return edge_rows


def run(input_path: Path, output_dir: Path) -> None:
    dataset = parse_msnbc_file(input_path)
    category_frequency_rows = build_category_frequency_rows(dataset)
    entry_frequency_rows = build_entry_frequency_rows(dataset)

    write_csv(
        output_dir / 'category_lookup.csv',
        build_category_lookup_rows(dataset.categories),
        fieldnames=['category_id', 'category'],
    )
    write_csv(
        output_dir / 'sessions.csv',
        iter_session_rows(dataset),
        fieldnames=['user_id', 'total_visits', 'entry_id', 'entry_category', 'sequence_ids'],
    )
    write_csv(
        output_dir / 'visits_per_user_long.csv',
        iter_visit_count_rows(dataset),
        fieldnames=['user_id', 'category_id', 'category', 'visit_count'],
    )
    write_csv(
        output_dir / 'visits_per_user_wide.csv',
        iter_visit_count_wide_rows(dataset),
        fieldnames=['user_id', *dataset.categories],
    )
    write_csv(
        output_dir / 'category_frequency.csv',
        category_frequency_rows,
        fieldnames=['category_id', 'category', 'visit_count', 'normalized_visit_count'],
    )
    write_csv(
        output_dir / 'entry_frequency.csv',
        entry_frequency_rows,
        fieldnames=['category_id', 'category', 'entry_count', 'normalized_entry_count'],
    )
    edge_weight_rows = write_transitions_and_collect_edge_weights(dataset, output_dir / 'transitions.csv')
    write_csv(
        output_dir / 'edge_weights.csv',
        edge_weight_rows,
        fieldnames=[
            'source_id',
            'source_category',
            'target_id',
            'target_category',
            'edge_count',
            'normalized_edge_count',
        ],
    )
    write_csv(
        output_dir / 'graph_nodes.csv',
        category_frequency_rows,
        fieldnames=['category_id', 'category', 'visit_count', 'normalized_visit_count'],
    )
    write_csv(
        output_dir / 'graph_edges.csv',
        edge_weight_rows,
        fieldnames=[
            'source_id',
            'source_category',
            'target_id',
            'target_category',
            'edge_count',
            'normalized_edge_count',
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Modern MSNBC parser and export pipeline')
    parser.add_argument('--input', required=True, type=Path, help='Path to msnbc990928.seq.gz')
    parser.add_argument('--output-dir', required=True, type=Path, help='Directory for derived CSV outputs')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(input_path=args.input, output_dir=args.output_dir)


if __name__ == '__main__':
    main()
