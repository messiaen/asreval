from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from builtins import range
from builtins import next
from builtins import int

from future import standard_library
standard_library.install_aliases()
import logging
import numpy as np
import matplotlib.pyplot as plt


def compute_det_curve(y_true, y_scores):
    # convert y_true to boolean vector
    y_true = y_true == 1
    logging.debug('true: {}'.format(y_true))
    logging.debug('score: {}'.format(y_scores))

    # sort y_scores and y_true by score desc
    desc_score_idx = np.argsort(y_scores)[::-1]
    y_scores = y_scores[desc_score_idx]
    y_true = y_true[desc_score_idx]
    logging.debug('true: {}'.format(y_true))
    logging.debug('score: {}'.format(y_scores))

    uniq_val_idx = np.where(np.diff(y_scores))[0]
    threshold_idx = np.r_[uniq_val_idx, y_true.size - 1]
    logging.debug('uniq_val: {}'.format(uniq_val_idx))
    logging.debug('thres_idxs: {}'.format(threshold_idx))

    thresholds = y_scores[threshold_idx]

    tps = np.cumsum(y_true)[threshold_idx]
    fps = 1 + threshold_idx - tps
    fns = tps[-1] - tps

    tp_count = tps[-1]
    tn_count = (fps[-1] - fps)[0]

    last_idx = tps.searchsorted(tps[-1]) + 1
    first_idx = fps[::-1].searchsorted(fps[0])
    thres_idxs = list(range(first_idx, last_idx))[::-1]
    return (fps[thres_idxs] / tp_count,
            fns[thres_idxs] / tn_count,
            thresholds[thres_idxs])


def plot_det(fps, fns):
    print(fps)
    print(fns)
    plt.figure()
    plt.plot(fps, fns)
    plt.show()
