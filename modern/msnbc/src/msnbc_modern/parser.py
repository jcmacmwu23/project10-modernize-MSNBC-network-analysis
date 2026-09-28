from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import gzip
from pathlib import Path
from typing import Iterable, Iterator


@dataclass(frozen=True)
class SessionRecord:
    user_id: int
    sequence_ids: tuple[str, ...]

    @property
    def total_visits(self) -> int:
        return len(self.sequence_ids)

    @property
    def entry_id(self) -> str:
        return self.sequence_ids[0]

    @property
    def transitions(self) -> tuple[tuple[str, str], ...]:
        return tuple(zip(self.sequence_ids, self.sequence_ids[1:]))


@dataclass(frozen=True)
class ParsedDataset:
    categories: tuple[str, ...]
    sessions: tuple[SessionRecord, ...]


def _clean_tokens(line: str) -> list[str]:
    return [token for token in line.strip().split() if token]


def parse_sequence_line(line: str, *, user_id: int) -> SessionRecord:
    tokens = _clean_tokens(line)
    if not tokens:
        raise ValueError('Sequence line is empty after tokenization.')
    return SessionRecord(user_id=user_id, sequence_ids=tuple(tokens))


def parse_msnbc_file(path: str | Path) -> ParsedDataset:
    categories: list[str] | None = None
    sessions: list[SessionRecord] = []
    in_sequences = False

    with gzip.open(path, mode='rt', encoding='utf-8') as handle:
        for raw_line in handle:
            stripped = raw_line.strip()
            if not stripped:
                continue

            if stripped.startswith('%'):
                if stripped.lower().startswith('% sequences'):
                    in_sequences = True
                continue

            if categories is None:
                categories = _clean_tokens(stripped)
                continue

            if not in_sequences:
                continue

            sessions.append(parse_sequence_line(stripped, user_id=len(sessions) + 1))

    if categories is None:
        raise ValueError('Could not find category metadata in the input file.')

    if not sessions:
        raise ValueError('Could not find any browsing sequences in the input file.')

    dataset = ParsedDataset(categories=tuple(categories), sessions=tuple(sessions))
    validate_dataset(dataset)
    return dataset


def iter_session_rows(dataset: ParsedDataset) -> Iterator[dict[str, object]]:
    for session in dataset.sessions:
        yield {
            'user_id': session.user_id,
            'total_visits': session.total_visits,
            'entry_id': session.entry_id,
            'entry_category': category_name(dataset.categories, session.entry_id),
            'sequence_ids': ' '.join(session.sequence_ids),
        }


def build_session_rows(dataset: ParsedDataset) -> list[dict[str, object]]:
    return list(iter_session_rows(dataset))


def iter_visit_count_rows(dataset: ParsedDataset) -> Iterator[dict[str, object]]:
    for session in dataset.sessions:
        visit_counts = Counter(session.sequence_ids)
        for category_id, visit_count in sorted(visit_counts.items(), key=lambda item: int(item[0])):
            yield {
                'user_id': session.user_id,
                'category_id': category_id,
                'category': category_name(dataset.categories, category_id),
                'visit_count': visit_count,
            }


def build_visit_count_rows(dataset: ParsedDataset) -> list[dict[str, object]]:
    return list(iter_visit_count_rows(dataset))


def iter_visit_count_wide_rows(dataset: ParsedDataset) -> Iterator[dict[str, object]]:
    ordered_ids = [str(index) for index in range(1, len(dataset.categories) + 1)]
    for session in dataset.sessions:
        visit_counts = Counter(session.sequence_ids)
        row: dict[str, object] = {'user_id': session.user_id}
        for category_id in ordered_ids:
            row[category_name(dataset.categories, category_id)] = visit_counts.get(category_id, 0)
        yield row


def build_visit_count_wide_rows(dataset: ParsedDataset) -> list[dict[str, object]]:
    return list(iter_visit_count_wide_rows(dataset))


def build_category_lookup_rows(categories: Iterable[str]) -> list[dict[str, str]]:
    return [
        {'category_id': str(index), 'category': category}
        for index, category in enumerate(categories, start=1)
    ]


def build_entry_frequency_rows(dataset: ParsedDataset) -> list[dict[str, object]]:
    entry_counts = Counter(session.entry_id for session in dataset.sessions)
    total_entries = sum(entry_counts.values())
    rows: list[dict[str, object]] = []
    for category_id, entry_count in sorted(entry_counts.items(), key=lambda item: int(item[0])):
        rows.append(
            {
                'category_id': category_id,
                'category': category_name(dataset.categories, category_id),
                'entry_count': entry_count,
                'normalized_entry_count': normalized_value(entry_count, total_entries),
            }
        )
    return rows


def build_category_frequency_rows(dataset: ParsedDataset) -> list[dict[str, object]]:
    category_counts: Counter[str] = Counter()
    for session in dataset.sessions:
        category_counts.update(session.sequence_ids)

    total_visits = sum(category_counts.values())
    rows: list[dict[str, object]] = []
    for category_id in sorted(category_counts, key=int):
        visit_count = category_counts[category_id]
        rows.append(
            {
                'category_id': category_id,
                'category': category_name(dataset.categories, category_id),
                'visit_count': visit_count,
                'normalized_visit_count': normalized_value(visit_count, total_visits),
            }
        )
    return rows


def iter_transition_rows(dataset: ParsedDataset) -> Iterator[dict[str, object]]:
    for session in dataset.sessions:
        for step_index, (source_id, target_id) in enumerate(session.transitions, start=1):
            yield {
                'user_id': session.user_id,
                'step_index': step_index,
                'source_id': source_id,
                'source_category': category_name(dataset.categories, source_id),
                'target_id': target_id,
                'target_category': category_name(dataset.categories, target_id),
            }


def build_transition_rows(dataset: ParsedDataset) -> list[dict[str, object]]:
    return list(iter_transition_rows(dataset))


def build_edge_weight_rows(dataset: ParsedDataset) -> list[dict[str, object]]:
    transition_counts: Counter[tuple[str, str]] = Counter()
    for session in dataset.sessions:
        transition_counts.update(session.transitions)

    total_transitions = sum(transition_counts.values())
    rows: list[dict[str, object]] = []
    for (source_id, target_id), edge_count in sorted(transition_counts.items(), key=_edge_sort_key):
        rows.append(
            {
                'source_id': source_id,
                'source_category': category_name(dataset.categories, source_id),
                'target_id': target_id,
                'target_category': category_name(dataset.categories, target_id),
                'edge_count': edge_count,
                'normalized_edge_count': normalized_value(edge_count, total_transitions),
            }
        )
    return rows


def build_node_rows_for_graph(dataset: ParsedDataset) -> list[dict[str, object]]:
    return build_category_frequency_rows(dataset)


def build_edge_rows_for_graph(dataset: ParsedDataset) -> list[dict[str, object]]:
    return build_edge_weight_rows(dataset)


def validate_dataset(dataset: ParsedDataset) -> None:
    for session in dataset.sessions:
        for category_id in session.sequence_ids:
            category_name(dataset.categories, category_id)


def normalized_value(count: int, total: int) -> float:
    if total <= 0:
        raise ValueError('Total must be positive for normalization.')
    return round(float(count) / float(total), 10)


def _edge_sort_key(item: tuple[tuple[str, str], int]) -> tuple[int, int]:
    (source_id, target_id), _ = item
    return (int(source_id), int(target_id))


def category_name(categories: tuple[str, ...], category_id: str) -> str:
    try:
        category_index = int(category_id) - 1
    except ValueError as exc:
        raise ValueError(f'Category id must be numeric, received {category_id!r}.') from exc

    if category_index < 0 or category_index >= len(categories):
        raise ValueError(
            f'Category id {category_id!r} is out of range for {len(categories)} categories.'
        )

    return categories[category_index]
