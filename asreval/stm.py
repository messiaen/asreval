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


class Stm(object):
    def __init__(self):
        self.utts = defaultdict(lambda: defaultdict(list))
        self.not_found = Counter()
        self.utt_count = Counter()
        self.word_list = []  # list of words in STM

    utt_re = re.compile(
        '(.*)\s+(.*)\s+.*\s+(\d+.\d+)\s+(\d+.\d+)\s+<.*>\s+(.*)')

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
        duration = hypothesis_end - hypothesis_start
        return (duration - min(duration, max(0, self.start - hypothesis_start))
                - min(duration, max(0, hypothesis_end - self.end))) / duration

    def __str__(self):
        s = "Audio Id: {}, Start: {}, End: {}, Word Ids: {}"
        return s.format(self.audio_id, self.start, self.end, self.word_idxs)
