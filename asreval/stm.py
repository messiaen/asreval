from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from future.utils import viewitems
from future import standard_library
standard_library.install_aliases()
from collections import Counter
from collections import defaultdict
from collections import OrderedDict


__all__ = ['Stm',
           'StmUtterance']


class Stm(object):
    def __init__(self, utterances):
        self._uttrs = defaultdict(lambda: defaultdict(list))
        self._uttr_counts = Counter()
        for uttr in utterances:
            self._uttrs[uttr.audio_id][uttr.channel].append(uttr)
            self._uttr_counts.update(set(uttr.words))

    @property
    def word_list(self):
        return set(self._uttr_counts)

    def uttr_count(self, word):
        return self._uttr_counts[word]

    def uttrs(self, audio_id, channel):
        # explicitly check for keys so that default dict won't grow
        if audio_id not in self._uttrs:
            return []
        if channel is None:
            uttrs = []
            for c, c_uttrs in viewitems(self._uttrs[audio_id]):
                uttrs.extend(c_uttrs)
            return uttrs
        if channel not in self._uttrs[audio_id]:
            return []
        return self._uttrs[audio_id][channel]


class StmUtterance(object):
    def __init__(self, start, end, words, channel=None, audio_id=None):
        self._words = OrderedDict()
        for w in words:
            self._words[w] = None

        self._audio_id = audio_id
        self._start_time = start
        self._end_time = end
        self._channel = channel

    @property
    def words(self):
        return list(self._words)

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def audio_id(self):
        return self._audio_id

    @property
    def channel(self):
        return self._channel

    def __contains__(self, word):
        return word in self._words

    def __repr__(self):
        return 'StmUtterance({0}, {1}, {2}, audio_id={3}, channel={4})'.format(
            repr(self.start_time),
            repr(self.end_time),
            repr(self.words),
            repr(self.audio_id),
            repr(self.channel))

    def __str__(self):
        return repr(self)

    def __hash__(self):
        return hash((self.start_time,
                     self.end_time,
                     self.words,
                     self.audio_id,
                     self.channel))

    def __eq__(self, o):
        this_tuple = (self.start_time,
                      self.end_time,
                      self.words,
                      self.audio_id,
                      self.channel)
        other_tuple = (o.start_time,
                       o.end_time,
                       o.words,
                       o.audio_id,
                       o.channel)
        return this_tuple == other_tuple

    # TODO clean up
    def time_match_ratio(self, start, stop):
        duration = float(stop - start)
        # If the duration is 0.0 then either the start time is in this uttr
        # or not
        if duration == 0.0:
            return 1.0 if self._start_time <= start < self._end_time else 0.0
            # return 0.0
        return (duration - min(duration, max(0, self._start_time - start))
                - min(duration, max(0, stop - self._end_time))) / duration
