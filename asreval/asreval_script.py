from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import int
from builtins import filter
from builtins import map
from builtins import open
from builtins import str
from future import standard_library
standard_library.install_aliases()
import os
import re
import io
import argparse
import gzip
import sys
import six

from asreval.slf import SlfIndex
from asreval.parse import parse_cnet_utterances
from asreval.parse import parse_stm_utterances
from asreval.parse import parse_ctm_utterances
from asreval.stm import Stm
from asreval.mean_average_precision import kws_mean_ave_precision
from asreval.word_uttr_scores import word_lst_uttr_scores

from collections import defaultdict
from collections import OrderedDict


gzip_open = gzip.open
if six.PY2:
    def py2_gzip_open(fn, mode, encoding='utf-8'):
        with gzip.open(fn, 'rb') as f:
            return io.StringIO(f.read().decode('utf-8'))
    gzip_open = py2_gzip_open


def word_list_from_ref_uttrs(stm_uttrs):
    word_list = OrderedDict()
    for uttr in stm_uttrs:
        for word in uttr.words:
            word_list[word] = True
    return list(word_list)


def load_stm(truth_file):
    return Stm(load_stm_uttrs(truth_file))


def load_stm_uttrs(truth_file):
    with open(truth_file, 'r', encoding='utf-8') as f:
        return list(parse_stm_utterances(f))


def load_ctm(truth_file, max_uttr_len=15.0, max_silence=3.0):
        return Stm(load_ctm_uttrs(
            truth_file,
            max_uttr_len=max_uttr_len,
            max_silence=max_silence))


def load_ctm_uttrs(truth_file, max_uttr_len=15.0, max_silence=3.0):
    max_len = None
    if max_uttr_len >= 0.0:
        max_len = max_uttr_len

    silence = None
    if max_silence >= 0.0:
        silence = max_silence

    with open(truth_file, 'r', encoding='utf-8') as f:
        return list(parse_ctm_utterances(f, max_len, silence))


def word_score_to_csv_row(score):
    return u','.join(
        map(lambda x: u'' if x is None else str(x),
            [score.audio_id,
             score.channel,
             score.start_time,
             score.end_time,
             score.word,
             score.score,
             score.truth]))


term_id = defaultdict()
xml_line_re = re.compile(
    u'\s*<term termid="(.*)"><termtext>(.*)</termtext>.*',
    re.UNICODE)
dict_line_re = re.compile(u'>(\S+)\s', re.UNICODE)


cnet_uttr_re = re.compile(u'UTTERANCE=((.*)-\d+)', re.UNICODE)


def ext_audio_id(s):
    m = cnet_uttr_re.match(s)
    if m:
        return m.group(2)
    return s


def load_word_list(word_list_file):
    word_list = set()

    with open(word_list_file, 'r', encoding='utf-8') as file:
        if '.dict' in word_list_file:

            for line in file:
                line = line.rstrip()
                match = dict_line_re.match(line)
                word_list.add(match.group(1))

        elif '.xml' in word_list_file:

            for line in file:
                line = line.rstrip()
                match = xml_line_re.match(line)
                if match:
                    term = match.group(2)
                    word_list.add(term)
                    term_id[term] = match.group(1)

        else:

            for line in file:
                line = line.rstrip()
                word_list.add(line)

    return word_list


def extract_channel(filename, use_channel):
    channel = None
    if use_channel == 'directory':
        basedir = os.path.basename(
            os.path.abspath(os.path.join(filename, os.pardir)))
        index = basedir.find('-')
        channel = basedir[index + 1] if index is not -1 else None
    elif use_channel == 'file':
        basename = os.path.basename(filename)
        index = basename.find('-')
        channel = basename[index + 1:index + 2]
    return channel


def load_cnets(cnet_list, use_channel):
    def uttrs():
        with open(cnet_list, 'r', encoding='utf-8') as f:
            for fn in filter(lambda l: len(l) > 0, map(str.strip, f)):
                chn = extract_channel(fn, use_channel)
                if fn.endswith('.gz'):
                    with gzip_open(fn, 'rt', encoding='utf-8') as lines:
                        for u in parse_cnet_utterances(
                                lines,
                                channel=chn,
                                ext_audio_id_fn=ext_audio_id):
                            yield u
                else:
                    with open(fn, 'r', encoding='utf-8') as lines:
                        for u in parse_cnet_utterances(
                                lines,
                                channel=chn,
                                ext_audio_id_fn=ext_audio_id):
                            yield u
    return SlfIndex(uttrs())


def get_arg_parser():
    parser = argparse.ArgumentParser(
        prog='asreval',
        description='Compute Mean Average Precision for KWS')

    parser.add_argument('--term-list',
                        dest='term_list',
                        required=False,
                        help='Calculate mAP for words in this list. If not ' +
                             'given, word list will be all words in the stm. '
                             'Can ' +
                             'be a dictionary xml term list, or a file with '
                             'one ' +
                             'term per line.')

    parser.add_argument('--cnet-list',
                        dest='cnet_list',
                        required=True,
                        help='File containing a list of consensus network ' +
                             'files to calculate mAP for.')

    truth_group = parser.add_mutually_exclusive_group(required=True)

    truth_group.add_argument('--stm',
                             dest='stm',
                             help='File containing the truth for each cnet listed.')

    truth_group.add_argument('--ctm',
                             dest='ctm',
                             help='File containing the truth for each cnet listed.')

    parser.add_argument('--ctm-max-silence',
                        dest='ctm_max_silence',
                        type=float,
                        default=3.0,
                        help='Silence gap in seconds to split utterances when useing a ctm reference (-1.0 for no splitting on silence gap) (default: 3.0).')

    parser.add_argument('--ctm-max-uttr-len',
                        dest='ctm_max_uttr_len',
                        type=float,
                        default=15.0,
                        help='Maximum len in seconds of a single utterance when using a ctm reference (-1.0 for no splitting on max len) (default: 15.0)')

    parser.add_argument('--use-channel',
                        dest='use_channel',
                        required=False,
                        help='\'directory\' if directory containing cnet '
                             'files has \'-<channel>\' appended.' +
                             '\'file\' if cnet file have \'-<channel>\' '
                             'before file extension',
                        choices=['file', 'directory'])

    parser.add_argument('--csv',
                        dest='csv',
                        required=False,
                        help='CSV style output instead of report style',
                        default=False,
                        action='store_true')

    subparsers = parser.add_subparsers(title='subcommands')

    kwsmap_parser = subparsers.add_parser('kwsmap', help='Compute Mean Average Precision for KWS (When outputing csv the first row has the overall MAP)')
    kwsmap_parser.set_defaults(func=run_kwsmap)

    kwsmap_parser.add_argument('--ave-precision-by-term',
                               dest='list_ap',
                               required=False,
                               help='List average precision for each word.',
                               action='store_true')

    word_scores_parser = subparsers.add_parser(
        'wordscores',
        help='Compute scores for each word utterance pair (Outputs csv rows with audio_id,channel,start_time,stop_time,word,score,truth)')
    word_scores_parser.set_defaults(func=run_word_scores)

    return parser


def run_word_scores(args):
    truth_file = args.stm
    if not truth_file:
        truth_file = args.ctm
        stm_uttrs = load_ctm_uttrs(truth_file, args.ctm_max_uttr_len, args.ctm_max_silence)
    else:
        stm_uttrs = load_stm_uttrs(truth_file)

    term_list = []
    if args.term_list:
        term_list = load_word_list(args.term_list)
    else:
        term_list = word_list_from_ref_uttrs(stm_uttrs)

    slf = load_cnets(args.cnet_list, args.use_channel)

    for word_score in word_lst_uttr_scores(term_list, stm_uttrs, slf):
        print(word_score_to_csv_row(word_score))
        sys.stdout.flush()


def run_kwsmap(args):
    truth_file = args.stm
    if not truth_file:
        truth_file = args.ctm
        stm = load_ctm(truth_file, args.ctm_max_uttr_len, args.ctm_max_silence)
    else:
        stm = load_stm(truth_file)

    term_list = []
    if args.term_list:
        term_list = load_word_list(args.term_list)
    else:
        term_list = stm.word_list

    slf = load_cnets(args.cnet_list, args.use_channel)
    results = kws_mean_ave_precision(term_list, slf, stm)

    map_score = results.mean_ave_precision
    word_ap = results.word_ap

    if args.csv:
        for row in kwsmap_results_to_csv(
                stm, slf, term_list, results, list_ap=args.list_ap):
            print(row)
            sys.stdout.flush()
    else:
        print("\n")
        print("Total speech duration (seconds): {}".format(slf.speech_dur))
        print("Total number of terms: {}".format(len(term_list)))
        print("Total possible hits: {}".format(results.total_possible_hits))
        print("Total true positives: {}".format(int(results.total_tp)))
        print("Total false positives: {}".format(int(results.total_fp)))
        print("Total hypotheses not matching reference window: {}".format(
            results.num_no_time_match_hypotheses))
        print("Recall: {}".format(results.recall))
        print("mAP: {}".format(map_score))
        if args.list_ap:
            print("\nAverage Precision for Words:")
            for word in sorted(word_ap):
                print(u'{} {} {}'.format(word,
                                         round(word_ap[word], 4),
                                         stm.uttr_count(word)))

    return 0


def kwsmap_results_csv_header():
    return u','.join([u'word',
              u'map',
              u'utterance count',
              u'total speech dur (sec)',
              u'total terms',
              u'possible hits',
              u'true positives',
              u'false positives',
              u'hypotheses not matching ref window',
              u'recall'])


def kwsmap_results_to_csv(stm, slf, term_list, results, list_ap=False):
    yield kwsmap_results_csv_header()
    yield u','.join(map(str,
                        [u'',
                         results.mean_ave_precision,
                         stm.total_uttr_count,
                         slf.speech_dur,
                         len(term_list),
                         results.total_possible_hits,
                         results.total_tp,
                         results.total_fp,
                         results.num_no_time_match_hypotheses,
                         results.recall]))
    if list_ap:
        for word in sorted(results.word_ap):
            yield ','.join(map(str,
                               [word,
                                round(results.word_ap[word], 4),
                                stm.uttr_count(word),
                                '',
                                '',
                                '',
                                '',
                                '',
                                '',
                                '']))


def main():
    args = get_arg_parser().parse_args()
    try:
        return args.func(args)
    except IOError as e:
        try:
            sys.stdout.flush()
        finally:
            try:
                sys.stdout.close()
            finally:
                try:
                    sys.stderr.flush()
                finally:
                    sys.stderr.close()
    except Exception as e:
        return 1


if __name__ == '__main__':
    sys.exit(main())
