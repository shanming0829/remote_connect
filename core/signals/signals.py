# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import re

from com.parse_html import parse_html

signals = parse_html()
seq_compile = re.compile(r'^<CTRL-(\S)>$')


class SignalException(Exception):
    pass


def get_signal_by_seq(seq):
    """
    <CTRL-C> --> \x30
    :param seq:
    :return: signal char
    """
    match = seq_compile.match(seq)
    if not match:
        raise SignalException('Currently not support {} signal yet.'.format(seq))

    match_seq = '^{}'.format(match.group(1).upper())

    for signal in signals:
        if match_seq == signal.seq:
            return chr(signal.decimal)


def get_signal_by_abbreviation(abbreviation):
    """
    ETX --> \x30
    :param abbreviation:
    :return: signal char
    """
    for signal in signals:
        if signal.abbreviation == abbreviation:
            return chr(signal.decimal)


if __name__ == '__main__':
    print(get_signal_by_abbreviation('ETX'))
    print(get_signal_by_seq('<CTRL-c>'))
