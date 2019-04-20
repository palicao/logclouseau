import argparse
import datetime
import re

import tailer
import toml
import logging

from alert import Alert
import channel

channels = dict()
files = dict()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    setup_logging(args.log)

    for name, channel_config in config['channel'].items():
        channels[name] = channel.ChannelFactory.get_channel(channel_config)

    for name, file_config in config['file'].items():
        files[name] = open(file_config['path'])

    for name, alert_config in config['alert'].items():
        regex = re.compile(alert_config['regex'])
        if alert_config['channel'] in channels:
            ch = channels[alert_config['channel']]
        else:
            ch = channel.DebugChannel()
        delta = alert_config['grace']
        message = alert_config['message']
        grace = datetime.timedelta(**delta)
        min_occurrences = alert_config['min_occurrences']

        alert = Alert(name, regex, ch, grace, message, min_occurrences)

        file = files[alert_config['file']]
        for line in tailer.follow(file):
            alert.evaluate(line)
            if regex.search(line):
                alert.evaluate(line)


def setup_logging(level: str) -> None:
    """
    Sets up logging according to the command line parameter --log
    """
    numeric_level = getattr(logging, level.upper(), logging.DEBUG)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    logging.basicConfig(level=numeric_level, format='%(asctime)s %(levelname)s %(message)s')


def load_config(config_file: str) -> dict:
    """
    Loads a config file from a toml file and asserts it's valid.
    In order to be valid, a config must have at least 3 keys: channel, file, alert.
    Each one of them has its own format. The validation of the format is left at the consumer.
    """
    config = toml.load(config_file)
    mandatory_keys = {'channel', 'file', 'alert'}
    assert mandatory_keys.issubset(config.keys())
    return config


def parse_args() -> argparse.Namespace:
    """
    Parses command line arguments (currently only --config)
    """
    parser = argparse.ArgumentParser(description='LogClouseau inspect your logs and reacts accordingly')
    parser.add_argument('-c', '--config', type=str, help='config file path (defaults to ./logclouseau.toml)',
                        default='./logclouseau.toml')
    parser.add_argument('-l', '--log', type=str, help='logging level (defaults to debug)', default='debug')
    return parser.parse_args()


if __name__ == '__main__':
    main()
