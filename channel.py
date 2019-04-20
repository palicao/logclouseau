import abc
import logging

from slackclient import SlackClient


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
    __instances = dict()

    @classmethod
    def get_channel(cls, config: dict) -> Channel:
        channel_type = config['type']

        if channel_type in cls.__instances:
            return cls.__instances[channel_type]

        if channel_type == 'slack':
            client = SlackClient(config['api_token'])
            instance = SlackChannel(client, config['channel'])
        elif channel_type == 'debug':
            instance = DebugChannel()
        else:
            raise NotImplementedError(f'channel type "{channel_type}" is not implemented')

        cls.__instances[channel_type] = instance
        return instance


class SlackChannel(Channel):
    __channel: str
    __client: SlackClient

    def __init__(self, client: SlackClient, channel: str):
        self.__client = client
        self.__channel = channel

    def alert(self, message: str, logline: str) -> None:
        try:
            self.__send_message(f'Message: {message}\nLogline: {logline}')
        except:
            logging.exception(f'unable to send message to channel {self.__channel}', exc_info=True)

    def __send_message(self, message):
        response = self.__client.api_call('chat.postMessage', channel=self.__channel, text=message)
        if not response['ok']:
            error = response['error']
            raise RuntimeError(f'unable to send message to slack: {error}')


class DebugChannel(Channel):
    def alert(self, message: str, logline: str) -> None:
        logging.info(f'Message: {message} - LogLine: {logline}')
