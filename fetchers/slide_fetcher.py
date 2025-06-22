from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class GoogleSlidesFetcher(Fetcher):
    """
    A fetcher class to retrieve data from Google Slides.
    """

    def __init__(self, presentation_id: str, service_name: str = "drive_cred"):
        self.service_name = service_name
        self.presentation_id = presentation_id
        self.service = None

    def initialize(self):
        creds = get_credentials(self.service_name)
        self.service = build("slides", "v1", credentials=creds)

    def fetch_presentation_metadata(self) -> DataWrapper:
        """
        Fetch presentation title and slide count.
        """
        presentation = self.service.presentations().get(presentationId=self.presentation_id).execute()
        metadata = {
            "title": presentation.get("title"),
            "slides_count": len(presentation.get("slides", [])),
        }
        return DataWrapper(data=metadata)

    def fetch_all_slides(self) -> DataWrapper:
        """
        Fetch all slide objects from the presentation.
        """
        presentation = self.service.presentations().get(presentationId=self.presentation_id).execute()
        return DataWrapper(data=presentation.get("slides", []))

    def get_operations(self):
        return {
            "fetch_presentation_metadata": self.fetch_presentation_metadata,
            "fetch_all_slides": self.fetch_all_slides,
        }
