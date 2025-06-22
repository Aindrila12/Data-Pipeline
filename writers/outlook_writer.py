from msgraph.core import GraphClient
from azure.identity import ClientSecretCredential
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class OutlookWriter(Writer):
    """
    Writer to send Outlook emails via Microsoft Graph.
    """

    def __init__(self, client_id: str, client_secret: str, tenant_id: str, service_name="outlook_cred"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.service_name = service_name
        self.client = None

    def initialize(self):
        cred = ClientSecretCredential(tenant_id=self.tenant_id, client_id=self.client_id, client_secret=self.client_secret)
        self.client = GraphClient(credential=cred, scopes=["https://graph.microsoft.com/.default"])

    def send_mail(self, data: DataWrapper, message: dict, save_to_sent_items: bool = True):
        """
        Send an email.
        """
        body = {"message": message, "saveToSentItems": save_to_sent_items}
        self.client.post("/me/sendMail", json=body)

    def get_operations(self):
        return {
            "send_mail": self.send_mail,
        }
