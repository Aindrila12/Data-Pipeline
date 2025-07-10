from datetime import datetime
from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class GoogleCalendarFetcher(Fetcher):
    """
    A fetcher class to retrieve events from Google Calendar.

    Supports fetching events in a time range or the next upcoming event.
    """

    def __init__(self, calendar_id: str = "primary", service_name="calendar_cred"):
        """
        Initialize the GoogleCalendarFetcher.

        Args:
            calendar_id (str): The ID of the calendar to operate on. Defaults to "primary".
            service_name (str): Key to identify the credential configuration. Defaults to "calendar_cred".
        """
        try:
            self.service_name = service_name
            self.calendar_id = calendar_id
            self.service = None
        except Exception as e:
            raise ValueError(f"Failed to initialize GoogleCalendarFetcher: {e}")

    def initialize(self):
        """
        Initialize the Calendar API service using credentials.
        """
        try:
            creds = get_credentials(self.service_name)
            self.service = build("calendar", "v3", credentials=creds)
        except Exception as e:
            raise ValueError(f"Failed to initialize Google Calendar service: {e}")

    def fetch_data(self, time_min: str = None, time_max: str = None, max_results: int = 10) -> DataWrapper:
        """
        Fetch events from the calendar within a specified time range.

        Args:
            time_min (str): The lower bound (inclusive) for an event’s start time (RFC3339 timestamp).
                            Defaults to the current UTC time.
            time_max (str): The upper bound (exclusive) for an event’s start time (RFC3339 timestamp).
            max_results (int): Maximum number of events to return. Defaults to 10.

        Returns:
            DataWrapper: A wrapped list of events retrieved from the calendar.
        """
        try:
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC
            time_min = time_min or now

            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            return DataWrapper(data=events)
        except Exception as e:
            raise ValueError(f"Failed to fetch data from Google Calendar: {e}")

    # def get_upcoming_event(self, calendar_id="primary") -> DataWrapper:
    #     """
    #     Fetch the next upcoming event from the calendar.

    #     Returns:
    #         DataWrapper: A wrapped single event dictionary, or empty list if none.
    #     """
    #     try:
    #         now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    #         events_result = self.service.events().list(
    #             calendarId=calendar_id,
    #             timeMin=now,
    #             maxResults=1,
    #             singleEvents=True,
    #             orderBy='startTime'
    #         ).execute()

    #         events = events_result.get('items', [])
    #         return DataWrapper(data=events)
    #     except Exception as e:
    #         raise ValueError(f"Failed to fetch upcoming event from Google Calendar: {e}")
        
    
    def get_sample_event(self, **event_details) -> DataWrapper:
        """
        Return a DataWrapper object containing the event data passed in operation_params.

        Args:
            event_details (dict): The full event dictionary.

        Returns:
            DataWrapper: Wrapped event data.
        """
        return DataWrapper([event_details])


    def get_operations(self):
        """
        Get a dictionary of supported fetch operations.

        Returns:
            dict: Mapping of operation names to methods.
        """
        return {
            "fetch_data": self.fetch_data,
            # "get_upcoming_event": self.get_upcoming_event,
            "get_sample_event": self.get_sample_event
        }
