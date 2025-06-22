from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class GoogleKeepWriter(Writer):
    """
    Writer for Google Keep notes via the official API.
    """

    def __init__(self, service_name="keep_cred"):
        self.service_name = service_name
        self.service = None

    def initialize(self):
        creds = get_credentials(self.service_name)
        self.service = build("keep", "v1", credentials=creds)

    def create_note(self, data: DataWrapper) -> DataWrapper:
        """
        Create text or list note(s).
        Expects data.data to be a list of note dicts:
          {
            "title": "Note title",
            "body": {"text": {"text": "..."}},
            # or for list notes:
            # "body": {"list": {"listItems": [ ... ]}}
          }
        """
        created = []
        for note_obj in data.data:
            note = self.service.notes().create(body=note_obj).execute()
            created.append(note)
        return DataWrapper(data=created)

    def delete_note(self, data: DataWrapper) -> None:
        """
        Delete one or more notes by ID.
        Expects data.data = [{'name': 'notes/ID'}, …]
        """
        for note in data.data:
            self.service.notes().delete(name=note["name"]).execute()

    def get_operations(self):
        return {
            "create_note": self.create_note,
            "delete_note": self.delete_note,
        }
