from pyairtable import Api
from utility.auth import get_credentials
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class AirtableFetcher(Fetcher):
    """
    Fetcher for Airtable: list records, retrieve by ID.
    """

    def __init__(self, base_id: str, table_name: str, service_name: str = "airtable_cred"):
        self.base_id = base_id
        self.table_name = table_name
        self.service_name = service_name
        self.table = None

    def initialize(self):
        api_key = get_credentials(self.service_name)
        api = Api(api_key)
        self.table = api.base(self.base_id).table(self.table_name)

    def fetch_data(self, max_records: int = 100, view: str = None) -> DataWrapper:
        """
        Fetch all matching records (with optional view filter and size limit).
        """
        records = self.table.all(max_records=max_records, view=view)
        return DataWrapper(data=records)

    def fetch_by_id(self, record_id: str) -> DataWrapper:
        """
        Fetch a single record by its ID.
        """
        rec = self.table.get(record_id)
        return DataWrapper(data=[rec])
    
    def prepare_records_payload(self, records: list) -> DataWrapper:
        """
        Prepare record data for Airtable insertion.
        Args:
            records: List of dicts, each dict should be in {'fields': {...}} format.

        Returns:
            DataWrapper with data to pass to writer.
        """
        return DataWrapper(data=records)

    def get_operations(self):
        return {
            "fetch_data": self.fetch_data,
            "fetch_by_id": self.fetch_by_id,
            "prepare_records_payload": self.prepare_records_payload
        }
