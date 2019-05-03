import abc
import logging
from typing import Dict, Optional

from slackclient import SlackClient

from src.utils import assert_dict_contains_keys


class Channel(metaclass=abc.ABCMeta):
    """
    Abstract Channel class. Every child must implement the alert method
    """
    @abc.abstractmethod
    def alert(self, message: str, logline: str) -> None:
        ...


class ChannelFactory:
    """
    Instantiates channels based on the "type". Currently only implemented
    "slack" and "debug"
    """
    _instances: Dict[str, Channel] = dict()

    @classmethod
    def get_channel(cls, config: dict) -> Channel:
        channel_type: str = config.get('type', 'debug')

        if channel_type in cls._instances:
            return cls._instances[channel_type]

        instance: Optional[Channel] = None
        if channel_type == 'slack':
            assert_dict_contains_keys(config, {'api_token', 'channel'})
            client = SlackClient(config['api_token'])
            instance = SlackChannel(client, config['channel'])
        elif channel_type == 'debug':
            instance = DebugChannel()
        else:
            raise NotImplementedError(
                f'channel type "{channel_type}" is not implemented'
            )

        cls._instances[channel_type] = instance
        return instance


class SlackChannel(Channel):
    def __init__(cls, client: SlackClient, channel: str, **kwargs):
        cls._client = client
        cls._channel = channel
        super().__init__()

    def alert(self, message: str, logline: str) -> None:
        try:
            self.__send_message(f'Message: {message}\nLine: {logline}')
        except RuntimeError:
            logging.exception(
                f'unable to send message to channel {self._channel}',
                exc_info=True
            )

    def __send_message(self, message: str):
        response = self._client.api_call(
            'chat.postMessage', channel=self._channel, text=message
        )
        if not response['ok']:
            error = response['error']
            raise RuntimeError(f'unable to send message to slack: {error}')


class DebugChannel(Channel):
    def alert(self, message: str, logline: str) -> None:
        logging.info(f'ALERT! Message: {message} - Line: {logline}')
