import logging
from datetime import timedelta, datetime
from re import Pattern

from channel import Channel


class Alert(object):
    __name: str
    __regex: Pattern
    __channel: Channel
    __grace_period: timedelta
    __end_grace: datetime
    __min_occurrences: int
    __occurrence: int

    def __init__(self, name: str, regex: Pattern, channel: Channel, grace_period: timedelta, message: str, min_occurrences):
        self.__name = name
        self.__regex = regex
        self.__channel = channel
        self.__grace_period = grace_period
        self.__end_grace = datetime.now()
        self.__message = message
        self.__min_occurrences = min_occurrences
        self.__occurrence = 0

    def evaluate(self, line: str):
        if self.__regex.search(line):
            self.__send_alert(line)

    def __send_alert(self, line: str) -> None:
        """
        Sends an alert if it's not in the grace_time and if it happened at least min_occurrences
        """
        self.__occurrence = self.__occurrence + 1
        if self.__occurrence < self.__min_occurrences:
            logging.debug(f'skipping message "{self.__message}" for line "{line}" because number of occurences {self.__occurrence} is less than the minimum {self.__min_occurrences}')
            return

        if self.__grace_period is None or self.__end_grace < datetime.now():
            self.__end_grace = datetime.now()
            self.__channel.alert(self.__message, line)
            self.__occurrence = 0
        else:
            logging.debug(f'skipping message "{self.__message}" for line "{line}" because in grace period')
