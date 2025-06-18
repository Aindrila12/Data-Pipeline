from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build

class FormFetcher(Fetcher):
    def __init__(self, form_id: str, service_name: str = "form_cred"):
        super().__init__(form_id=form_id, service_name=service_name)
        self.form_id = form_id
        self.service_name = service_name
        self.service = None

    def initialize(self):
        creds = get_credentials(self.service_name)
        self.service = build(
            "forms", "v1", credentials=creds, discoveryServiceUrl="https://forms.googleapis.com/$discovery/rest?version=v1", static_discovery=False
        )

    def fetch_data(self) -> DataWrapper:
        """Fetch full form definition (metadata + structure)."""
        form = self.service.forms().get(formId=self.form_id).execute()
        return DataWrapper(data=form)

    def fetch_responses(self, page_size: int = 100) -> DataWrapper:
        """Fetch all responses to the form."""
        resp = self.service.forms().responses().list(formId=self.form_id, pageSize=page_size).execute()
        return DataWrapper(data=resp.get("responses", []))

    def fetch_single_response(self, response_id: str) -> DataWrapper:
        """Fetch a single response by its ID."""
        res = self.service.forms().responses().get(formId=self.form_id, responseId=response_id).execute()
        return DataWrapper(data=res)
    
    def fetch_structure_only(self, info) -> DataWrapper:
        """
        Returns a static form structure provided in the config under 'form_structure'.
        This is useful for testing or creating new forms using a pre-defined schema.
        """
        structure = {
            "info": info
        }

        print("structure >>>>>>>>>", structure)

        return DataWrapper(data=structure)


    def fetch_questions_only(self) -> DataWrapper:
        """
        Extracts and returns only question items from the form.
        """
        form = self.service.forms().get(formId=self.form_id).execute()
        questions = []
        for item in form.get("items", []):
            if "questionItem" in item:
                questions.append(item)
        return DataWrapper(data=questions)


    def get_operations(self):
        return {
            "fetch_data": self.fetch_data,
            "fetch_responses": self.fetch_responses,
            "fetch_single_response": self.fetch_single_response,
            "fetch_structure_only": self.fetch_structure_only,
            "fetch_questions_only": self.fetch_questions_only
        }
