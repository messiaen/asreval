import re
import gzip
import os
from collections import defaultdict

class Cnet():


    def __init__(self, use_channel):
        self.words = defaultdict(lambda : defaultdict(list))
        self.start_times = defaultdict(list)
        self.speech_duration = 0
        self.last_node_id = None
        self.use_channel = use_channel


    def __set_channel(self, filename):
        if self.use_channel == 'directory':
            basedir = os.path.basename(os.path.abspath(os.path.join(filename, os.pardir)))
            index = basedir.find('-')
            self.channel = basedir[index + 1] if index is not -1 else None
        elif self.use_channel == 'file':
            basename = os.path.basename(filename)
            index = basename.find('-')
            self.channel = basename[index+1:index+2]
        else:
            self.channel = None


    def load(self, filename):
        self.__set_channel(filename)

        if '.gz' in filename:
            with gzip.open(filename, 'rb') as fin:
                self.__process_file(fin)
        else:
            with open(filename, 'r') as fin:
                self.__process_file(file)


    def __process_file(self, fin):
        for line in fin:
            if self.__match_speech_duration(line):
                continue

            if self.__match_utterance(line):
                self.utterance = Utterance(self.audio_id, self.channel, None, None, None)
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


    speech_duration_re = re.compile('# <speech_duration>(.*)</speech_duration>')
    def __match_speech_duration(self, line):
        match = self.speech_duration_re.match(line)
        if match:
            self.speech_duration += float(match.group(1))
            return True
        return False


    utt_re = re.compile('UTTERANCE=((.*)-\d+)')
    def __match_utterance(self, line):
        match = self.utt_re.match(line)
        if match:
            self.audio_id = match.group(2)
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
        

    node_re = re.compile('I=(\d+) t=(\d+.\d+)')
    def __match_node(self, line):
        match = self.node_re.match(line)
        if match:
            node_id = int(match.group(1))
            if node_id is 0:
                self.start_times = defaultdict()
            self.start_times[node_id] = float(match.group(2))
            return True
        return False


    edge_re = re.compile('J=\d+\s+S=(\d+)\s+E=(\d+)\s+W=(.*)\s+v=\d+\s+a=\d+\s+l=\d+\s+s=(-?\d+\.\d+)')
    def __match_edge(self, line):
        match = self.edge_re.match(line)

        if match:
            start_node_id = int(match.group(1))
            end_node_id = int(match.group(2))
            word = unicode(match.group(3), encoding='utf-8')
            confidence = float(match.group(4))

            # Skip silence and start or end of speech
            if word is '-' or '<' in word:
                return True

            new_edge = Edge(self.start_times[start_node_id],
                                                         self.start_times[end_node_id],
                                                         confidence,
                                                         False,
                                                         False)

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
        return sorted(best, key=lambda edge : edge.confidence, reverse=True)


class Edge():

    def __init__(self, start, end, confidence, correct=False, found=False):
        self.start = float(start)
        self.end = float(end)
        self.confidence = float(confidence)
        self.correct = bool(correct)
        self.found = bool(found)


    def __str__(self):
        str = "Start: {}, End: {}, Confidence {}, Correct: {}"
        return str.format(self.start,
                          self.end,
                          self.confidence,
                          self.correct)

class Utterance():

    def __init__(self, audio_id, channel, start, end, elements):
        self.audio_id = audio_id
        self.channel = channel
        self.start = float(start) if start else None
        self.end = float(end) if end else None
        self.elements = list(elements) if elements else None


    def add_element(self, element):
        self.elements.append(element)
