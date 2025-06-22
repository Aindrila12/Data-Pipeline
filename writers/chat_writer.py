from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class GoogleChatWriter(Writer):
    """
    A writer class to send messages to Google Chat spaces.
    """

    def __init__(self, space_id: str = "", service_name: str = "chat_cred"):
        """
        Initialize the writer.

        Args:
            space_id (str): The space/room ID.
            service_name (str): Credential key.
        """
        self.service_name = service_name
        self.space_id = space_id
        self.service = None

    def initialize(self):
        """
        Initialize the Chat API service.
        """
        creds = get_credentials(self.service_name)
        self.service = build("chat", "v1", credentials=creds)

    def write_data(self, data: DataWrapper):
        """
        Send message(s) to the specified Chat space.

        Args:
            data (DataWrapper): Contains list of message dicts.
        """
        for message in data.data:
            self.service.spaces().messages().create(
                parent=f"spaces/{self.space_id}",
                body=message
            ).execute()

    def get_operations(self):
        return {
            "write_data": self.write_data
        }
