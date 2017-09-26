from collections import Counter
from collections import namedtuple

from asreval.slf import LabeledSlfEdge


__all__ = ['KwsMapResults',
           'kws_mean_ave_precision']


KwsMapResults = namedtuple('KwsMapResults', ['mean_ave_precision',
                                             'word_ap',
                                             'total_tp',
                                             'total_fp',
                                             'total_possible_hits',
                                             'arc_counts',
                                             'no_time_match_counts'])


def kws_mean_ave_precision(word_list, hypothesis, ref, min_match_ratio=0.5):
    total_possible_hits = 0
    no_time_match_counts = Counter()
    arc_counts = Counter()
    total_tp = 0
    total_fp = 0
    word_ap = {}
    sum_ap = 0.0
    num_aps = 0

    for query_word in word_list:
        true_count = ref.uttr_count(query_word)
        if true_count < 1:
            continue
        total_possible_hits += true_count

        matching_uttrs = hypothesis[query_word]
        if len(matching_uttrs) < 1:
            num_aps += 1
            word_ap[query_word] = 0
            continue
        arc_lsts = labeled_uttr_arc_lists(query_word,
                                          matching_uttrs,
                                          ref,
                                          min_match_ratio=min_match_ratio)

        best_labeled_arcs = []
        for uttr_arcs in arc_lsts:
            best_arc, num_arcs, num_no_time_match = select_best_arc(uttr_arcs)
            if not best_arc:
                continue
            best_labeled_arcs.append(best_arc)
            if num_no_time_match > 0:
                no_time_match_counts.update({query_word: num_no_time_match})
            if num_arcs > 0:
                arc_counts.update({query_word: num_arcs})
        sorted_best_arcs = sorted(best_labeled_arcs,
                                  key=lambda l_arc: l_arc.score,
                                  reverse=True)

        ap, ctp, cfp = word_ave_precision(sorted_best_arcs, true_count)

        sum_ap += ap
        word_ap[query_word] = ap
        num_aps += 1
        total_tp += ctp
        total_fp += cfp

    if num_aps < 1:
        raise Exception('No terms in term list found in STM')
    return KwsMapResults(sum_ap / num_aps,
                         word_ap,
                         total_tp,
                         total_fp,
                         total_possible_hits,
                         arc_counts,
                         no_time_match_counts)


def word_ave_precision(labeled_arcs, num_true):
    rank_n_tp = 0.0
    rank_n_fp = 0.0

    word_ap = 0.0

    for tp, fp in _tied_tp_fp(labeled_arcs):
        if tp > 0:
            for j in range(1, int(tp) + 1):
                word_ap += ((rank_n_tp + j)
                            / (rank_n_tp + j + rank_n_fp + fp / tp * j))
        rank_n_tp += tp
        rank_n_fp += fp

    return word_ap / num_true, rank_n_tp, rank_n_fp


def _tied_tp_fp(sorted_labeled_arcs):
    arc_iter = iter(sorted_labeled_arcs)
    arc, _, matches_word = next(arc_iter)

    while True:
        tp = 0.0
        fp = 0.0
        score = arc.score

        try:
            while score == arc.score:
                if matches_word:
                    tp += 1
                else:
                    fp += 1
                arc, _, matches_word = next(arc_iter)
        except StopIteration as e:
            yield tp, fp
            raise e

        yield tp, fp


def select_best_arc(labeled_arcs):
    num_arcs = 0
    num_no_time_match = 0
    max_time_match_arc = None
    max_arc = None

    try:
        first_arc = next(labeled_arcs)
        if first_arc.matches_time:
            max_time_match_arc = first_arc
        else:
            num_no_time_match += 1
        num_arcs += 1
        max_arc = first_arc
    except StopIteration:
        return None, 0, 0

    for l_arc in labeled_arcs:
        num_arcs += 1
        if not l_arc.matches_time:
            num_no_time_match += 1
        elif max_time_match_arc is None:
            max_time_match_arc = l_arc
        elif l_arc.score > max_time_match_arc.score:
            max_time_match_arc = l_arc

        if l_arc.score > max_arc.score:
            max_arc = l_arc

    if max_time_match_arc is not None:
        return max_time_match_arc, num_arcs, num_no_time_match
    else:
        return max_arc, num_arcs, num_no_time_match


def labeled_uttr_arc_lists(query_word, hyp_uttrs, ref, min_match_ratio=0.5):
    for hyp_uttr in hyp_uttrs:
        yield labeled_arc_matches(hyp_uttr[query_word],
                                  hyp_uttr.audio_id,
                                  hyp_uttr.channel,
                                  ref,
                                  min_match_ratio=min_match_ratio)


def labeled_arc_matches(arcs, audio_id, channel, ref, min_match_ratio=0.5):
        for arc in arcs:
            has_time_match = False
            has_word_match = False
            max_ratio = min_match_ratio

            for ref_uttr in ref.uttrs(audio_id, channel):
                time_match_ratio = ref_uttr.time_match_ratio(
                    arc.start_time,
                    arc.end_time)
                if time_match_ratio > max_ratio:
                    max_ratio = time_match_ratio
                    has_time_match = True
                    has_word_match = arc.word in ref_uttr
            yield LabeledSlfEdge(arc, has_time_match, has_word_match)
