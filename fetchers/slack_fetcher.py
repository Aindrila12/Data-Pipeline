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

    def fetch_messages(self, channel: str, limit: int = 100) -> DataWrapper:
        """
        Retrieve recent messages from a channel.
        """
        try:
            response = self.client.conversations_open(users=channel)
            dm_channel_id = response["channel"]["id"]
            print("dm_channel_id>>>>>>>>>", dm_channel_id)
            resp = self.client.conversations_history(channel=dm_channel_id, limit=limit).data
            print("resp>>>>>>>>>", resp)
            return DataWrapper(data={"channel": dm_channel_id, "ts": resp.get("messages")[0]["ts"]})
        except SlackApiError as e:
            print(f"[SlackFetcher] Error: {e.response['error']}")
            return DataWrapper(data=[])

    def fetch_data(self) -> DataWrapper:
        """Fetch list of accessible channels."""
        resp = self.client.conversations_list(types="public_channel,private_channel").data
        return DataWrapper(data=resp.get("channels", []))
        
    def get_dm_message_payload(self, username: str, text: str, thread_ts: str = None) -> DataWrapper:
        """
        Resolve a Slack username to a DM channel and construct a message payload.

        Args:
            username: Slack username (not email).
            text: Message to send.
            thread_ts: Optional thread timestamp (for threaded replies).

        Returns:
            DataWrapper with {
                "channel_id": str,
                "message": { "channel": str, "text": str, "thread_ts": Optional[str] }
            }
        """
        # Step 1: Get user list
        users_resp = self.client.users_list()
        users = users_resp["members"]

        # Step 2: Match username to user ID
        user_id = None
        for user in users:
            if user["name"] == username:
                user_id = user["id"]
                break

        if not user_id:
            raise ValueError(f"User with name '{username}' not found")

        # Step 3: Open DM with that user
        dm_resp = self.client.conversations_open(users=[user_id])
        channel_id = dm_resp["channel"]["id"]

        # Step 4: Construct the message payload
        message = {
            "channel": channel_id,
            "text": text
        }
        if thread_ts:
            message["thread_ts"] = thread_ts

        return DataWrapper(data={"message": message})
    
    def list_slack_usernames(self):
        response = self.client.users_list()

        print("Slack Users:")
        for member in response['members']:
            print("111111111111111", member)
            if not member.get("deleted") and not member.get("is_bot"):
                real_name = member.get("real_name")
                username = member.get("name")
                user_id = member.get("id")
                print(f"->>>>>>>>>>>>>>>> {real_name} (@{username}) | ID: {user_id}")

        return DataWrapper(data=response['members'])


    def get_operations(self):
        return {
            "fetch_messages": self.fetch_messages,
            "fetch_data": self.fetch_data,
            "get_message_payload": self.get_dm_message_payload,
            "list_slack_usernames": self.list_slack_usernames
        }
