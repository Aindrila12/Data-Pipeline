from googleapiclient.discovery import build
from utility.auth import get_credentials
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class GoogleClassroomFetcher(Fetcher):
    """
    A fetcher class to retrieve data from Google Classroom.
    Supports fetching courses and course work.
    """

    def __init__(self, service_name="classroom_cred"):
        self.service_name = service_name
        self.service = None

    def initialize(self):
        creds = get_credentials(self.service_name)
        self.service = build("classroom", "v1", credentials=creds)

    def fetch_courses(self, page_size: int = 10) -> DataWrapper:
        """
        Fetch list of active courses.
        """
        results = self.service.courses().list(pageSize=page_size).execute()
        courses = results.get('courses', [])
        return DataWrapper(data=courses)

    def fetch_course_work(self, course_id: str) -> DataWrapper:
        """
        Fetch coursework for a specific course.
        """
        results = self.service.courses().courseWork().list(courseId=course_id).execute()
        course_work = results.get('courseWork', [])
        return DataWrapper(data=course_work)

    def get_sample_course(self, **course) -> DataWrapper:
        """
        Return a course structure directly from operation_params.
        """
        return DataWrapper([course])

    def get_operations(self):
        return {
            "fetch_courses": self.fetch_courses,
            "fetch_course_work": self.fetch_course_work,
            "get_sample_course": self.get_sample_course
        }
