from twilio.rest import Client
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class TwilioFetcher(Fetcher):
    """
    Fetcher for retrieving SMS messages from Twilio.
    """

    def __init__(self, account_sid: str, auth_token: str, service_name="twilio_cred"):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.service_name = service_name
        self.client = None

    def initialize(self):
        self.client = Client(self.account_sid, self.auth_token)

    def fetch_messages(self, limit: int = 10) -> DataWrapper:
        """
        Fetch recent SMS messages.

        Args:
            limit (int): Number of recent messages to fetch.

        Returns:
            DataWrapper: List of messages.
        """
        messages = self.client.messages.list(limit=limit)
        messages_data = [msg.__dict__ for msg in messages]
        return DataWrapper(data=messages_data)

    def get_operations(self):
        return {
            "fetch_messages": self.fetch_messages
        }
