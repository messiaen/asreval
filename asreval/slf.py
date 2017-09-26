from collections import defaultdict
from collections import namedtuple


__all__ = ['SlfEdge',
           'LabeledSlfEdge',
           'SlfUtterance',
           'SlfIndex']


SlfEdge = namedtuple('CnetEdge', ['start_node',
                                  'end_node',
                                  'start_time',
                                  'end_time',
                                  'word',
                                  'score'])


__LabeledSlfEdge = namedtuple('LabeledCnetEdge', ['arc',
                                                  'matches_time',
                                                  'matches_word'])


class LabeledSlfEdge(__LabeledSlfEdge):
    @property
    def score(self):
        return self.arc.score

    @property
    def start_node(self):
        return self.arc.start_node

    @property
    def end_node(self):
        return self.arc.end_node

    @property
    def start_time(self):
        return self.arc.start_time

    @property
    def end_time(self):
        return self.arc.end_time

    @property
    def word(self):
        return self.arc.word

    def __hash__(self):
        return super().__hash__() + 39 * hash(
            (self.arc, self.matches_time, self.matches_word))

    def __eq__(self, other):
        this_tuple = (self.arc, self.matches_time, self.matches_word)
        other_tuple = (other.arc, other.matches_time, other.matches_word)
        return this_tuple == other_tuple


class SlfIndex(object):
    def __init__(self, utterances):
        self._words = defaultdict(list)
        for uttr in utterances:
            for w, edges in uttr:
                self._words[w].append(uttr)

    @property
    def words(self):
        return self._words

    def __getitem__(self, item):
        if not isinstance(item, str):
            raise TypeError('Key must be a of type str not {}'.format(
                type(item)))
        if item in self.words:
            return self.words[item]
        return []


class SlfUtterance(object):
    def __init__(self, start, end, edges, channel=None, audio_id=None):
        self._start = float(start)
        self._end = float(end)
        self._channel = channel
        self._audio_id = audio_id
        self._edges = defaultdict(list)
        for e in edges:
            self._edges[e.word].append(e)

    @property
    def start_time(self):
        return self._start

    @property
    def end_time(self):
        return self._end

    @property
    def channel(self):
        return self._channel

    @property
    def audio_id(self):
        return self._audio_id

    def __iter__(self):
        return iter(self._edges.items())

    def __getitem__(self, item):
        if not isinstance(item, str):
            raise TypeError('index must be of type str not {}'.format(
                type(item)))
        return self._edges[item]

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        this_tuple = (self._start,
                      self._end,
                      self._channel,
                      self._audio_id,
                      self._edges)

        other_tuple = (other._start,
                       other._end,
                       other._channel,
                       other._audio_id,
                       other._edges)

        return this_tuple == other_tuple

    def __hash__(self):
        return hash(
            (self.audio_id, self.channel, self.start_time, self.end_time))

    def __repr__(self):
        edge_lst = []
        for w, edges in self._edges.items():
            edge_lst.extend(edges)
        return 'SlfUtterance({0}, {1}, {2}, channel={3}, uttr_id={4})'.format(
            repr(self._start),
            repr(self._end),
            repr(tuple(set(edge_lst))),
            repr(self._channel),
            repr(self._audio_id)
        )
