from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import filter
from builtins import next
from builtins import open
from builtins import int
from builtins import str
from future import standard_library
standard_library.install_aliases()
import re

from asreval.slf import SlfEdge
from asreval.slf import SlfUtterance
from asreval.stm import StmUtterance


__all__ = ['parse_stm_utterances',
           'parse_cnet_utterances']

# TODO this parses some subset / extension of standard slf and stm files
# Refactor to handle standard slf and stms files.  Allow users to pass in
# special processing functions like ext_audio_id (see compute_map.py).

cnet_uttr_re = re.compile('UTTERANCE=(.*)')
cnet_uttr_info_re = re.compile('N=(\d+)\s+L=(\d+)')
cnet_node_re = re.compile('I=(\S+)\s+t=(\S+)')
cnet_edge_re = re.compile(
    'J=(\S+)+\s+S=(\S+)\s+E=(\S+)\s+W=(.*)\s+v=\S+\s+a=\S+\s+l=\S+\s+s=(\S+)')


stm_uttr_re = re.compile(
    '^(.*)\s+(.*)\s+.*\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+<.*>\s+(.*)')


def parse_stm_utterances(lines):
    for line in filter(lambda l: len(l) > 0, lines):
        if line.startswith(';;'):
            continue
        m = stm_uttr_re.match(line)
        if m:
            audio_id = m.group(1)
            channel = m.group(2)
            start = float(m.group(3))
            end = float(m.group(4))
            words = m.group(5).split()
            yield StmUtterance(start,
                               end,
                               words,
                               channel=channel,
                               audio_id=audio_id)
        else:
            raise Exception('Invalid stm line {}'.format(line))


def lines_from_file_list(file_names):
    for fn in file_names:
        with open(fn, 'r') as f:
            for l in f:
                yield l


def parse_cnet_utterances(lines, channel=None, ext_audio_id_fn=None):
    while True:
        yield _parse_cnet_utterance(
            lines, channel=channel, ext_audio_id_fn=ext_audio_id_fn)


def _parse_cnet_utterance(lines, channel=None, ext_audio_id_fn=None):
    start_times = {}
    last_node_id = None
    last_edge_id = None
    edges = []
    audio_id = None

    while True:
        line = next(lines).strip()
        if len(line) < 1 or line.startswith('#'):
            continue

        match_uttr = cnet_uttr_re.match(line)
        if match_uttr:
            if not ext_audio_id_fn:
                audio_id = str(match_uttr.group(1))
            else:
                audio_id = ext_audio_id_fn(line)

        match_uttr_info = cnet_uttr_info_re.match(line)
        if match_uttr_info:
            last_node_id = int(match_uttr_info.group(1)) - 1
            last_edge_id = int(match_uttr_info.group(2)) - 1

        match_node = cnet_node_re.match(line)
        if match_node:
            start_times[int(match_node.group(1))] = float(match_node.group(2))

        match_edge = cnet_edge_re.match(line)
        if match_edge:
            edge_id = int(match_edge.group(1))
            start_node_id = int(match_edge.group(2))
            end_node_id = int(match_edge.group(3))
            word = str(match_edge.group(4))
            score = float(match_edge.group(5))

            if word != '-' and '<' not in word:
                edges.append(SlfEdge(start_node_id,
                                     end_node_id,
                                     start_times[start_node_id],
                                     start_times[end_node_id],
                                     word,
                                     score))

            if edge_id == last_edge_id:
                return SlfUtterance(start_times[0],
                                    start_times[last_node_id],
                                    edges,
                                    audio_id=audio_id,
                                    channel=channel)

