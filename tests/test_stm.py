from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import zip
from future import standard_library
standard_library.install_aliases()
from asreval.stm import StmUtterance
from asreval.stm import Stm


def test_StmUtterance():
    words = ['hi', 'here', 'is', 'a', 'test', 'utterance']
    uttr = StmUtterance(4.0,
                        8.0,
                        words,
                        channel='C',
                        audio_id='asdf')

    assert uttr.audio_id == 'asdf'
    assert uttr.start_time == 4.0
    assert uttr.end_time == 8.0
    assert uttr.channel == 'C'

    for w in words:
        assert w in uttr

    for expected, actual in zip(words, uttr.words):
        assert expected == actual

    assert uttr.time_match_ratio(6.0, 10.0) == 0.5


def test_Stm():
    w1 = ['the', 'quick', 'brown', 'fox']
    w2 = ['foxes', 'are', 'very', 'neat']
    w3 = ['cats', 'seem', 'neat', 'also']

    all_words = {'the', 'quick', 'brown', 'fox', 'foxes', 'are', 'very',
                 'neat', 'cats', 'seem', 'neat', 'also'}

    u1 = StmUtterance(3.23, 6.89, w1, audio_id='1234', channel='A')
    u2 = StmUtterance(5.87, 9.00, w2, audio_id='1234', channel='A')
    u3 = StmUtterance(34.97, 39.87, w3, audio_id='7654', channel='B')

    ref = Stm((u1, u2, u3))

    assert ref.word_list == all_words
    assert ref.uttr_count('fox') == 1
    assert ref.uttr_count('neat') == 2
    assert ref.uttr_count('newword') == 0

    assert ref.uttrs('1234', 'A') == [u1, u2]
    assert ref.uttrs('9999', 'A') == []



