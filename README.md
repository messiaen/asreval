# asreval

A software development tool kit for evaluating ASR and KWS systems

## Install from source

```
$ python setup.py install
```

## Scripts

### compute_map

```
$ compute_map --help

usage: compute_map [-h] [--term-list TERM_LIST] --cnet-list CNET_LIST --stm
                   STM [--ave-precision-by-term]
                   [--use-channel {file,directory}]

Compute Mean Average Precision for KWS

optional arguments:
  -h, --help            show this help message and exit
  --term-list TERM_LIST
                        Calculate mAP for words in this list. If not given,
                        word list will be all words in the stm. Can be a
                        dictionary xml term list, or a file with one term per
                        line.
  --cnet-list CNET_LIST
                        File containing a list of consensus network files to
                        calculate mAP for.
  --stm STM             File containing the truth for each cnet listed.
  --ave-precision-by-term
                        List average precision for each word.
  --use-channel {file,directory}
                        'directory' if directory containing cnet files has
                        '-<channel>' appended.'file' if cnet file have
                        '-<channel>' before file extension
```

