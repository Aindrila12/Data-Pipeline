from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class GoogleClassroomWriter(Writer):
    """
    A writer class to perform write operations in Google Classroom.
    Supports creating courses and course work.
    """

    def __init__(self, service_name="classroom_cred"):
        self.service_name = service_name
        self.service = None

    def initialize(self):
        creds = get_credentials(self.service_name)
        self.service = build("classroom", "v1", credentials=creds)

    def write_data(self, data: DataWrapper):
        """
        Create one or more courses.
        """
        for course in data.data:
            self.service.courses().create(body=course).execute()

    def create_course_work(self, data: DataWrapper, course_id: str):
        """
        Create coursework in a specific course.
        """
        print(">>>>>>>>data.data>>>>>>>>", data.data)
        for cw in data.data:
            if course_id == cw["id"]:
                self.service.courses().courseWork().create(courseId=course_id, body=cw).execute()

    # def delete_course(self, data: DataWrapper):
    #     """
    #     Delete one or more courses by ID.
    #     """
    #     for course in data.data:
    #         print(">>>>>>>>course>>>>>>>>", course)
    #         course_id = course.get("courseId")
    #         if course_id:
    #             self.service.courses().delete(id=course_id).execute()

    def get_operations(self):
        return {
            "write_data": self.write_data,
            "create_course_work": self.create_course_work,
        }
