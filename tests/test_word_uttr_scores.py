from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import os
from future import standard_library

from asreval.parse import lines_from_file_list
from asreval.parse import parse_cnet_utterances

standard_library.install_aliases()
import numpy as np

from asreval import StmUtterance
from asreval import SlfIndex
from asreval import parse_stm_utterances
from asreval import SlfEdge
from asreval import SlfUtterance
from asreval import word_uttr_scores
from asreval import word_lst_uttr_scores
from asreval import WordUttrScore
from asreval.word_uttr_scores import max_word_score
from asreval.word_uttr_scores import truth_and_scores


def test_max_score():
    words = ['hi', 'here', 'is', 'a', 'test', 'utterance']
    uttr = StmUtterance(4.0,
                        8.0,
                        words,
                        channel='C',
                        audio_id='asdf')

    edges1 = (SlfEdge(1, 2, 0.0, 1.0, 'the', 0.6),
              SlfEdge(1, 2, 0.0, 1.0, 'that', 0.7),
              SlfEdge(2, 3, 0.0, 1.0, 'cat', 0.8),
              SlfEdge(2, 4, 0.0, 1.0, 'dog', 0.3),
              SlfEdge(4, 5, 0.0, 1.0, 'ran', 0.4))

    edges2 = (SlfEdge(1, 2, 0.0, 1.0, 'the', 0.6),
              SlfEdge(1, 2, 0.0, 1.0, 'a', 0.7),
              SlfEdge(2, 3, 6.0, 9.0, 'utterance', 0.8),
              SlfEdge(2, 3, 6.0, 9.0, 'utterance', 0.7),
              SlfEdge(2, 3, 1.0, 2.0, 'utterance', 0.9),
              SlfEdge(2, 4, 0.0, 1.0, 'dog', 0.3))

    edges3 = (SlfEdge(1, 2, 0.0, 1.0, 'how', 0.6),
              SlfEdge(2, 3, 4.0, 8.0, 'utterance', 0.9),
              SlfEdge(2, 4, 0.0, 1.0, 'you', 0.3),
              SlfEdge(4, 5, 0.0, 1.0, 'no', 0.4))

    hyp_uttrs = (SlfUtterance(0.0, 1.0, edges1, audio_id='asdf', channel='C'),
                 SlfUtterance(0.0, 1.0, edges2, audio_id='asdf', channel='C'),
                 SlfUtterance(0.0, 1.0, edges3, audio_id='lkjh', channel='C'))

    cnetIndex = SlfIndex(hyp_uttrs)

    assert 0.8 == max_word_score('utterance', uttr, cnetIndex)


def test_target_scores():
    test_stm_filename = os.path.join(os.path.dirname(__file__), '3test.stm')
    with open(test_stm_filename, 'r') as f:
        ref_utterances = list(parse_stm_utterances(f))

    cnet_dir = os.path.join(os.path.dirname(__file__), '3cnets-A')

    cnet_list = map(lambda fn: os.path.join(cnet_dir, fn),
                    filter(lambda x: x.endswith('.lat'),
                           os.listdir(cnet_dir)))

    line_iter = lines_from_file_list(cnet_list)
    cnet_uttrs = list(parse_cnet_utterances(line_iter, channel='A'))

    assert len(cnet_uttrs) == 24
    assert len(ref_utterances) == 24

    cnetIndex = SlfIndex(cnet_uttrs)

    expected_scores = [
        WordUttrScore('2830-3980-0063', 'A', 'I', 0.0, 0),
        WordUttrScore('2830-3980-0064', 'A', 'I', 0.0, 0),
        WordUttrScore('2830-3980-0065', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0007', 'A', 'I', 1.53451e-6, 0),
        WordUttrScore('260-123286-0008', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0009', 'A', 'I', 8.52933e-06, 1),
        WordUttrScore('260-123286-0010', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0011', 'A', 'I', 4.69459e-06, 0),
        WordUttrScore('260-123286-0012', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0013', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0014', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0015', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0016', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0017', 'A', 'I', 9.77185e-05, 1),
        WordUttrScore('260-123286-0018', 'A', 'I', 0.00172956, 1),
        WordUttrScore('260-123286-0019', 'A', 'I', 3.84432e-07, 1),
        WordUttrScore('260-123286-0020', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0021', 'A', 'I', 6.23947e-07, 1),
        WordUttrScore('260-123286-0022', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0023', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0024', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0025', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0026', 'A', 'I', 1.18413e-06, 0),
        WordUttrScore('260-123286-0027', 'A', 'I', 2.30856e-05, 1)
    ]

    actual_scores = list(word_uttr_scores('I', ref_utterances, cnetIndex))
    assert expected_scores == actual_scores

    assert expected_scores[0].audio_id == actual_scores[0].audio_id
    assert expected_scores[0].channel == actual_scores[0].channel
    assert expected_scores[0].word == actual_scores[0].word
    assert expected_scores[0].score == actual_scores[0].score
    assert expected_scores[0].truth == actual_scores[0].truth

    expected_scores = [
        WordUttrScore('2830-3980-0063', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('2830-3980-0064', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('2830-3980-0065', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0007', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0008', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0009', 'A', 'PROFESSOR', 0.000618948, 1),
        WordUttrScore('260-123286-0010', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0011', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0012', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0013', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0014', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0015', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0016', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0017', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0018', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0019', 'A', 'PROFESSOR', 8.69463e-05, 1),
        WordUttrScore('260-123286-0020', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0021', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0022', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0023', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0024', 'A', 'PROFESSOR', 0.031387, 1),
        WordUttrScore('260-123286-0025', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0026', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0027', 'A', 'PROFESSOR', 0.0, 0)
    ]

    actual_scores = word_uttr_scores('PROFESSOR', ref_utterances, cnetIndex)
    assert expected_scores == list(actual_scores)


def test_word_lst_target_scores():
    test_stm_filename = os.path.join(os.path.dirname(__file__), '3test.stm')
    with open(test_stm_filename, 'r') as f:
        ref_utterances = list(parse_stm_utterances(f))

    cnet_dir = os.path.join(os.path.dirname(__file__), '3cnets-A')

    cnet_list = map(lambda fn: os.path.join(cnet_dir, fn),
                    filter(lambda x: x.endswith('.lat'),
                           os.listdir(cnet_dir)))

    line_iter = lines_from_file_list(cnet_list)
    cnet_uttrs = list(parse_cnet_utterances(line_iter, channel='A'))

    assert len(cnet_uttrs) == 24
    assert len(ref_utterances) == 24

    cnetIndex = SlfIndex(cnet_uttrs)

    expected_scores = [
        WordUttrScore('2830-3980-0063', 'A', 'I', 0.0, 0),
        WordUttrScore('2830-3980-0064', 'A', 'I', 0.0, 0),
        WordUttrScore('2830-3980-0065', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0007', 'A', 'I', 1.53451e-6, 0),
        WordUttrScore('260-123286-0008', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0009', 'A', 'I', 8.52933e-06, 1),
        WordUttrScore('260-123286-0010', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0011', 'A', 'I', 4.69459e-06, 0),
        WordUttrScore('260-123286-0012', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0013', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0014', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0015', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0016', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0017', 'A', 'I', 9.77185e-05, 1),
        WordUttrScore('260-123286-0018', 'A', 'I', 0.00172956, 1),
        WordUttrScore('260-123286-0019', 'A', 'I', 3.84432e-07, 1),
        WordUttrScore('260-123286-0020', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0021', 'A', 'I', 6.23947e-07, 1),
        WordUttrScore('260-123286-0022', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0023', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0024', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0025', 'A', 'I', 0.0, 0),
        WordUttrScore('260-123286-0026', 'A', 'I', 1.18413e-06, 0),
        WordUttrScore('260-123286-0027', 'A', 'I', 2.30856e-05, 1),
        WordUttrScore('2830-3980-0063', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('2830-3980-0064', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('2830-3980-0065', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0007', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0008', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0009', 'A', 'PROFESSOR', 0.000618948, 1),
        WordUttrScore('260-123286-0010', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0011', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0012', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0013', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0014', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0015', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0016', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0017', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0018', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0019', 'A', 'PROFESSOR', 8.69463e-05, 1),
        WordUttrScore('260-123286-0020', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0021', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0022', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0023', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0024', 'A', 'PROFESSOR', 0.031387, 1),
        WordUttrScore('260-123286-0025', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0026', 'A', 'PROFESSOR', 0.0, 0),
        WordUttrScore('260-123286-0027', 'A', 'PROFESSOR', 0.0, 0)
    ]

    actual_scores = list(word_lst_uttr_scores(['I', 'PROFESSOR'], ref_utterances, cnetIndex))
    assert expected_scores == actual_scores

    assert expected_scores[0].audio_id == actual_scores[0].audio_id
    assert expected_scores[0].channel == actual_scores[0].channel
    assert expected_scores[0].word == actual_scores[0].word
    assert expected_scores[0].score == actual_scores[0].score
    assert expected_scores[0].truth == actual_scores[0].truth


def test_truth_and_scores():
    test_stm_filename = os.path.join(os.path.dirname(__file__), '3test.stm')
    with open(test_stm_filename, 'r') as f:
        ref_utterances = list(parse_stm_utterances(f))

    cnet_dir = os.path.join(os.path.dirname(__file__), '3cnets-A')

    cnet_list = map(lambda fn: os.path.join(cnet_dir, fn),
                    filter(lambda x: x.endswith('.lat'),
                           os.listdir(cnet_dir)))

    line_iter = lines_from_file_list(cnet_list)
    cnet_uttrs = list(parse_cnet_utterances(line_iter, channel='A'))

    assert len(cnet_uttrs) == 24
    assert len(ref_utterances) == 24

    cnetIndex = SlfIndex(cnet_uttrs)
    actual_word_scores = word_lst_uttr_scores(['I', 'PROFESSOR'], ref_utterances, cnetIndex)
    actual_word_scores_lst = list(actual_word_scores)

    expected_truth = np.zeros(48, dtype='int')
    expected_truth[5] = 1
    expected_truth[13] = 1
    expected_truth[14] = 1
    expected_truth[15] = 1
    expected_truth[17] = 1
    expected_truth[23] = 1
    expected_truth[29] = 1
    expected_truth[39] = 1
    expected_truth[44] = 1

    expected_scores = np.zeros(48, dtype='float64')
    expected_scores[3] = actual_word_scores_lst[3].score
    expected_scores[5] = actual_word_scores_lst[5].score
    expected_scores[7] = actual_word_scores_lst[7].score
    expected_scores[13] = actual_word_scores_lst[13].score
    expected_scores[14] = actual_word_scores_lst[14].score
    expected_scores[15] = actual_word_scores_lst[15].score
    expected_scores[17] = actual_word_scores_lst[17].score
    expected_scores[22] = actual_word_scores_lst[22].score
    expected_scores[23] = actual_word_scores_lst[23].score
    expected_scores[29] = actual_word_scores_lst[29].score
    expected_scores[39] = actual_word_scores_lst[39].score
    expected_scores[44] = actual_word_scores_lst[44].score

    actual_truth, actual_scores = truth_and_scores(actual_word_scores_lst)

    assert np.all(expected_truth == actual_truth)
    assert np.all(expected_scores == actual_scores)
