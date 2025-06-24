from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class GoogleSlidesWriter(Writer):
    """
    A writer class to perform write operations on Google Slides.
    """

    def __init__(self, presentation_id: str, service_name: str = "slides_cred"):
        self.service_name = service_name
        self.presentation_id = presentation_id
        self.service = None

    def initialize(self):
        creds = get_credentials(self.service_name)
        self.service = build("slides", "v1", credentials=creds)

    def insert_textbox(self, data: DataWrapper, text, x, y) -> None:
        """
        Insert a textbox with text into the first slide of the presentation.
        Uses data from fetcher to get valid slide ID.
        Text, x, and y come from operation_params.
        """
        # Extract slide IDs from fetcher data
        slide_ids = data.data.get("slide_ids")
        if not slide_ids or not isinstance(slide_ids, list):
            raise ValueError("[SlidesWriter] No valid slide IDs found in fetcher data.")

        page_id = slide_ids[0]  # Default to the first slide

        # Get operation parameters
        # text = getattr(self, "operation_params", {}).get("text", "Default Text")
        # x = getattr(self, "operation_params", {}).get("x", 50)
        # y = getattr(self, "operation_params", {}).get("y", 50)

        element_id = f"textbox_{page_id}"
        requests = [
            {
                "createShape": {
                    "objectId": element_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": page_id,
                        "size": {
                            "height": {"magnitude": 100, "unit": "PT"},
                            "width": {"magnitude": 300, "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": x,
                            "translateY": y,
                            "unit": "PT"
                        }
                    }
                }
            },
            {
                "insertText": {
                    "objectId": element_id,
                    "insertionIndex": 0,
                    "text": text
                }
            }
        ]

        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={"requests": requests}
        ).execute()

        print(f"[SlidesWriter] Inserted textbox on slide {page_id} with text: '{text}' at ({x}, {y})")


    # def insert_textbox(self, data: DataWrapper, page_id: str, text: str, x: int = 50, y: int = 50):
    #     """
    #     Insert a textbox with text into the given slide.
    #     """
    #     element_id = f"textbox_{page_id}"
    #     requests = [
    #         {
    #             "createShape": {
    #                 "objectId": element_id,
    #                 "shapeType": "TEXT_BOX",
    #                 "elementProperties": {
    #                     "pageObjectId": page_id,
    #                     "size": {
    #                         "height": {"magnitude": 100, "unit": "PT"},
    #                         "width": {"magnitude": 300, "unit": "PT"},
    #                     },
    #                     "transform": {
    #                         "scaleX": 1,
    #                         "scaleY": 1,
    #                         "translateX": x,
    #                         "translateY": y,
    #                         "unit": "PT"
    #                     }
    #                 }
    #             }
    #         },
    #         {
    #             "insertText": {
    #                 "objectId": element_id,
    #                 "insertionIndex": 0,
    #                 "text": text
    #             }
    #         }
    #     ]

    #     self.service.presentations().batchUpdate(
    #         presentationId=self.presentation_id,
    #         body={"requests": requests}
    #     ).execute()
    #     print(f"[SlidesWriter] Inserted textbox on page {page_id} with text: {text}")

    # def write_data(self, data: DataWrapper) -> DataWrapper:
    #     """
    #     Create a new presentation.
    #     """
    #     presentation = self.service.presentations().create(body=data.data).execute()
    #     return DataWrapper(data=presentation)

    def write_data(self, data: DataWrapper):
        """
        Create a new presentation.
        """
        presentation_data = data.data
        title = presentation_data.get("title", "Untitled Presentation1")

        # Step 1: Create the presentation
        presentation = self.service.presentations().create(body={"title": title}).execute()
        presentation_id = presentation["presentationId"]
        print(f"[SlideWriter] Created presentation: {title} ({presentation_id})")



    def get_operations(self):
        return {
            "insert_textbox": self.insert_textbox,
            "write_data": self.write_data
        }
