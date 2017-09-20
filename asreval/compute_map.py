import argparse
import re
import sys
from collections import defaultdict
from asreval import Stm
from asreval import Cnet


class MAP:
    def __init__(self, word_list, hypothesis, ref):
        self.word_list = word_list
        self.hypothesis = hypothesis
        self.ref = ref
        self.total_tp = 0
        self.total_fp = 0
        self.total_possible_hits = 0

    def compute_map(self):
        word_ap = {}  # map of words to their average precisions
        ap_sum = 0  # sum of average precisions calculated
        num_aps = 0  # number of average precisions calculated

        for word in self.word_list:

            num_true = self.ref.get_num_utts(word)
            if not num_true:
                continue
            self.total_possible_hits += num_true

            hyp_list = self.hypothesis.get(word)
            if hyp_list:
                self.ref.check_truth(word, hyp_list)
                sorted_hyps = self.hypothesis.get_best_sorted(word)
                ap = self.average_precision_for_word(sorted_hyps, num_true)
            else:
                ap = 0

            ap_sum += ap
            word_ap[word] = ap
            num_aps += 1

        try:
            map = ap_sum / num_aps
        except ZeroDivisionError as e:
            sys.stderr.write("Error: no terms in term list found in STM\n")
            sys.exit(1)

        return (map, word_ap)

    def average_precision_for_word(self, hyp_list, num_true):
        total = 0.0  # sum of precisions for each occurance of a word
        ctp = 0.0  # cumulative true positives (with higher confidence)
        cfp = 0.0  # cumulative false positives (with higher confidence)

        i = 0
        while i < len(hyp_list):
            elt = hyp_list[i]
            conf = elt.confidence

            tp = 0.0  # true positives with current confidence
            fp = 0.0  # false positives with current confidence

            # Tie Breaking: when we have true positives and false positives
            # with the same confidence, we want to deterministically evenly
            # distribute them throughout the range of occurances with the
            # same confidence
            while conf == elt.confidence:
                if elt.correct:
                    tp += 1
                else:
                    fp += 1

                i += 1
                if i >= len(hyp_list):
                    break
                elt = hyp_list[i]

            if tp:
                for x in range(1, int(tp) + 1):
                    total += (ctp + x) / (ctp + x + cfp + fp / tp * x)
            ctp += tp
            cfp += fp

        self.total_tp += ctp
        self.total_fp += cfp

        return total / num_true


def load_stm(truth_file):
    ref = Stm()
    ref.load(truth_file)
    return ref


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


def load_cnets(cnet_list, use_channel):
    hypothesis = Cnet(use_channel)

    with  open(cnet_list, 'r') as file:
        for cnet_file in file:
            cnet_file = cnet_file.strip()
            hypothesis.load(cnet_file)

    return hypothesis


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
    term_list = load_word_list(
        args.term_list) if args.term_list else stm.get_word_list()
    cnet = load_cnets(args.cnet_list, args.use_channel)
    mAP = MAP(term_list, cnet, stm)

    map_score, word_ap = mAP.compute_map()

    print("\n")
    print("Total speech duration (seconds): {}".format(cnet.speech_duration))
    print("Total number of terms: {}".format(len(term_list)))
    print("Total possible hits: {}".format(mAP.total_possible_hits))
    print("Total true positives: {}".format(int(mAP.total_tp)))
    print("Total false positives: {}".format(int(mAP.total_fp)))
    print("Total hypotheses not matching STM window: {}".format(
        sum(stm.not_found.values())))
    print("Recall: {}".format(mAP.total_tp / mAP.total_possible_hits))
    print("mAP: {}".format(map_score))
    if args.list_ap:
        print("\nAverage Precision for Words:")
        for word in sorted(word_ap):
            print(u'{} {} {}'.format(word, word_ap[word], stm.utt_count[word]))


if __name__ == '__main__':
    main()
