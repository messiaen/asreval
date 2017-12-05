from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from collections import namedtuple


__all__ = [
    'word_lst_uttr_scores',
    'word_uttr_scores',
    'max_word_score'
]


WordUttrScore = namedtuple(
    'WordUttrScore',
    'audio_id channel start_time end_time word score truth')


def word_lst_uttr_scores(words, ref_uttrs, hypothesis):
    for word in words:
        for row in word_uttr_scores(word, ref_uttrs, hypothesis):
            yield row


def word_uttr_scores(word, ref_uttrs, hypothesis):
    for ref in ref_uttrs:
        score = max_word_score(word, ref, hypothesis)
        truth = 1 if word in ref else 0
        yield WordUttrScore(
            ref.audio_id,
            ref.channel,
            ref.start_time,
            ref.end_time,
            word,
            score,
            truth)


def max_word_score(word, ref, hypothesis):
    score = 0.0
    for hyp in hypothesis[word]:
        if hyp.audio_id == ref.audio_id and hyp.channel == ref.channel:
            for edge in hyp[word]:
                if ref.time_match_ratio(edge.start_time, edge.end_time) > 0.5:
                    score = max(score, edge.score)
    return score


# TODO for now we just output word uttr csv rows
# def truth_and_scores(word_scores):
#     truths = []
#     scores = []
#     for _, _, _, _, _, score, truth in word_scores:
#         truths.append(truth)
#         scores.append(score)
#
#     return np.array(truths, dtype='int'), np.array(scores, dtype='float64')
