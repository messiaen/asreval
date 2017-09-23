import collections

from asreval.cnet import CnetEdge
from asreval.cnet import CnetIndex
from asreval.cnet import CnetUtterance


def test_CnetUtterance_init():
    u = CnetUtterance(0.0,
                      4.34,
                      [CnetEdge(1, 2, 'a', 0.234)], 'A', '1234')

    assert u.start_time == 0.0
    assert u.end_time == 4.34

    edges = u.edges
    assert isinstance(edges, collections.Iterator)
    for i, e in enumerate(edges):
        assert i < 1
        assert e == CnetEdge(1, 2, 'a', 0.234)

    edges = iter(u)
    assert isinstance(edges, collections.Iterator)
    for i, e in enumerate(edges):
        assert i < 1
        assert e == CnetEdge(1, 2, 'a', 0.234)

    assert u.channel == 'A'
    assert u.uttr_id == '1234'


def test_CnetIndex():
    edges1 = (CnetEdge(1, 2, 'the', 0.6),
             CnetEdge(1, 2, 'that', 0.7),
             CnetEdge(2, 3, 'cat', 0.8),
             CnetEdge(2, 4, 'dog', 0.3),
             CnetEdge(4, 5, 'ran', 0.4))

    edges2 = (CnetEdge(1, 2, 'the', 0.6),
              CnetEdge(1, 2, 'a', 0.7),
              CnetEdge(2, 3, 'bird', 0.8),
              CnetEdge(2, 4, 'dog', 0.3))

    edges3 = (CnetEdge(1, 2, 'how', 0.6),
              CnetEdge(2, 3, 'did', 0.8),
              CnetEdge(2, 4, 'you', 0.3),
              CnetEdge(4, 5, 'no', 0.4))

    uttrs = (CnetUtterance(0.0, 1.0, edges1),
             CnetUtterance(0.0, 1.0, edges2),
             CnetUtterance(0.0, 1.0, edges3))

    cnetIndex = CnetIndex(uttrs)

    assert len(cnetIndex.words) == 11

    assert cnetIndex['the'] == [CnetUtterance(0.0, 1.0, edges1),
                                CnetUtterance(0.0, 1.0, edges2)]

    assert cnetIndex['a'] == [CnetUtterance(0.0, 1.0, edges2)]

    assert len(cnetIndex['foo']) == 0

