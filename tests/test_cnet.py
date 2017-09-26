import collections

from asreval.cnet import CnetEdge
from asreval.cnet import LabeledCnetEdge
from asreval.cnet import CnetIndex
from asreval.cnet import CnetUtterance


def test_CnetUtterance_init():
    u = CnetUtterance(0.0,
                      4.34,
                      [CnetEdge(1, 2, 0.0, 1.0, 'a', 0.234)], 'A', '1234')

    assert u.start_time == 0.0
    assert u.end_time == 4.34

    assert u['a'] == [CnetEdge(1, 2, 0.0, 1.0, 'a', 0.234)]

    assert u.channel == 'A'
    assert u.audio_id == '1234'


def test_LabeledCnetEdge():
    l = LabeledCnetEdge(CnetEdge(6, 7, 1.0, 4.0, 'WORD1', 0.99), True, True)
    assert l.arc == CnetEdge(6, 7, 1.0, 4.0, 'WORD1', 0.99)
    assert l.matches_time is True
    assert l.matches_word is True


def test_CnetIndex():
    edges1 = (CnetEdge(1, 2, 0.0, 1.0, 'the', 0.6),
              CnetEdge(1, 2, 0.0, 1.0, 'that', 0.7),
              CnetEdge(2, 3, 0.0, 1.0, 'cat', 0.8),
              CnetEdge(2, 4, 0.0, 1.0, 'dog', 0.3),
              CnetEdge(4, 5, 0.0, 1.0, 'ran', 0.4))

    edges2 = (CnetEdge(1, 2, 0.0, 1.0, 'the', 0.6),
              CnetEdge(1, 2, 0.0, 1.0, 'a', 0.7),
              CnetEdge(2, 3, 0.0, 1.0, 'bird', 0.8),
              CnetEdge(2, 4, 0.0, 1.0, 'dog', 0.3))

    edges3 = (CnetEdge(1, 2, 0.0, 1.0, 'how', 0.6),
              CnetEdge(2, 3, 0.0, 1.0, 'did', 0.8),
              CnetEdge(2, 4, 0.0, 1.0, 'you', 0.3),
              CnetEdge(4, 5, 0.0, 1.0, 'no', 0.4))

    uttrs = (CnetUtterance(0.0, 1.0, edges1),
             CnetUtterance(0.0, 1.0, edges2),
             CnetUtterance(0.0, 1.0, edges3))

    cnetIndex = CnetIndex(uttrs)

    assert len(cnetIndex.words) == 11

    assert cnetIndex['the'] == [CnetUtterance(0.0, 1.0, edges1),
                                CnetUtterance(0.0, 1.0, edges2)]

    assert cnetIndex['a'] == [CnetUtterance(0.0, 1.0, edges2)]

    assert len(cnetIndex['foo']) == 0

