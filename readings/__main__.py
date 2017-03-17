"""CLI entry point for readings.

usage:
    readings term [options]
    readings web [options]
    readings topocket <login> <password> [options]
    readings [options]


options:

    -h, --help          print this message
    -v, --version       print version
    --age=TIME          stories have at most 1 TIME (hour/day/week) [default: today]
    --min-score=INT     stories have a score of INT+ [default: 100]

"""

from functools import partial
from readings import readings
from readings import Preferences
from readings.readers import browser_reader


if __name__ == "__main__":
    from docopt import docopt

    args = docopt(__doc__, version=0.1)
    age = args['--age']
    min_score = int(args['--min-score'])

    called = partial(readings, max_per_topic=10)

    if args['topocket']:
        raise NotImplementedError("Pocket interface not implemented.")
    elif args['term']:
        pass  # nothing to do
    elif args['web']:
        called = partial(called, reader=browser_reader)

    if age:
        EXPECTED_AGES = {'hour', 'today', 'week'}
        if age not in EXPECTED_AGES:
            raise ValueError("Given age (--age option) is not in {}. '{}' is "
                             "invalid.".format(', '.join(EXPECTED_AGES), age))
        called = partial(called, timeframe=getattr(Preferences.time, age))

    # call the resulting function with remaining options
    called(minimal_score=min_score)
