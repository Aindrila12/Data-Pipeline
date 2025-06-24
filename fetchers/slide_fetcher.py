from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class GoogleSlidesFetcher(Fetcher):
    """
    A fetcher class to retrieve data from Google Slides.
    """

    def __init__(self, presentation_id: str, service_name: str = "slides_cred"):
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

    # def fetch_data(self) -> DataWrapper:
    #     """
    #     Fetch all slide objects from the presentation.
    #     """
    #     presentation = self.service.presentations().get(presentationId=self.presentation_id).execute()
    #     return DataWrapper(data=presentation.get("slides", []))

    def fetch_data(self) -> DataWrapper:
        """
        Fetch presentation slide ids.
        """
        presentation = self.service.presentations().get(presentationId=self.presentation_id).execute()
        slides = presentation.get('slides', [])
        
        slide_ids = []
        for slide in slides:
            slide_ids.append(slide.get("objectId"))

        print(f"[SlideFetcher] Found slides: {slide_ids}")
        return DataWrapper(data={"slide_ids": slide_ids})
    
    def get_presentation_data(self, **presentation_details) -> DataWrapper:
        """
        Returns a static presentation data structure passed in via operation_params.

        Args:
            presentation_details (dict): Dict containing the initial structure of the presentation
                                        such as title, slides content, etc.

        Returns:
            DataWrapper: Wrapped presentation data.
        """
        return DataWrapper(data=presentation_details)


    def get_operations(self):
        return {
            "fetch_presentation_metadata": self.fetch_presentation_metadata,
            "fetch_data": self.fetch_data,
            "get_presentation_data": self.get_presentation_data
        }
