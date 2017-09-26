import os

import pytest

from asreval.compute_map import MAP
from asreval.compute_map import load_stm
from asreval.cnet import CnetOld, SlfIndex
from asreval.stm import Stm
from asreval.mean_average_precision import kws_mean_ave_precision, \
    labeled_uttr_arc_lists, select_best_arc


@pytest.mark.skip('Skip this b/c is takes awhile to run')
def test_map_orig():
    test_stm_filename = os.path.join(os.path.dirname(__file__), '3test.stm')
    cnet_dir = os.path.join(os.path.dirname(__file__), '3cnets-A')

    cnet_list = map(lambda fn: os.path.join(cnet_dir, fn),
                    filter(lambda x: x.endswith('.lat'),
                           os.listdir(cnet_dir)))

    cnet = CnetOld('directory')
    for fn in cnet_list:
        cnet.load(fn)

    # there is not speech duration
    assert cnet.speech_duration == 0.0

    stm = load_stm(test_stm_filename)
    word_list = stm.get_word_list()

    # assert len(word_list) == 8118

    comp_map = MAP(word_list, cnet, stm)
    map_score, word_ap = comp_map.compute_map()

    new_uttrs = set(cnet.to_new_uttrs())
    assert len(new_uttrs) == cnet.uttr_count

    new_ref_uttrs = stm.new_uttrs
    assert len(new_ref_uttrs) == stm.num_uttrs
    assert stm.num_uttrs == cnet.uttr_count

    cnetIndex = SlfIndex(new_uttrs)
    stmRef = Stm(new_ref_uttrs)
    assert len(word_list) == len(stmRef.word_list)

    results = kws_mean_ave_precision(word_list, cnetIndex, stmRef)
    new_map_score, new_word_ap, total_tp, total_fp, true_count_total, arc_counts, no_time_match_counts = results
    assert true_count_total == comp_map.total_possible_hits
    assert total_fp == comp_map.total_fp
    assert total_tp == comp_map.total_tp
    assert new_word_ap == word_ap
    assert sum(new_word_ap.values()) == sum(word_ap.values())
    assert len(no_time_match_counts) == len(stm.not_found)

    assert abs(new_map_score - map_score) < 0.00001


@pytest.mark.skip('This is not consistent when edge do not have time matches')
def test_map_orig_internal():
    test_stm_filename = os.path.join(os.path.dirname(__file__), '3test.stm')
    cnet_dir = os.path.join(os.path.dirname(__file__), '3cnets-A')

    cnet_list = map(lambda fn: os.path.join(cnet_dir, fn),
                    filter(lambda x: x.endswith('.lat'),
                           os.listdir(cnet_dir)))

    cnet = CnetOld('directory')
    for fn in cnet_list:
        cnet.load(fn)

    # there is not speech duration
    assert cnet.speech_duration == 0.0

    stm = load_stm(test_stm_filename)
    word_list = stm.get_word_list()

    # assert len(word_list) == 8118

    new_uttrs = set(cnet.to_new_uttrs())
    assert len(new_uttrs) == cnet.uttr_count

    new_ref_uttrs = stm.new_uttrs
    assert len(new_ref_uttrs) == stm.num_uttrs
    assert stm.num_uttrs == cnet.uttr_count

    cnetIndex = SlfIndex(new_uttrs)
    stmRef = Stm(new_ref_uttrs)

    assert len(cnet.get('THE')) == len(cnetIndex['THE'])
    assert len(cnet.get('DOG')) == len(cnetIndex['DOG'])

    for word in stmRef.word_list:
        old_hyp_list = cnet.get(word)
        len_old_hyp_list = len(old_hyp_list)
        stm.check_truth(word, old_hyp_list)
        old_best_sorted = cnet.get_best_sorted(word)

        matching_uttrs = cnetIndex[word]
        arc_lsts = labeled_uttr_arc_lists(word,
                                          matching_uttrs,
                                          stmRef,
                                          min_match_ratio=0.5)

        best_labeled_arcs = []
        num_arc_sets = 0
        for uttr_arcs in arc_lsts:
            num_arc_sets += 1
            best_arc, num_arcs, num_no_time_match = select_best_arc(uttr_arcs)
            if not best_arc:
                continue
            best_labeled_arcs.append(best_arc)
        sorted_best_arcs = sorted(best_labeled_arcs, key=lambda l_arc: l_arc.score, reverse=True)

        assert len_old_hyp_list == len(matching_uttrs) == num_arc_sets
        assert len(old_best_sorted) == len(sorted_best_arcs)
        for old, new in zip(old_best_sorted, sorted_best_arcs):
            if old.confidence != new.score:
                print('Not equal: {} {}'.format(old, new))
                # for o, n in zip(old_best_sorted, sorted_best_arcs):
                #     print(o, n)
                assert False
