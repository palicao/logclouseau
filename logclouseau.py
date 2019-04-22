import argparse
import datetime
import re

import tailer
import toml
import logging

from alert import Alert
import channel
import utils

channels = dict()
alerts = dict()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    setup_logging(args.log)
    setup_channels(config)
    setup_alerts(config)
    evaluate_files(config)


def evaluate_files(config):
    for file_name, file_config in config['file'].items():
        regex = utils.tokens_to_pattern(file_config['tokens'])
        with open(file_config['path']) as file:
            for line in tailer.follow(file):
                for alert in alerts[file_name].values():
                    matches = re.match(regex, line)
                    if matches:
                        gd = matches.groupdict()
                        alert.evaluate(gd, line)


def setup_alerts(config):
    for alert_name, alert_config in config['alert'].items():
        ch = alert_config.get('channel', 'debug')
        ch = channels.get(ch, channel.DebugChannel())
        delta = alert_config.get('grace', 0)
        grace = datetime.timedelta(**delta)
        message = alert_config.get('message', f'Alert {alert_name}')
        min_occurrences = alert_config.get('min_occurrences', 1)
        condition = alert_config.get('condition', 'True')
        identifier = alert_config.get('identifier', alert_name)

        file = alert_config['file']
        if file not in alerts:
            alerts[file] = dict()
        alerts[file][alert_name] = Alert(ch, condition, identifier, grace, min_occurrences, message)


def setup_channels(config):
    for channel_name, channel_config in config['channel'].items():
        channels[channel_name] = channel.ChannelFactory.get_channel(channel_config)


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
    utils.assert_dict_contains_keys(config, {'channel', 'file', 'alert'})
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
