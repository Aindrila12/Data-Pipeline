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

    def fetch_data(self, page_size: int = 50) -> DataWrapper:
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
    
    def get_sample_note(self, **note_fields) -> DataWrapper:
        """
        Returns a Google Keep note body structure from operation_params.
        Supports both text and list notes.
        Example input in config.yaml:
        title: "Meeting Notes"
        body:
            text:
            text: "Discuss project timelines and deliverables."
        """
        note = {
            "title": note_fields.get("title", "Untitled Note"),
            "body": note_fields.get("body", {})
        }
        return DataWrapper([note])


    def get_operations(self):
        return {
            "fetch_data": self.fetch_data,
            "get_note": self.get_note,
            "get_sample_note": self.get_sample_note
        }
