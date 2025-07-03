from pyairtable import Api
from utility.auth import get_credentials
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class AirtableWriter(Writer):
    """
    Writer for Airtable: create, update, delete records.
    """

    def __init__(self, base_id: str, table_name: str, service_name: str = "airtable_cred"):
        self.base_id = base_id
        self.table_name = table_name
        self.service_name = service_name
        self.table = None

    def initialize(self):
        print("///////////////////////////")
        api_key = get_credentials(self.service_name)
        api = Api(api_key)
        print("api&&&&&&&&&&&&&&&&&&&&&&", api, api_key)
        self.table = api.base(self.base_id).table(self.table_name)
        print("self.table******************", self.table)

    def write_data(self, data: DataWrapper) -> DataWrapper:
        """
        Create one or more records.
        Expects data.data = list of field-dicts:
            [{'fields': {...}}, ...]
        """
        created = self.table.batch_create(data.data)
        return DataWrapper(data=created)

    def update_records(self, data: DataWrapper) -> DataWrapper:
        """
        Update records.
        Expects data.data = list like:
            [{'id': 'recXXX', 'fields': {...}}, ...]
        """
        updated = self.table.batch_update(data.data)
        return DataWrapper(data=updated)

    def delete_records(self, data: DataWrapper) -> DataWrapper:
        """
        Delete records by ID.
        Expects data.data = list of record IDs:
            ['recXXX', ...]
        """
        result = self.table.batch_delete(data.data)
        return DataWrapper(data=result)

    def get_operations(self):
        return {
            "write_data": self.write_data,
            "update_records": self.update_records,
            "delete_records": self.delete_records,
        }

