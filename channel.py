import abc
import logging

from slackclient import SlackClient

from utils import assert_dict_contains_keys


class Channel(object, metaclass=abc.ABCMeta):
    """
    Abstract Channel class. Every child must implement the alert method
    """
    @abc.abstractmethod
    def alert(self, message: str, logline: str) -> None:
        raise NotImplementedError('each Channel must implement the "alert" method')


class ChannelFactory(object):
    """
    Instantiates channels based on the "type". Currently only implemented "slack" and "debug"
    """
    instances = dict()

    @classmethod
    def get_channel(cls, config: dict) -> Channel:
        channel_type = config['type'] if 'type' in config else 'debug'

        if channel_type in cls.instances:
            return cls.instances[channel_type]

        if channel_type == 'slack':
            assert_dict_contains_keys(config, {'api_token', 'channel'})
            client = SlackClient(config['api_token'])
            instance = SlackChannel(client, config['channel'])
        elif channel_type == 'debug':
            instance = DebugChannel()
        else:
            raise NotImplementedError(f'channel type "{channel_type}" is not implemented')

        cls.instances[channel_type] = instance
        return instance


class SlackChannel(Channel):
    def __init__(self, client: SlackClient, channel: str):
        self.client = client
        self.channel = channel

    def alert(self, message: str, logline: str) -> None:
        try:
            self.__send_message(f'Message: {message}\nLine: {logline}')
        except:
            logging.exception(f'unable to send message to channel {self.channel}', exc_info=True)

    def __send_message(self, message):
        response = self.client.api_call('chat.postMessage', channel=self.channel, text=message)
        if not response['ok']:
            error = response['error']
            raise RuntimeError(f'unable to send message to slack: {error}')


class DebugChannel(Channel):
    def alert(self, message: str, logline: str) -> None:
        logging.info(f'ALERT! Message: {message} - Line: {logline}')
