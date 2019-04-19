import argparse
import datetime
import re

import tailer
import toml

from channel import Channel, ChannelFactory

channels = dict()
grace_times = dict()


def main() -> None:
    parser = argparse.ArgumentParser(description='LogClouseau inspect your logs and reacts accordingly')
    parser.add_argument('-c', '--config', type=str, help='config file path (defaults to ./logclouseau.toml)',
                        default='./logclouseau.toml')
    args = parser.parse_args()

    config = toml.load(args.config)

    for name, channel_config in config['channel'].items():
        channels[name] = ChannelFactory.get_channel(channel_config)

    for name, file_config in config['file'].items():
        regex = re.compile(file_config['regexp'])
        channel = file_config['channel']
        with open(file_config['path']) as file:
            for line in tailer.follow(file):
                if regex.search(line):
                    send_alert(channels[channel], name, file_config['message'], line, file_config['grace'])


def send_alert(channel: Channel, name: str, message: str, line: str, grace: dict) -> None:
    if name not in grace_times or grace_times[name] < datetime.datetime.now():
        grace_times[name] = datetime.datetime.now() + datetime.timedelta(**grace)
        channel.alert(message, line)


if __name__ == '__main__':
    main()
