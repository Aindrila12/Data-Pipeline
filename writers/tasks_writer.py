from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class GoogleTasksWriter(Writer):
    """
    A writer class to perform operations on Google Tasks.
    """

    def __init__(self, service_name="tasks_cred"):
        self.service_name = service_name
        self.service = None

    def initialize(self):
        creds = get_credentials(self.service_name)
        self.service = build("tasks", "v1", credentials=creds)

    def create_task_list(self, data: DataWrapper) -> DataWrapper:
        task_list = self.service.tasklists().insert(body=data.data).execute()
        return DataWrapper(data=task_list)

    def create_task(self, data: DataWrapper, tasklist_id: str) -> None:
        for task in data.data:
            self.service.tasks().insert(tasklist=tasklist_id, body=task).execute()

    def update_task(self, data: DataWrapper, tasklist_id: str, task_id: str, updates: dict) -> None:
        self.service.tasks().patch(
            tasklist=tasklist_id,
            task=task_id,
            body=updates
        ).execute()

    def delete_task(self, data: DataWrapper, tasklist_id: str) -> None:
        for task in data.data:
            task_id = task.get("id")
            if task_id:
                self.service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()

    def get_operations(self):
        return {
            "create_task_list": self.create_task_list,
            "create_task": self.create_task,
            "update_task": self.update_task,
            "delete_task": self.delete_task,
        }
