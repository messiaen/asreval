from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import *
import re
import gzip
from collections import Counter
from collections import defaultdict
from collections import OrderedDict


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
        other_tuple = (self.start_time,
                       self.end_time,
                       self.words,
                       self.audio_id,
                       self.channel)
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


class StmOld(object):
    def __init__(self):
        self.utts = defaultdict(lambda: defaultdict(list))
        self.not_found = Counter()
        self.utt_count = Counter()
        self.word_list = []  # list of words in STM

        self.new_uttrs = []
        self.num_uttrs = 0

    utt_re = re.compile(
        '(.*)\s+(.*)\s+.*\s+(\S+)\s+(\S+)\s+<.*>\s+(.*)')

    def load(self, filename):

        if '.gz' in filename:
            with gzip.open(filename, 'rb') as fin:
                self.__process_file(fin)
        else:
            with open(filename, 'r') as fin:
                self.__process_file(fin)

    def __process_file(self, fin):
        for line in fin:
            match = self.utt_re.match(line)
            if match:
                self.num_uttrs += 1
                audio_id = match.group(1)
                channel = match.group(2)
                start = float(match.group(3))
                end = float(match.group(4))
                words = match.group(5).split()

                utt_words = []
                for word in words:
                    if word not in self.word_list:
                        self.word_list.append(word)
                    utt_words.append(self.word_list.index(word))

                self.__add_to_utt_count(words)
                self.__add_to_utts(audio_id, channel, start, end, utt_words)

                self.new_uttrs.append(StmUtterance(start, end, words, channel=channel, audio_id=audio_id))
            else:
                print(line)

    def __add_to_utt_count(self, words):
        # Use a set so you only count a word once per utterance
        self.utt_count.update(set(words))

    def __add_to_utts(self, audio_id, channel, start, end, words):
        new_utt = Utterance(None, None, start, end, words)
        self.utts[audio_id][channel].append(new_utt)

    def get_word_list(self):
        return self.word_list

    def check_truth(self, word, hyp):
        word_idx = self.word_list.index(word)

        for utt in hyp:
            for elt in hyp[utt]:
                max_in = .5
                found = False

                if utt.channel:
                    self.mark_truth_with_channel(utt.audio_id, utt.channel,
                                                 elt, word_idx)
                else:
                    self.mark_truth(utt.audio_id, elt, word_idx)

                if not elt.found:
                    self.not_found.update([word_idx])

    def mark_truth_with_channel(self, audio_id, channel, elt, word_idx):
        max_in = .5
        for occurance in self.utts[audio_id][channel]:
            percent = occurance.percent_in(elt.start, elt.end)
            if percent > max_in:
                elt.correct = True if occurance.contains_word(
                    word_idx) else False
                max_in = percent
                elt.found = True

    def mark_truth(self, audio_id, elt, word_idx):
        max_in = .5
        for channel in self.utts[audio_id]:
            for occurance in self.utts[audio_id][channel]:
                percent = occurance.percent_in(elt.start, elt.end)
                if percent > max_in:
                    elt.correct = True if occurance.contains_word(
                        word_idx) else False
                    max_in = percent
                    elt.found = True

    def get_num_utts(self, word):
        if word in self.utt_count:
            return self.utt_count[word]
        return 0


class Utterance(object):
    def __init__(self, audio_id, channel, start, end, word_idxs):
        self.audio_id = audio_id
        self.channel = channel
        self.start = float(start)
        self.end = float(end)
        self.word_idxs = word_idxs

    def contains_word(self, word_idx):
        try:
            self.word_idxs.index(word_idx)
            return True
        except ValueError as err:
            return False

    def percent_in(self, hypothesis_start, hypothesis_end):
        duration = float(hypothesis_end - hypothesis_start)
        # for zero length edge there's nothing to be in
        if duration == 0.0:
            return 1.0 if self.start <= hypothesis_start < self.end else 0.0
            # return 0.0
        return (duration - min(duration, max(0, self.start - hypothesis_start))
                - min(duration, max(0, hypothesis_end - self.end))) / duration

    def __str__(self):
        s = "Audio Id: {}, Start: {}, End: {}, Word Ids: {}"
        return s.format(self.audio_id, self.start, self.end, self.word_idxs)
