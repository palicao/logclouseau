import logging
from datetime import timedelta, datetime

from src.channel import Channel


class Alert(object):
    def __init__(self, channel: Channel, condition: str, identifier: str, grace: timedelta, min_occurrences: int,
                 message: str):
        self._channel = channel
        self._condition = condition
        self._identifier = identifier
        self._grace = grace
        self._min_occurrences = min_occurrences
        self._message = message
        self._occurrence = dict()
        self._end_grace = dict()

    def evaluate(self, tokens: dict, line: str) -> None:
        if eval(self._condition, {}, tokens):
            self.__send_alert(tokens, line)

    def __send_alert(self, tokens: dict, line: str) -> None:
        """
        Sends an alert if it's not in the grace_time and if it happened at least min_occurrences
        """
        ident = eval(self._identifier, {}, tokens)
        msg = eval(self._message, {}, tokens)
        if ident not in self._occurrence:
            self._occurrence[ident] = 0
        self._occurrence[ident] += 1
        if self._occurrence[ident] < self._min_occurrences:
            logging.debug(f'skipping message "{msg}", line "{line}" because number of occurences ' +
                          f'{self._occurrence[ident]} is less than the minimum {self._min_occurrences}')
            return

        if ident not in self._end_grace or self._end_grace[ident] < datetime.now():
            self._end_grace[ident] = datetime.now() + self._grace
            self._channel.alert(msg, line)
            self._occurrence[ident] = 0
        else:
            logging.debug(f'skipping message "{msg}", line {line} because in grace period till {self._end_grace[ident]}')
