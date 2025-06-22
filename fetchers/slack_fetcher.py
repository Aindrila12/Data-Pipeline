from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from utility.auth import get_credentials
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class SlackFetcher(Fetcher):
    """
    Fetch messages or channel info from Slack.
    """
    def __init__(self, token: str = None):
        self.token = token or get_credentials("slack_cred")
        self.client = None

    def initialize(self):
        self.client = WebClient(token=self.token)

    def list_channels(self) -> DataWrapper:
        """Fetch list of accessible channels."""
        resp = self.client.conversations_list(types="public_channel,private_channel").data
        return DataWrapper(data=resp.get("channels", []))

    def fetch_messages(self, channel: str, limit: int = 100) -> DataWrapper:
        """
        Retrieve recent messages from a channel.
        """
        try:
            resp = self.client.conversations_history(channel=channel, limit=limit).data
            return DataWrapper(data=resp.get("messages", []))
        except SlackApiError as e:
            print(f"[SlackFetcher] Error: {e.response['error']}")
            return DataWrapper(data=[])

    def get_operations(self):
        return {
            "list_channels": self.list_channels,
            "fetch_messages": self.fetch_messages,
        }
