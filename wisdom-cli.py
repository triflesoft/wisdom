#!/usr/bin/python3

from logging import info
from logging.config import dictConfig
from os.path import join
from sys import argv
from time import perf_counter_ns
from time import sleep

from wisdom.arguments import Arguments
from wisdom.configuration import Configuration
from wisdom.source import Source
from wisdom.output import Output


def process(arguments):
    configuration = Configuration(arguments)
    time_nano_from = perf_counter_ns()
    source = Source(arguments, configuration)
    source.discover()
    output = Output(arguments, configuration, source)
    output.generate_static()
    output.generate_jinja2()
    time_nano_till = perf_counter_ns()
    span_nano = time_nano_till - time_nano_from
    span_micro = span_nano // 1000
    span_milli = span_micro // 1000
    total_full = span_milli // 1000
    total_milli = span_milli % 1000
    info(f'{total_full} seconds {total_milli} milliseconds elapsed.')


def main():
    arguments = Arguments()
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s [%(levelname)-8s] %(pathname)s:%(lineno)s (%(funcName)s) %(message)s',
                'datefmt': "%Y-%m-%d %H:%M:%S",
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': max(0, 10 * (4 - arguments.verbosity_level)),
            },
            'file': {
                'backupCount': 14,
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': join(arguments.output_path, 'wisdom-cli.log'),
                'formatter': 'default',
                'level': 'DEBUG',
                'when': 'midnight',
            },
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    })
    info('wisdom-cli "%s"', '" "'.join(argv))


    if arguments.inotify:
        from inotify.adapters import InotifyTree
        from inotify.constants import IN_CLOSE_WRITE

        inotify = InotifyTree(arguments.source_path, IN_CLOSE_WRITE, 24*60*60)

        while True:
            process(arguments)

            for e in inotify.event_gen():
                if e:
                    _, _, path, name = e
                    info('inotify "%s/%s"', path, name)
                else:
                    break
            sleep(0.1)

    else:
        process(arguments)

if __name__ == '__main__':
    main()
