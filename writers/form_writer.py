from core.interfaces import Writer
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build

class FormWriter(Writer):
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

    def batch_update(self, data: DataWrapper) -> None:
        """
        Apply a list of update requests to the form.
        Each element in data.data should be a Google Forms API request dict.
        """
        requests = data.data  # expecting [{'updateItem': {...}}, ...]
        if not isinstance(requests, list):
            raise ValueError("batch_update expects a list of update request objects")
        self.service.forms().batchUpdate(formId=self.form_id, body={"requests": requests}).execute()
        print(f"[FormWriter] Applied {len(requests)} update requests.")

    # def write_data(self, data: DataWrapper) -> DataWrapper:
    #     """
    #     Create a new form given initial form object (must include 'info': {'title': ...}).
    #     Returns the created form definition.
    #     """
    #     form_obj = data.data
    #     new_form = self.service.forms().create(body=form_obj).execute()
    #     return DataWrapper(data=new_form)

    def write_data(self, data: DataWrapper) -> DataWrapper:
        """
        Create a new Google Form with title and document title, and optionally add description and questions.
        """
        form_obj = data.data
        info = form_obj.get("info", {})

        # Step 1: Create form with title and document title
        create_body = {"info": {"title": info["title"]}}
        if "documentTitle" in info:
            create_body["info"]["documentTitle"] = info["documentTitle"]

        new_form = self.service.forms().create(body=create_body).execute()
        form_id = new_form["formId"]

        # Step 2: Use batchUpdate to add description and questions
        requests = []

        if "description" in info:
            requests.append({
                "updateFormInfo": {
                    "info": {
                        "description": info["description"]
                    },
                    "updateMask": "description"
                }
            })


        if requests:
            self.service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()

        return DataWrapper(data=new_form)


    def set_publish_settings(self, data: DataWrapper, settings: dict) -> None:
        """
        Update form publish settings.
        Args:
            settings: dict matching Forms API settings schema.
        """
        self.service.forms().setPublishSettings(formId=self.form_id, body=settings).execute()
        print("[FormWriter] Publish settings updated.")

    def create_questions(self, data: DataWrapper) -> None:
        """
        Adds multiple questions to the form using batchUpdate.

        Expects:
        data = [
            {
                'title': 'Question 1',
                'questionItem': {
                    'question': {
                        'required': True,
                        'choiceQuestion': {
                            'type': 'RADIO',
                            'options': [{'value': 'Yes'}, {'value': 'No'}],
                            'shuffle': False
                        }
                    }
                }
            },
            {
                'title': 'Question 2',
                'questionItem': {
                    'question': {
                        'required': False,
                        'textQuestion': {}
                    }
                }
            }
        ]
        """
        requests = []
        for index, q in enumerate(data.data):
            requests.append({
                "createItem": {
                    "item": {
                        "title": q["title"],
                        "questionItem": q["questionItem"]
                    },
                    "location": {"index": index}
                }
            })

        self.service.forms().batchUpdate(
            formId=self.form_id,
            body={"requests": requests}
        ).execute()
        print(f"[FormWriter] {len(requests)} question(s) created.")



    def get_operations(self):
        return {
            "batch_update": self.batch_update,
            "write_data": self.write_data,
            "set_publish_settings": self.set_publish_settings,
            "create_questions": self.create_questions
        }
