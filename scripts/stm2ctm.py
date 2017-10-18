import sys


if __name__ == '__main__':
    fn = sys.argv[1]
    with open(fn, 'r', encoding='utf-8') as f:
        for line in filter(lambda l: len(l) > 0, f):
            if line.startswith(';;'):
                continue
            fields = line.strip().split()
            audio_id = fields[0]
            channel = fields[1]
            start = float(fields[3])
            end = float(fields[4])
            words = fields[6:]

            for word in words:
                print('{0} {1} {2} {3} {4}'.format(
                    audio_id,
                    channel,
                    start,
                    end - start,
                    word))
