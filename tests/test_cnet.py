import collections

from asreval.cnet import SlfEdge
from asreval.cnet import LabeledSlfEdge
from asreval.cnet import SlfIndex
from asreval.cnet import SlfUtterance


def test_CnetUtterance_init():
    u = SlfUtterance(0.0,
                     4.34,
                     [SlfEdge(1, 2, 0.0, 1.0, 'a', 0.234)], 'A', '1234')

    assert u.start_time == 0.0
    assert u.end_time == 4.34

    assert u['a'] == [SlfEdge(1, 2, 0.0, 1.0, 'a', 0.234)]

    assert u.channel == 'A'
    assert u.audio_id == '1234'


def test_LabeledCnetEdge():
    l = LabeledSlfEdge(SlfEdge(6, 7, 1.0, 4.0, 'WORD1', 0.99), True, True)
    assert l.arc == SlfEdge(6, 7, 1.0, 4.0, 'WORD1', 0.99)
    assert l.matches_time is True
    assert l.matches_word is True


def test_CnetIndex():
    edges1 = (SlfEdge(1, 2, 0.0, 1.0, 'the', 0.6),
              SlfEdge(1, 2, 0.0, 1.0, 'that', 0.7),
              SlfEdge(2, 3, 0.0, 1.0, 'cat', 0.8),
              SlfEdge(2, 4, 0.0, 1.0, 'dog', 0.3),
              SlfEdge(4, 5, 0.0, 1.0, 'ran', 0.4))

    edges2 = (SlfEdge(1, 2, 0.0, 1.0, 'the', 0.6),
              SlfEdge(1, 2, 0.0, 1.0, 'a', 0.7),
              SlfEdge(2, 3, 0.0, 1.0, 'bird', 0.8),
              SlfEdge(2, 4, 0.0, 1.0, 'dog', 0.3))

    edges3 = (SlfEdge(1, 2, 0.0, 1.0, 'how', 0.6),
              SlfEdge(2, 3, 0.0, 1.0, 'did', 0.8),
              SlfEdge(2, 4, 0.0, 1.0, 'you', 0.3),
              SlfEdge(4, 5, 0.0, 1.0, 'no', 0.4))

    uttrs = (SlfUtterance(0.0, 1.0, edges1),
             SlfUtterance(0.0, 1.0, edges2),
             SlfUtterance(0.0, 1.0, edges3))

    cnetIndex = SlfIndex(uttrs)

    assert len(cnetIndex.words) == 11

    assert cnetIndex['the'] == [SlfUtterance(0.0, 1.0, edges1),
                                SlfUtterance(0.0, 1.0, edges2)]

    assert cnetIndex['a'] == [SlfUtterance(0.0, 1.0, edges2)]

    assert len(cnetIndex['foo']) == 0

