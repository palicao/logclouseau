import logging
from datetime import timedelta, datetime

from channel import Channel


class Alert(object):
    def __init__(self, channel: Channel, condition: str, identifier: str, grace: timedelta, min_occurrences: int,
                 message: str):
        self.channel = channel
        self.condition = condition
        self.identifier = identifier
        self.grace = grace
        self.min_occurrences = min_occurrences
        self.message = message
        self.occurrence = dict()
        self.end_grace = dict()

    def evaluate(self, tokens: dict, line: str) -> None:
        if eval(self.condition, {}, tokens):
            self.__send_alert(tokens, line)

    def __send_alert(self, tokens: dict, line: str) -> None:
        """
        Sends an alert if it's not in the grace_time and if it happened at least min_occurrences
        """
        ident = eval(self.identifier, {}, tokens)
        msg = eval(self.message, {}, tokens)
        if ident not in self.occurrence:
            self.occurrence[ident] = 0
        self.occurrence[ident] += 1
        if self.occurrence[ident] < self.min_occurrences:
            logging.debug(f'skipping message "{msg}", line "{line}" because number of occurences ' +
                          f'{self.occurrence[ident]} is less than the minimum {self.min_occurrences}')
            return

        if ident not in self.end_grace or self.end_grace[ident] < datetime.now():
            self.end_grace[ident] = datetime.now() + self.grace
            self.channel.alert(msg, line)
            self.occurrence[ident] = 0
        else:
            logging.debug(f'skipping message "{msg}", line {line} because in grace period till {self.end_grace[ident]}')
