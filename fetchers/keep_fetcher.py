from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class GoogleKeepFetcher(Fetcher):
    """
    Fetcher for Google Keep notes using the official API.
    """

    def __init__(self, service_name="keep_cred"):
        self.service_name = service_name
        self.service = None

    def initialize(self):
        creds = get_credentials(self.service_name)
        self.service = build("keep", "v1", credentials=creds)

    def fetch_notes(self, page_size: int = 50) -> DataWrapper:
        """
        List note summaries.
        """
        resp = self.service.notes().list(pageSize=page_size).execute()
        notes = resp.get("notes", [])
        return DataWrapper(data=notes)

    def get_note(self, note_id: str) -> DataWrapper:
        """
        Retrieve a specific note by its ID.
        """
        note = self.service.notes().get(name=f"notes/{note_id}").execute()
        return DataWrapper(data=[note])

    def get_operations(self):
        return {
            "fetch_notes": self.fetch_notes,
            "get_note": self.get_note,
        }
