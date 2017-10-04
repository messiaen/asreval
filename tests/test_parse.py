from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import map
from builtins import open
from builtins import filter
from future import standard_library
standard_library.install_aliases()
import os
import re

from asreval.parse import parse_stm_utterances
from asreval.parse import _parse_cnet_utterance
from asreval.parse import parse_cnet_utterances
from asreval.parse import lines_from_file_list
from asreval.stm import StmUtterance


def test_parse_cnet_utterance():
    test_cnet_file = os.path.join(os.path.dirname(__file__), '3cnets-A/260-123286-0007.lat')
    test_cnet_file2 = os.path.join(os.path.dirname(__file__), '3cnets-A/260-123286-0008.lat')
    uttrs = []
    with open(test_cnet_file, 'r') as f:
        uttrs.append(_parse_cnet_utterance(f, channel='A'))

    with open(test_cnet_file2, 'r') as f:
        uttrs.append(_parse_cnet_utterance(f, channel='A'))
    assert len(uttrs) == 2

    assert uttrs[0].start_time == 0.00
    assert uttrs[0].end_time == 4.53


def test_parse_cnet_uttr():
    s = '''
# comment line
# another comment
UTTERANCE=utt_1234-9

N=8 L=12
I=0 t=13.89
I=1 t=13.89
I=2 t=13.89
I=3 t=13.89
I=4 t=13.89
I=5 t=13.89
I=6 t=13.89
I=7 t=13.89
J=0 S=0 E=1 W=<s> v=0 a=0 l=0 s=0.01021101
J=2 S=0 E=2 W=ALL v=0 a=0 l=0 s=0.00022301
J=3 S=0 E=3 W=THE v=0 a=0 l=0 s=0.00001
J=4 S=1 E=4 W=WORDS v=0 a=0 l=0 s=0.000301
J=5 S=4 E=5 W=BLAH v=0 a=0 l=0 s=0.780001
J=6 S=5 E=6 W=BLAH v=0 a=0 l=0 s=0.30001
J=7 S=6 E=7 W=FOO v=0 a=0 l=0 s=0.99991
J=8 S=6 E=7 W=BAR v=0 a=0 l=0 s=0.88721
J=9 S=6 E=7 W=HELP v=0 a=0 l=0 s=0.5847
J=10 S=0 E=6 W=- v=0 a=0 l=0 s=0.0345
J=11 S=0 E=6 W=</s> v=0 a=0 l=0 s=0.021201

'''
    uttr = _parse_cnet_utterance(iter(s.split('\n')), 'A')

    assert uttr is not None
    assert uttr.audio_id == 'utt_1234-9'

    utt_re = re.compile('UTTERANCE=((.*)-\d+)')
    def ext_id(s):
        m = utt_re.match(s)
        if m:
            return m.group(2)
        return s

    uttr = _parse_cnet_utterance(
        iter(s.split('\n')), 'A', ext_audio_id_fn=ext_id)
    assert uttr is not None
    assert uttr.audio_id == 'utt_1234'



def test_parse_cnet_utterances():
    cnet_dir = os.path.join(os.path.dirname(__file__), '3cnets-A')

    cnet_list = map(lambda fn: os.path.join(cnet_dir, fn),
                    filter(lambda x: x.endswith('.lat'),
                           os.listdir(cnet_dir)))

    line_iter = lines_from_file_list(cnet_list)
    uttrs = list(parse_cnet_utterances(line_iter, channel='A'))

    assert len(uttrs) == 24


def test_stream_stm_utterances():
    test_stm_filename = os.path.join(os.path.dirname(__file__), '3test.stm')
    with open(test_stm_filename, 'r') as f:
        uttrs = list(parse_stm_utterances(f))

    assert len(uttrs) == 24

    assert uttrs[0] == StmUtterance(
        0.0,
        5.415,
        'UNDERSCORE THESE WORDS FOR THEY ARE FULL OF COMFORT FOR SORE CONSCIENCES'.split(),
        audio_id='2830-3980-0063',
        channel='A')

    assert uttrs[16] == StmUtterance(
        0.0,
        3.06,
        'TUESDAY AUGUST EIGHTEENTH'.split(),
        audio_id='260-123286-0020',
        channel='A')


def test_stream_stm_utterances_unk():
    test_stm_filename = os.path.join(os.path.dirname(__file__), '3test_unk.stm')
    with open(test_stm_filename, 'r') as f:
        uttrs = list(parse_stm_utterances(f))

    assert len(uttrs) == 24

    assert uttrs[0] == StmUtterance(
        0.0,
        5.415,
        '<unk> UNDERSCORE THESE WORDS FOR THEY ARE FULL OF COMFORT FOR SORE CONSCIENCES'.split(),
        audio_id='2830-3980-0063',
        channel='A')
