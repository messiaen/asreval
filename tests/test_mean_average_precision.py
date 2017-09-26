import os

from asreval.compute_map import load_stm
from asreval.cnet import CnetIndex
from asreval.stm import Stm
from asreval.mean_average_precision import kws_mean_ave_precision
from asreval.mean_average_precision import labeled_arc_matches
from asreval.mean_average_precision import select_best_arc
from asreval.cnet import CnetEdge
from asreval.cnet import LabeledCnetEdge
from asreval.parse import parse_stm_utterances
from asreval.parse import parse_cnet_utterances
from asreval.parse import lines_from_file_list


def test_kws_map():
    test_stm_filename = os.path.join(os.path.dirname(__file__), '3test.stm')
    with open(test_stm_filename, 'r') as f:
        stmRef = Stm(parse_stm_utterances(f))
    word_list = stmRef.word_list

    cnet_dir = os.path.join(os.path.dirname(__file__), '3cnets-A')

    cnet_list = map(lambda fn: os.path.join(cnet_dir, fn),
                    filter(lambda x: x.endswith('.lat'),
                           os.listdir(cnet_dir)))

    line_iter = lines_from_file_list(cnet_list)
    cnet_uttrs = list(parse_cnet_utterances(line_iter, channel='A'))

    assert len(cnet_uttrs) == 24
    assert len(word_list) == 196

    # new_uttrs = set(cnet.to_new_uttrs())

    cnetIndex = CnetIndex(cnet_uttrs)

    results = kws_mean_ave_precision(word_list, cnetIndex, stmRef)
    assert results.true_total_hits == 286
    assert results.total_tp == 278
    assert results.total_fp == 119
    assert sum(results.no_time_match_counts.values()) == 1
    assert abs(results.map - 0.9151) < 0.0001


def test_select_best_arc():
    arcs = [LabeledCnetEdge(CnetEdge(1, 2, 1.0, 4.0, 'WORD1', 0.7), True, True),
            LabeledCnetEdge(CnetEdge(2, 3, 1.0, 4.0, 'WORD1', 0.7), True, True),
            LabeledCnetEdge(CnetEdge(3, 4, 1.0, 4.0, 'WORD1', 0.3), True, True),
            LabeledCnetEdge(CnetEdge(4, 5, 1.0, 4.0, 'WORD1', 0.8), True, True),
            LabeledCnetEdge(CnetEdge(5, 6, 1.0, 4.0, 'WORD1', 0.9), True, True),
            LabeledCnetEdge(CnetEdge(6, 7, 1.0, 4.0, 'WORD1', 0.99), True, True),
            LabeledCnetEdge(CnetEdge(7, 8, 1.0, 4.0, 'WORD1', 0.2), True, True),
            LabeledCnetEdge(CnetEdge(8, 9, 1.0, 4.0, 'WORD1', 0.01), True, True)]

    expected = LabeledCnetEdge(CnetEdge(6, 7, 1.0, 4.0, 'WORD1', 0.99), True, True)

    assert (expected, 8, 0) == select_best_arc(iter(arcs))

    arcs = [LabeledCnetEdge(CnetEdge(1, 2, 1.0, 4.0, 'WORD1', 0.7), True, True),
            LabeledCnetEdge(CnetEdge(2, 3, 1.0, 4.0, 'WORD1', 0.7), True, True),
            LabeledCnetEdge(CnetEdge(3, 4, 1.0, 4.0, 'WORD1', 0.3), True, True),
            LabeledCnetEdge(CnetEdge(4, 5, 1.0, 4.0, 'WORD1', 0.8), True, True),
            LabeledCnetEdge(CnetEdge(5, 6, 1.0, 4.0, 'WORD1', 0.9), True, True),
            LabeledCnetEdge(CnetEdge(6, 7, 1.0, 4.0, 'WORD1', 0.99), False, True),
            LabeledCnetEdge(CnetEdge(7, 8, 1.0, 4.0, 'WORD1', 0.2), True, True),
            LabeledCnetEdge(CnetEdge(8, 9, 1.0, 4.0, 'WORD1', 0.01), True, True)]

    expected = LabeledCnetEdge(CnetEdge(5, 6, 1.0, 4.0, 'WORD1', 0.9), True, True)

    assert (expected, 8, 1) == select_best_arc(iter(arcs))

    arcs = [LabeledCnetEdge(CnetEdge(1, 2, 1.0, 4.0, 'WORD1', 0.7), False, True),
            LabeledCnetEdge(CnetEdge(2, 3, 1.0, 4.0, 'WORD1', 0.7), False, True),
            LabeledCnetEdge(CnetEdge(3, 4, 1.0, 4.0, 'WORD1', 0.3), False, True),
            LabeledCnetEdge(CnetEdge(4, 5, 1.0, 4.0, 'WORD1', 0.8), False, True),
            LabeledCnetEdge(CnetEdge(5, 6, 1.0, 4.0, 'WORD1', 0.9), False, True),
            LabeledCnetEdge(CnetEdge(6, 7, 1.0, 4.0, 'WORD1', 0.99), False, True),
            LabeledCnetEdge(CnetEdge(7, 8, 1.0, 4.0, 'WORD1', 0.2), False, True),
            LabeledCnetEdge(CnetEdge(8, 9, 1.0, 4.0, 'WORD1', 0.01), False, True)]

    expected = LabeledCnetEdge(CnetEdge(6, 7, 1.0, 4.0, 'WORD1', 0.99), False, True)

    assert (expected, 8, 8) == select_best_arc(iter(arcs))


def test_labeled_arc_matches():
    arcs = [CnetEdge(start_node=11, end_node=12, start_time=3.24, end_time=3.61, word='THE', score=5.43949e-05),
            CnetEdge(start_node=13, end_node=17, start_time=3.3, end_time=3.61, word='BLAH', score=4.17964e-05),
            CnetEdge(start_node=65, end_node=72, start_time=10.56, end_time=90.09, word='THE', score=1.05067e-05),
            CnetEdge(start_node=69, end_node=72, start_time=5.75, end_time=5.98, word='THE', score=6.24331e-06),
            CnetEdge(start_node=71, end_node=72, start_time=5.53, end_time=5.98, word='THE', score=2.15655e-06)]

    expected_labels = [LabeledCnetEdge(CnetEdge(start_node=11, end_node=12, start_time=3.24, end_time=3.61, word='THE', score=5.43949e-05), matches_time=True, matches_word=True),
                       LabeledCnetEdge(CnetEdge(start_node=13, end_node=17, start_time=3.3, end_time=3.61, word='BLAH', score=4.17964e-05), matches_time=True, matches_word=False),
                       LabeledCnetEdge(CnetEdge(start_node=65, end_node=72, start_time=10.56, end_time=90.09, word='THE', score=1.05067e-05), matches_time=False, matches_word=False),
                       LabeledCnetEdge(CnetEdge(start_node=69, end_node=72, start_time=5.75, end_time=5.98, word='THE', score=6.24331e-06), matches_time=True, matches_word=True),
                       LabeledCnetEdge(CnetEdge(start_node=71, end_node=72, start_time=5.53, end_time=5.98, word='THE', score=2.15655e-06), matches_time=True, matches_word=True)]

    test_stm_filename = os.path.join(os.path.dirname(__file__), '3test.stm')
    stmRef = Stm(load_stm(test_stm_filename).new_uttrs)

    labeled_arcs = list(labeled_arc_matches(arcs, '260-123286-0026', 'A', stmRef, 0.5))

    assert labeled_arcs == expected_labels

