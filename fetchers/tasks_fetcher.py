from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class GoogleTasksFetcher(Fetcher):
    """
    A fetcher class to retrieve task lists and tasks from Google Tasks.
    """

    def __init__(self, service_name="tasks_cred"):
        self.service_name = service_name
        self.service = None

    def initialize(self):
        creds = get_credentials(self.service_name)
        self.service = build("tasks", "v1", credentials=creds)

    def fetch_task_lists(self) -> DataWrapper:
        result = self.service.tasklists().list(maxResults=100).execute()
        return DataWrapper(data=result.get("items", []))

    def fetch_tasks(self, tasklist_id: str) -> DataWrapper:
        result = self.service.tasks().list(tasklist=tasklist_id, showCompleted=True).execute()
        return DataWrapper(data=result.get("items", []))

    def get_operations(self):
        return {
            "fetch_task_lists": self.fetch_task_lists,
            "fetch_tasks": self.fetch_tasks,
        }
