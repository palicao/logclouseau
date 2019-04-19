import abc

from slackclient import SlackClient


class Channel(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def alert(self, message: str, logline: str) -> None:
        raise NotImplementedError('users must define alert to implement a Channel')


class ChannelFactory(object):
    @staticmethod
    def get_channel(config: dict) -> Channel:
        type = config['type']
        if type == "slack":
            client = SlackClient(config['api_token'])
            return SlackChannel(client, config['channel'])
        elif type == 'debug':
            return DebugChannel()
        else:
            raise NotImplementedError(f'channel type "{type}" is not implemented')


class SlackChannel(Channel):
    channel: str
    api_token: str
    client: SlackClient

    def __init__(self, client: SlackClient, channel: str):
        self.client = client
        self.channel = channel

    def alert(self, message: str, logline: str) -> None:
        self.client.api_call("chat.postMessage", channel=self.channel, text=message)


class DebugChannel(Channel):
    def alert(self, message: str, logline: str) -> None:
        print("alert!")
        print(f"message {message}")
        print(f"logline {logline}")
        print()
