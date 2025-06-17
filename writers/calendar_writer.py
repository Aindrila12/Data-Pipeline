from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class GoogleCalendarWriter(Writer):
    """
    A writer class to perform various write operations on Google Calendar.

    Supports creating, updating, deleting events, and clearing all events in a calendar.
    """

    def __init__(self, calendar_id: str = "primary", service_name="calendar_cred"):
        """
        Initialize the GoogleCalendarWriter.

        Args:
            calendar_id (str): The ID of the calendar to operate on. Defaults to "primary".
            service_name (str): Key to identify the credential configuration. Defaults to "calendar_cred".
        """
        self.service_name = service_name
        self.calendar_id = calendar_id
        self.service = None

    def initialize(self):
        """
        Initialize the Calendar API service using credentials.
        """
        creds = get_credentials(self.service_name)
        self.service = build("calendar", "v3", credentials=creds)

    def write_data(self, data: DataWrapper):
        """
        Create one or more events in the calendar.

        Args:
            data (DataWrapper): Contains a list of event dictionaries to be created.
        """
        for event in data.data:
            self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                sendUpdates='all'
            ).execute()

    def update_event(self, data: DataWrapper, event_id: str, event):
        """
        Update an existing event with new data.

        Args:
            data (DataWrapper): Ignored in this case.
            event_id (str): ID of the event to be updated.
            event (list): List of dicts containing update fields.
        """
        for updated_fields in event:
            self.service.events().patch(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=updated_fields
            ).execute()


    def delete_event(self, data: DataWrapper):
        """
        Delete one or more events based on their IDs.

        Args:
            data (DataWrapper): Contains a list of event dictionaries, each including an 'id' field.
        """
        for event in data.data:
            event_id = event.get("id")
            if event_id:
                self.service.events().delete(
                    calendarId=self.calendar_id,
                    eventId=event_id
                ).execute()

    def clear_all_events(self, confirm: bool = False):
        """
        Delete all events from the calendar.

        Args:
            confirm (bool): Set to True to confirm deletion. Prevents accidental wipes.
        """
        if not confirm:
            print("[CalendarWriter] Skipping deletion. Set confirm=True to proceed.")
            return

        events = self.service.events().list(calendarId=self.calendar_id).execute().get("items", [])
        for e in events:
            self.service.events().delete(calendarId=self.calendar_id, eventId=e["id"]).execute()

    def get_operations(self):
        """
        Get a dictionary of supported operations and their corresponding methods.

        Returns:
            dict: Mapping of operation names to methods.
        """
        return {
            "write_data": self.write_data,
            "update_event": self.update_event,
            "delete_event": self.delete_event,
            "clear_all_events": self.clear_all_events,
        }
