import datetime
import logging
import re
from concurrent.futures.thread import ThreadPoolExecutor
from os.path import expanduser
from typing import Dict, Any

import tailer
import toml

from src import channel, utils
from src.alert import Alert
from src.channel import Channel


class Logclouseau:
    _channels: Dict[str, Channel] = dict()
    _alerts: Dict[str, Alert] = dict()
    _config: Dict[str, Any] = dict()

    def __init__(self, config_file, log_level):
        self._config = self.load_config(config_file)
        self.setup_logging(log_level)

    def investigate(self) -> None:
        self.setup_channels(self._config)
        self.setup_alerts(self._config)
        self.evaluate_files(self._config)

    def evaluate_files(self, config):
        """
        Evaluates each file in a different thread
        """
        files = config['file']
        executor = ThreadPoolExecutor(len(files))
        with executor as thread:
            thread.map(self.evaluate_file, files.items())

    def evaluate_file(self, file):
        (file_name, file_config) = file
        regex = utils.tokens_to_pattern(file_config['tokens'])
        with open(expanduser(file_config['path'])) as file:
            for line in tailer.follow(file):
                for alert in self._alerts[file_name].values():
                    matches = re.match(regex, line)
                    if matches:
                        gd = matches.groupdict()
                        alert.evaluate(gd, line)

    def setup_alerts(self, config):
        for alert_name, alert_config in config['alert'].items():
            ch = alert_config.get('channel', 'debug')
            ch = self._channels.get(ch, channel.DebugChannel())
            delta = alert_config.get('grace', 0)
            grace = datetime.timedelta(**delta)
            message = alert_config.get('message', f'Alert {alert_name}')
            min_occurrences = alert_config.get('min_occurrences', 1)
            condition = alert_config.get('condition', 'True')
            identifier = alert_config.get('identifier', alert_name)

            file = alert_config['file']
            if file not in self._alerts:
                self._alerts[file] = dict()
            self._alerts[file][alert_name] = Alert(ch, condition, identifier,
                                                   grace, min_occurrences,
                                                   message)

    def setup_channels(self, config):
        for channel_name, channel_config in config['channel'].items():
            self._channels[channel_name] = \
                channel.ChannelFactory.get_channel(channel_config)

    def setup_logging(self, level: str) -> None:
        """
        Sets up logging according to the command line parameter --log
        """
        numeric_level = getattr(logging, level.upper(), logging.DEBUG)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Invalid log level: {level}')
        logging.basicConfig(level=numeric_level,
                            format='%(asctime)s %(levelname)s %(message)s')

    def load_config(self, config_file: str) -> dict:
        """
        Loads a config file from a toml file and asserts it's valid.
        In order to be valid, a config must have at least 3 keys:
        channel, file, alert.
        Each one of them has its own format.
        The validation of the format is left at the consumer.
        """
        config: Dict[str, Any] = toml.load(config_file)
        utils.assert_dict_contains_keys(config, {'channel', 'file', 'alert'})
        return config
