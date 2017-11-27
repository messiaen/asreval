from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from builtins import range
from builtins import next
from builtins import int

import os
from future import standard_library

from asreval import SlfIndex, word_lst_uttr_scores
from asreval.parse import lines_from_file_list, \
    parse_cnet_utterances, parse_stm_utterances
from asreval.word_uttr_scores import truth_and_scores
from asreval.det import compute_det_curve
from asreval.det import plot_det

standard_library.install_aliases()
import numpy as np
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_stm_filename = os.path.join(os.path.dirname(__file__), '..', 'tests', '3test.stm')
    with open(test_stm_filename, 'r') as f:
        ref_utterances = list(parse_stm_utterances(f))

    cnet_dir = os.path.join(os.path.dirname(__file__), '..', 'tests', '3cnets-A')

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
    actual_truth, actual_scores = truth_and_scores(actual_word_scores_lst)
    fps, fns, _ = compute_det_curve(actual_truth, actual_scores)

    plot_det(fps, fns)
