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

    def write_data(self, data: DataWrapper) -> None:
        """
        Send a Slack message (optionally to a thread).
        Expects:
            data.data = {
                "channel_id": str,
                "message": {
                    "channel": str,
                    "text": str,
                    "thread_ts": Optional[str]
                }
            }
        """
        message = data.data["message"]
        self.client.chat_postMessage(
            channel=message["channel"],
            text=message["text"],
            thread_ts=message.get("thread_ts")  # Optional
        )


    # def update_message(self, data: DataWrapper, channel: str, ts: str, text: str):
    #     """
    #     Update an existing message by timestamp.
    #     """
    #     self.client.chat_update(channel=channel, ts=ts, text=text)

    def delete_message(self, data: DataWrapper):
        """
        Delete a message by its channel and timestamp.
        """
        print("888888888888888", data.data)
        self.client.chat_delete(channel=data.data["channel"], ts=data.data["ts"])

    def get_operations(self):
        return {
            "write_data": self.write_data,
            # "update_message": self.update_message,
            "delete_message": self.delete_message,
        }
