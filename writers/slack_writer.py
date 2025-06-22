from slack_sdk import WebClient
from utility.auth import get_credentials
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class SlackWriter(Writer):
    """
    Send, update, and remove Slack messages.
    """
    def __init__(self, token: str = None):
        self.token = token or get_credentials("slack_cred")
        self.client = None

    def initialize(self):
        self.client = WebClient(token=self.token)

    def post_message(self, data: DataWrapper, channel: str, text: str, thread_ts: str = None):
        """
        Send a Slack message (optionally to a thread).
        """
        self.client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)

    def update_message(self, data: DataWrapper, channel: str, ts: str, text: str):
        """
        Update an existing message by timestamp.
        """
        self.client.chat_update(channel=channel, ts=ts, text=text)

    def delete_message(self, data: DataWrapper, channel: str, ts: str):
        """
        Delete a message by its channel and timestamp.
        """
        self.client.chat_delete(channel=channel, ts=ts)

    def get_operations(self):
        return {
            "post_message": self.post_message,
            "update_message": self.update_message,
            "delete_message": self.delete_message,
        }
