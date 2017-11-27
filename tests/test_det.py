from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import numpy as np
import os
import matplotlib

from asreval.parse import lines_from_file_list
from asreval.parse import parse_cnet_utterances
from asreval.det import compute_det_curve
from asreval import SlfIndex
from asreval import parse_stm_utterances
from asreval import word_lst_uttr_scores
from asreval.word_uttr_scores import truth_and_scores


def test_compute_det_curve():
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
    actual_word_scores = word_lst_uttr_scores(['I'], ref_utterances, cnetIndex)
    actual_word_scores_lst = list(actual_word_scores)

    actual_truth, actual_scores = truth_and_scores(actual_word_scores_lst)

    expected_fps = np.array([0.1666, 0.1666, 0.1666, 0.1111, 0.0555, 0.0, 0.0, 0.0, 0.0])
    expected_fns = np.array([0.0, 0.2, 0.4, 0.4, 0.4, 0.4, 0.6, 0.8, 1.0])

    actual_fps, actual_fns, thresholds = compute_det_curve(actual_truth, actual_scores)

    assert np.allclose(expected_fps, actual_fps, atol=1.0e-03)
    assert np.allclose(expected_fns, actual_fns, atol=1.0e-03)
