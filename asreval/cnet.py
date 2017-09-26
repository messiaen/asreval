from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import *
import re
import gzip
import os
from collections import defaultdict
from collections import namedtuple


CnetEdge = namedtuple('CnetEdge', ['start_node',
                                   'end_node',
                                   'start_time',
                                   'end_time',
                                   'word',
                                   'score'])

__LabeledCnetEdge = namedtuple('LabeledCnetEdge', ['arc',
                                                   'matches_time',
                                                   'matches_word'])


class LabeledCnetEdge(__LabeledCnetEdge):
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
        return super().__hash__() + 39 * hash((self.arc, self.matches_time, self.matches_word))

    def __eq__(self, other):
        this_tuple = (self.arc, self.matches_time, self.matches_word)
        other_tuple = (other.arc, other.matches_time, other.matches_word)
        return this_tuple == other_tuple


class CnetIndex(object):
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


class CnetUtterance(object):
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
        return hash((self.audio_id, self.channel, self.start_time, self.end_time))

    def __repr__(self):
        edge_lst = []
        for w, edges in self._edges.items():
            edge_lst.extend(edges)
        return 'CnetUtterance({0}, {1}, {2}, channel={3}, uttr_id={4})'.format(
            self._start, self._end, tuple(set(edge_lst)), self._channel, self._audio_id
        )


class CnetOld(object):
    def __init__(self, use_channel):
        self.words = defaultdict(lambda: defaultdict(list))
        self.start_times = defaultdict(float)
        self.speech_duration = 0
        self.last_node_id = None
        self.use_channel = use_channel

        self.uttr_count = 0

        self.new_edges = []
        self.new_utterances = []

    def to_new_uttrs(self):
        return self.new_utterances

    def __set_channel(self, filename):
        if self.use_channel == 'directory':
            basedir = os.path.basename(
                os.path.abspath(os.path.join(filename, os.pardir)))
            index = basedir.find('-')
            self.channel = basedir[index + 1] if index is not -1 else None
        elif self.use_channel == 'file':
            basename = os.path.basename(filename)
            index = basename.find('-')
            self.channel = basename[index + 1:index + 2]
        else:
            self.channel = None

    def load(self, filename):
        self.__set_channel(filename)

        if '.gz' in filename:
            with gzip.open(filename, 'rb') as fin:
                self.__process_file(fin)
        else:
            with open(filename, 'r') as fin:
                self.__process_file(fin)

    def __process_file(self, fin):
        has_uttr = False
        for line in fin:
            if self.__match_speech_duration(line):
                continue

            if self.__match_utterance(line):
                self.utterance = Utterance(self.audio_id, self.channel, None,
                                           None, None)
                has_uttr = True
                continue

            if self.__match_utt_info(line):
                continue

            if self.__match_node(line):
                continue

            if self.__match_edge(line):
                continue

            if 0 in self.start_times:
                self.utterance.start = self.start_times[0]

            if self.last_node_id in self.start_times:
                self.utterance.end = self.start_times[self.last_node_id]

            if has_uttr:
                self.new_utterances.append(CnetUtterance(
                    self.start_times[self.last_node_id],
                    self.start_times[0],
                    self.new_edges,
                    channel=self.channel,
                    audio_id=self.utterance.audio_id
                ))
                self.new_edges = []

    speech_duration_re = re.compile(
        '# <speech_duration>(.*)</speech_duration>')

    def __match_speech_duration(self, line):
        match = self.speech_duration_re.match(line)
        if match:
            self.speech_duration += float(match.group(1))
            return True
        return False

    utt_re = re.compile('UTTERANCE=(.*)')

    def __match_utterance(self, line):
        match = self.utt_re.match(line)
        if match:
            self.uttr_count += 1
            self.audio_id = match.group(1)
            return True
        return False

    utt_info_re = re.compile('N=(\d+)\s+L=(\d+)')

    def __match_utt_info(self, line):
        match = self.utt_info_re.match(line)
        if match:
            self.last_node_id = int(match.group(1)) - 1
            self.last_edge_id = int(match.group(2)) - 1
            return True
        return False

    node_re = re.compile('I=(\S+)\s+t=(\S+)')

    def __match_node(self, line):
        match = self.node_re.match(line)
        if match:
            node_id = int(match.group(1))
            if node_id is 0:
                self.start_times = defaultdict(float)
            self.start_times[node_id] = float(match.group(2))
            return True
        return False

    edge_re = re.compile('J=\S+\s+S=(\S+)\s+E=(\S+)\s+W=(.*)\s+v=\S+\s+a=\S+\s+l=\S+\s+s=(\S+)')

    def __match_edge(self, line):
        match = self.edge_re.match(line)

        if match:
            start_node_id = int(match.group(1))
            end_node_id = int(match.group(2))
            word = match.group(3)
            confidence = float(match.group(4))

            # Skip silence and start or end of speech
            if word is '-' or '<' in word:
                return True

            new_edge = Edge(self.start_times[start_node_id],
                            self.start_times[end_node_id],
                            confidence,
                            False,
                            False)

            self.new_edges.append(CnetEdge(
                start_node_id,
                end_node_id,
                self.start_times[start_node_id],
                self.start_times[end_node_id],
                word,
                confidence))

            self.words[word][self.utterance].append(new_edge)
            return True
        return False

    def get(self, word):
        return self.words[word]

    def get_best_sorted(self, word):
        best = []
        for utt in self.words[word]:
            current = self.words[word][utt][0]
            for hyp in self.words[word][utt]:
                if hyp.found and hyp.confidence > current.confidence:
                    current = hyp
            best.append(current)
        return sorted(best, key=lambda edge: edge.confidence, reverse=True)


class Edge(object):
    def __init__(self, start, end, confidence, correct=False, found=False):
        self.start = float(start)
        self.end = float(end)
        self.confidence = float(confidence)
        self.correct = bool(correct)
        self.found = bool(found)

    def __repr__(self):
        return str(self)

    def __str__(self):
        s = "Start: {}, End: {}, Confidence {}, Correct: {}"
        return s.format(self.start,
                        self.end,
                        self.confidence,
                        self.correct)


class Utterance(object):
    def __init__(self, audio_id, channel, start, end, elements):
        self.audio_id = audio_id
        self.channel = channel
        self.start = float(start) if start else None
        self.end = float(end) if end else None
        self.elements = list(elements) if elements else None

    def add_element(self, element):
        self.elements.append(element)
