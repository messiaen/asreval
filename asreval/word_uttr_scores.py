from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
import math
from collections import namedtuple


__all__ = [
    'word_lst_uttr_scores',
    'word_uttr_scores',
    'max_word_score'
]


WordUttrScore = namedtuple(
    'WordUttrScore',
    'audio_id channel start_time end_time word score truth')


score_converters = {
    'raw': lambda x: x,
    'posterior': lambda x: x,
    'log10': lambda x: 10 ** x,
    'log2': lambda x: 2 ** x,
    'ln': lambda x: math.e ** x
}


def word_lst_uttr_scores(
        words,
        ref_uttrs,
        hypothesis,
        convert_fn=None,
        default_score=0.0):
    for word in words:
        for row in word_uttr_scores(
                word,
                ref_uttrs,
                hypothesis,
                convert_fn=convert_fn,
                default_score=default_score):
            yield row


def word_uttr_scores(
        word,
        ref_uttrs,
        hypothesis,
        convert_fn=None,
        default_score=0.0):
    for ref in ref_uttrs:
        score = max_word_score(
            word,
            ref,
            hypothesis,
            convert_fn=convert_fn,
            default_score=default_score)
        truth = 1 if word in ref else 0
        yield WordUttrScore(
            ref.audio_id,
            ref.channel,
            ref.start_time,
            ref.end_time,
            word,
            score,
            truth)


def max_word_score(word, ref, hypothesis, convert_fn=None, default_score=0.0):
    score = None
    for hyp in hypothesis[word]:
        if hyp.audio_id == ref.audio_id and hyp.channel == ref.channel:
            for edge in hyp[word]:
                if ref.time_match_ratio(edge.start_time, edge.end_time) > 0.5:
                    if (isinstance(convert_fn, str)
                            and convert_fn in score_converters):
                        curr_score = score_converters[convert_fn](edge.score)
                    elif callable(convert_fn):
                        curr_score = convert_fn(edge.score)
                    else:
                        curr_score = edge.score
                    if score is None:
                        score = curr_score
                    else:
                        score = max(score, curr_score)
    if score is None:
        return default_score
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
