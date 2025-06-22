from simple_salesforce import Salesforce, SalesforceLogin
from utility.auth import get_credentials
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class SalesforceFetcher(Fetcher):
    """
    Fetcher for Salesforce using simple-salesforce client.
    """

    def __init__(self, username: str, password: str, security_token: str, domain: str = None):
        self.username = username
        self.password = password
        self.security_token = security_token
        self.domain = domain  # "test" for sandbox
        self.sf = None

    def initialize(self):
        self.sf = Salesforce(
            username=self.username,
            password=self.password,
            security_token=self.security_token,
            domain=self.domain
        )

    def fetch_object(self, object_name: str, record_id: str) -> DataWrapper:
        """Fetch a single record by ID."""
        rec = getattr(self.sf, object_name).get(record_id)
        return DataWrapper(data=[rec])

    def query(self, soql: str) -> DataWrapper:
        """Run SOQL query and return all records."""
        result = self.sf.query_all(soql)
        return DataWrapper(data=result.get("records", []))

    def get_operations(self):
        return {
            "fetch_object": self.fetch_object,
            "query": self.query
        }
