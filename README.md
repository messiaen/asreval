# asreval

A software development tool kit for evaluating ASR and KWS systems

## Install from source

```
$ python setup.py install
```

## Scripts

### compute_map

```
$ asreval --help
usage: asreval [-h] [--term-list TERM_LIST] --cnet-list CNET_LIST
               (--stm STM | --ctm CTM) [--ctm-max-silence CTM_MAX_SILENCE]
               [--ctm-max-uttr-len CTM_MAX_UTTR_LEN]
               [--use-channel {file,directory}] [--csv]
               {wordscores,kwsmap} ...

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
  --ctm CTM             File containing the truth for each cnet listed.
  --ctm-max-silence CTM_MAX_SILENCE
                        Silence gap in seconds to split utterances when useing
                        a ctm reference (-1.0 for no splitting on silence gap)
                        (default: 3.0).
  --ctm-max-uttr-len CTM_MAX_UTTR_LEN
                        Maximum len in seconds of a single utterance when
                        using a ctm reference (-1.0 for no splitting on max
                        len) (default: 15.0)
  --use-channel {file,directory}
                        'directory' if directory containing cnet files has
                        '-<channel>' appended.'file' if cnet file have
                        '-<channel>' before file extension
  --csv                 CSV style output instead of report style

subcommands:
  {wordscores,kwsmap}
    kwsmap              Compute Mean Average Precision for KWS (When outputing
                        csv the first row has the overall MAP)
    wordscores          Compute scores for each word utterance pair (Outputs
                        csv rows with audio_id,channel,start_time,stop_time,wo
                        rd,score,truth)
```

