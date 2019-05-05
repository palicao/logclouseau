import logging
from datetime import timedelta, datetime
from typing import Dict, Any

from src.channel import Channel
from src.expression import TokensAwareExpressionCompiler, CompilerError


class Alert:
    def __init__(self, channel: Channel, condition: str, identifier: str,
                 grace: timedelta, min_occurrences: int,
                 message: str):
        self._channel = channel
        self._condition = condition
        self._identifier = identifier
        self._compiler = TokensAwareExpressionCompiler()
        self._grace = grace
        self._min_occurrences = min_occurrences
        self._message = message
        self._occurrence: Dict[str, int] = dict()
        self._end_grace: Dict[str, datetime] = dict()

    def evaluate(self, tokens: Dict[str, Any], line: str) -> None:
        try:
            compiled = self._compiler.compile(self._condition, tokens)
            if compiled:
                self.__send_alert(tokens, line)
        except BaseException as ex:
            logging.error(f'Error: {ex}')

    def __send_alert(self, tokens: Dict[str, Any], line: str) -> None:
        """
        Sends an alert if it's not in the grace_time and if it happened at
        least min_occurrences
        """
        ident = self._identifier.format(**tokens)
        msg = self._message.format(**tokens)
        try:
            self._occurrence[ident] += 1
        except KeyError:
            self._occurrence[ident] = 1

        if self._occurrence[ident] < self._min_occurrences:
            logging.debug(
                f'skipping message "{msg}", line "{line}" '
                f'because number of occurences '
                f'{self._occurrence[ident]} is less '
                f'than the minimum {self._min_occurrences}'
            )
            return

        if ident not in self._end_grace or \
                self._end_grace[ident] < datetime.now():
            self._end_grace[ident] = datetime.now() + self._grace
            self._channel.alert(msg, line)
            self._occurrence[ident] = 0
        else:
            logging.debug(
                f'skipping message "{msg}", line {line} because in grace '
                f'period till {self._end_grace[ident]}'
            )
