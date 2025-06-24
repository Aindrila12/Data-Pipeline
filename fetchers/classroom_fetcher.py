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

    # def fetch_data(self, page_size: int = 10) -> DataWrapper:
    #     """
    #     Fetch list of active courses.
    #     """
    #     results = self.service.courses().list(pageSize=page_size).execute()
    #     print(">>>>>>>>>>results>>>>>>>>>>", results)
    #     courses = results.get('courses', [])
    #     return DataWrapper(data=courses)

    def fetch_data(self, page_size: int = 10) -> DataWrapper:
        """
        Fetch list of courses and prepare sample coursework entries.
        """
        results = self.service.courses().list(pageSize=page_size).execute()
        raw_courses = results.get('courses', [])
        course_works = []

        for course in raw_courses:
            course_id = course.get("id")

            sample_coursework = {
                "id": course_id,  # Required for matching in writer
                "title": "Assignment 1",
                "description": "Complete the questions from Chapter 2.",
                "materials": [],
                "workType": "ASSIGNMENT",
                "state": "PUBLISHED",
                "dueDate": {
                    "year": 2025,
                    "month": 6,
                    "day": 28
                },
                "dueTime": {
                    "hours": 23,
                    "minutes": 59
                }
            }

            course_works.append(sample_coursework)

            print(f"""
                [Prepared Coursework]
                For Course ID: {course_id}
                Title: {sample_coursework['title']}
                Due: {sample_coursework['dueDate']} at {sample_coursework['dueTime']}
            """.strip())

        return DataWrapper(data=course_works)



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
            "fetch_data": self.fetch_data,
            "fetch_course_work": self.fetch_course_work,
            "get_sample_course": self.get_sample_course
        }
