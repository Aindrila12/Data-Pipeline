from simple_salesforce import Salesforce
from utility.auth import get_credentials
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class SalesforceWriter(Writer):
    """
    Writer for Salesforce operations via simple-salesforce.
    """

    def __init__(self, username: str, password: str, security_token: str, domain: str = None):
        self.username = username
        self.password = password
        self.security_token = security_token
        self.domain = domain
        self.sf = None

    def initialize(self):
        self.sf = Salesforce(
            username=self.username,
            password=self.password,
            security_token=self.security_token,
            domain=self.domain
        )

    def create_record(self, data: DataWrapper, object_name: str) -> DataWrapper:
        """Create records in specified object."""
        created = []
        for row in data.data:
            res = getattr(self.sf, object_name).create(row)
            created.append(res)
        return DataWrapper(data=created)

    def update_record(self, data: DataWrapper, object_name: str, record_id: str) -> None:
        """Update record fields by ID."""
        for fields in data.data:
            getattr(self.sf, object_name).update(record_id, fields)

    def delete_record(self, data: DataWrapper, object_name: str, record_id: str) -> None:
        """Delete a record by ID."""
        getattr(self.sf, object_name).delete(record_id)

    def get_operations(self):
        return {
            "create_record": self.create_record,
            "update_record": self.update_record,
            "delete_record": self.delete_record
        }
