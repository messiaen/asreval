import os

from asreval.parse import parse_stm_utterances
from asreval.parse import parse_cnet_utterance
from asreval.parse import parse_cnet_utterances
from asreval.parse import lines_from_file_list
from asreval.stm import StmUtterance


def test_parse_cnet_utterance():
    test_cnet_file = os.path.join(os.path.dirname(__file__), '3cnets-A/260-123286-0007.lat')
    test_cnet_file2 = os.path.join(os.path.dirname(__file__), '3cnets-A/260-123286-0008.lat')
    uttrs = []
    with open(test_cnet_file, 'r') as f:
        uttrs.append(parse_cnet_utterance(f, channel='A'))

    with open(test_cnet_file2, 'r') as f:
        uttrs.append(parse_cnet_utterance(f, channel='A'))
    assert len(uttrs) == 2

    assert uttrs[0].start_time == 0.00
    assert uttrs[0].end_time == 4.53


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
