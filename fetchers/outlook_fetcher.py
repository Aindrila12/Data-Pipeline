from msgraph.core import GraphClient
from azure.identity import ClientSecretCredential
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class OutlookFetcher(Fetcher):
    """
    Fetcher for Outlook Mail using Microsoft Graph API.
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

    def fetch_messages(self, folder: str = "Inbox", top: int = 10) -> DataWrapper:
        """
        Fetch recent messages from a folder.
        """
        resp = self.client.get(f"/me/mailFolders/{folder}/messages?$top={top}")
        items = resp.json().get("value", [])
        return DataWrapper(data=items)

    def get_operations(self):
        return {
            "fetch_messages": self.fetch_messages,
        }
