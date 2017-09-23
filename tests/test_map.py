import os

from asreval.compute_map import MAP
from asreval.compute_map import load_stm
from asreval.cnet import Cnet


def test_map_orig():
    test_stm_filename = os.path.join(os.path.dirname(__file__), 'test.stm')
    cnet_dir = os.path.join(os.path.dirname(__file__), 'testcnets-A')

    cnet_list = map(lambda fn: os.path.join(cnet_dir, fn),
                    filter(lambda x: x.endswith('.lat'),
                           os.listdir(cnet_dir)))

    cnet = Cnet('directory')
    for fn in cnet_list:
        cnet.load(fn)

    # there is not speech duration
    assert cnet.speech_duration == 0.0

    stm = load_stm(test_stm_filename)
    word_list = stm.get_word_list()

    assert len(word_list) == 8118

    comp_map = MAP(word_list, cnet, stm)
    map_score, word_ap = comp_map.compute_map()

    assert comp_map.total_possible_hits == 45544
    assert comp_map.total_fp == 55332
    assert comp_map.total_tp == 43733
    assert sum(stm.not_found.values()) == 2692
    assert abs(map_score - 0.77445) < 0.00001

