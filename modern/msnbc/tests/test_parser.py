from pathlib import Path

import pytest

from msnbc_modern.parser import (
    build_category_frequency_rows,
    build_category_lookup_rows,
    build_edge_weight_rows,
    build_entry_frequency_rows,
    build_session_rows,
    build_transition_rows,
    build_visit_count_rows,
    build_visit_count_wide_rows,
    parse_msnbc_file,
    parse_sequence_line,
)
from msnbc_modern.pipeline import run, write_transitions_and_collect_edge_weights


SAMPLE_CONTENT = (
    "% Different categories found in input file:\n\n"
    "frontpage news tech local\n\n"
    "% Sequences:\n\n"
    "1 2 2 4 \n"
    "3 1 \n"
)


def test_parse_sequence_line_trims_and_keeps_order() -> None:
    session = parse_sequence_line('1 2 2 5 3 ', user_id=7)

    assert session.user_id == 7
    assert session.sequence_ids == ('1', '2', '2', '5', '3')
    assert session.total_visits == 5
    assert session.entry_id == '1'


def test_parse_msnbc_file_reads_metadata_and_sessions(tmp_path: Path) -> None:
    import gzip

    compressed_file = tmp_path / 'sample.seq.gz'
    with gzip.open(compressed_file, 'wt', encoding='utf-8') as handle:
        handle.write(SAMPLE_CONTENT)

    dataset = parse_msnbc_file(compressed_file)

    assert dataset.categories == ('frontpage', 'news', 'tech', 'local')
    assert len(dataset.sessions) == 2
    assert dataset.sessions[0].sequence_ids == ('1', '2', '2', '4')
    assert dataset.sessions[1].entry_id == '3'


def test_category_name_validation_raises_for_out_of_range_ids(tmp_path: Path) -> None:
    import gzip

    compressed_file = tmp_path / 'invalid.seq.gz'
    with gzip.open(compressed_file, 'wt', encoding='utf-8') as handle:
        handle.write(
            "% Different categories found in input file:\n\n"
            "frontpage news\n\n"
            "% Sequences:\n\n"
            "1 3 \n"
        )

    with pytest.raises(ValueError, match='out of range'):
        parse_msnbc_file(compressed_file)


def test_derived_rows_match_expected_metrics(tmp_path: Path) -> None:
    import gzip

    compressed_file = tmp_path / 'sample.seq.gz'
    with gzip.open(compressed_file, 'wt', encoding='utf-8') as handle:
        handle.write(SAMPLE_CONTENT)

    dataset = parse_msnbc_file(compressed_file)

    session_rows = build_session_rows(dataset)
    long_rows = build_visit_count_rows(dataset)
    wide_rows = build_visit_count_wide_rows(dataset)
    lookup_rows = build_category_lookup_rows(dataset.categories)
    category_rows = build_category_frequency_rows(dataset)
    entry_rows = build_entry_frequency_rows(dataset)
    transition_rows = build_transition_rows(dataset)
    edge_rows = build_edge_weight_rows(dataset)

    assert session_rows[0] == {
        'user_id': 1,
        'total_visits': 4,
        'entry_id': '1',
        'entry_category': 'frontpage',
        'sequence_ids': '1 2 2 4',
    }
    assert {'user_id': 1, 'category_id': '2', 'category': 'news', 'visit_count': 2} in long_rows
    assert wide_rows[0]['frontpage'] == 1
    assert wide_rows[0]['news'] == 2
    assert wide_rows[0]['tech'] == 0
    assert wide_rows[0]['local'] == 1
    assert lookup_rows[0] == {'category_id': '1', 'category': 'frontpage'}
    assert category_rows[1] == {
        'category_id': '2',
        'category': 'news',
        'visit_count': 2,
        'normalized_visit_count': 0.3333333333,
    }
    assert entry_rows[0] == {
        'category_id': '1',
        'category': 'frontpage',
        'entry_count': 1,
        'normalized_entry_count': 0.5,
    }
    assert transition_rows[0] == {
        'user_id': 1,
        'step_index': 1,
        'source_id': '1',
        'source_category': 'frontpage',
        'target_id': '2',
        'target_category': 'news',
    }
    assert edge_rows[0] == {
        'source_id': '1',
        'source_category': 'frontpage',
        'target_id': '2',
        'target_category': 'news',
        'edge_count': 1,
        'normalized_edge_count': 0.25,
    }


def test_pipeline_run_writes_expected_outputs(tmp_path: Path) -> None:
    import gzip

    input_file = tmp_path / 'sample.seq.gz'
    output_dir = tmp_path / 'derived'

    with gzip.open(input_file, 'wt', encoding='utf-8') as handle:
        handle.write(SAMPLE_CONTENT)

    run(input_file, output_dir)

    expected_files = {
        'category_lookup.csv',
        'sessions.csv',
        'visits_per_user_long.csv',
        'visits_per_user_wide.csv',
        'category_frequency.csv',
        'entry_frequency.csv',
        'transitions.csv',
        'edge_weights.csv',
        'graph_nodes.csv',
        'graph_edges.csv',
    }

    assert {path.name for path in output_dir.iterdir()} == expected_files

    sessions_header = (output_dir / 'sessions.csv').read_text(encoding='utf-8').splitlines()[0]
    transitions_header = (output_dir / 'transitions.csv').read_text(encoding='utf-8').splitlines()[0]

    assert sessions_header == 'user_id,total_visits,entry_id,entry_category,sequence_ids'
    assert transitions_header == 'user_id,step_index,source_id,source_category,target_id,target_category'


def test_transition_writer_collects_edge_weights_in_single_pass(tmp_path: Path) -> None:
    import gzip

    input_file = tmp_path / 'sample.seq.gz'
    transitions_file = tmp_path / 'transitions.csv'

    with gzip.open(input_file, 'wt', encoding='utf-8') as handle:
        handle.write(SAMPLE_CONTENT)

    dataset = parse_msnbc_file(input_file)
    edge_rows = write_transitions_and_collect_edge_weights(dataset, transitions_file)

    assert transitions_file.exists()
    assert edge_rows == [
        {
            'source_id': '1',
            'source_category': 'frontpage',
            'target_id': '2',
            'target_category': 'news',
            'edge_count': 1,
            'normalized_edge_count': 0.25,
        },
        {
            'source_id': '2',
            'source_category': 'news',
            'target_id': '2',
            'target_category': 'news',
            'edge_count': 1,
            'normalized_edge_count': 0.25,
        },
        {
            'source_id': '2',
            'source_category': 'news',
            'target_id': '4',
            'target_category': 'local',
            'edge_count': 1,
            'normalized_edge_count': 0.25,
        },
        {
            'source_id': '3',
            'source_category': 'tech',
            'target_id': '1',
            'target_category': 'frontpage',
            'edge_count': 1,
            'normalized_edge_count': 0.25,
        },
    ]
