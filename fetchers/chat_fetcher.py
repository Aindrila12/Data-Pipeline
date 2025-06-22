from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class GoogleChatFetcher(Fetcher):
    """
    A fetcher class to interact with Google Chat.

    Currently supports static message templates or room lookup stubs.
    """

    def __init__(self, space_id: str = "", service_name: str = "chat_cred"):
        """
        Initialize the fetcher.

        Args:
            space_id (str): Space/room ID for Google Chat.
            service_name (str): Key from the credentials config.
        """
        self.service_name = service_name
        self.space_id = space_id
        self.service = None

    def initialize(self):
        """
        Initialize the Chat API service using credentials.
        """
        creds = get_credentials(self.service_name)
        self.service = build("chat", "v1", credentials=creds)

    def get_sample_message(self, **message_dict) -> DataWrapper:
        """
        Return a wrapped message dictionary passed via config.

        Args:
            message_dict (dict): Chat message content and options.

        Returns:
            DataWrapper: Wrapped message data.
        """
        return DataWrapper([message_dict])

    def get_operations(self):
        return {
            "get_sample_message": self.get_sample_message,
        }
