import os
import re
import argparse
import gzip

from asreval.slf import SlfIndex
from asreval.parse import parse_cnet_utterances
from asreval.parse import parse_stm_utterances
from asreval.stm import Stm
from asreval.mean_average_precision import kws_mean_ave_precision

from collections import defaultdict


def load_stm(truth_file):
    with open(truth_file, 'r', encoding='utf-8') as f:
        return Stm(parse_stm_utterances(f))


term_id = defaultdict()
xml_line_re = re.compile('\s*<term termid="(.*)"><termtext>(.*)</termtext>.*')
dict_line_re = re.compile('>(\S+)\s')


def load_word_list(word_list_file):
    word_list = set()

    with open(word_list_file, 'r') as file:
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
                if fn.endswith('.lat'):
                    with open(fn, 'r', encoding='utf-8') as lines:
                        yield from parse_cnet_utterances(lines, channel=chn)
                elif fn.endswith('.gz'):
                    with gzip.open(fn, 'rt', encoding='utf-8') as lines:
                        yield from parse_cnet_utterances(lines, channel=chn)
                else:
                    raise Exception('Unrecognized file format {}'.format(fn))
    return SlfIndex(uttrs())


def parse_args():
    parser = argparse.ArgumentParser(
        prog='compute_map',
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

    parser.add_argument('--stm',
                        dest='stm',
                        required=True,
                        help='File containing the truth for each cnet listed.')

    parser.add_argument('--ave-precision-by-term',
                        dest='list_ap',
                        required=False,
                        help='List average precision for each word.',
                        action='store_true')

    parser.add_argument('--use-channel',
                        dest='use_channel',
                        required=False,
                        help='\'directory\' if directory containing cnet '
                             'files has \'-<channel>\' appended.' +
                             '\'file\' if cnet file have \'-<channel>\' '
                             'before file extension',
                        choices=['file', 'directory'])

    return parser.parse_args()


def main():
    args = parse_args()

    stm = load_stm(args.stm)
    term_list = []
    if args.term_list:
        term_list = load_word_list(args.term_list)
    else:
        term_list = stm.word_list

    slf = load_cnets(args.cnet_list, args.use_channel)
    results = kws_mean_ave_precision(term_list, slf, stm)

    map_score = results.mean_ave_precision
    word_ap = results.word_ap

    print("\n")
    print("Total speech duration (seconds): {}".format(slf.speech_dur))
    print("Total number of terms: {}".format(len(term_list)))
    print("Total possible hits: {}".format(results.total_possible_hits))
    print("Total true positives: {}".format(int(results.total_tp)))
    print("Total false positives: {}".format(int(results.total_fp)))
    print("Total hypotheses not matching STM window: {}".format(
        sum(results.no_time_match_counts.values())))
    print("Recall: {}".format(results.total_tp / results.total_possible_hits))
    print("mAP: {}".format(map_score))
    if args.list_ap:
        print("\nAverage Precision for Words:")
        for word in sorted(word_ap):
            print(u'{} {} {}'.format(word,
                                     word_ap[word],
                                     stm.uttr_count(word)))


if __name__ == '__main__':
    main()
