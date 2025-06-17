# fetchers/sheet_fetcher.py

from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build

class SheetsFetcher(Fetcher):
    def __init__(self, spreadsheet_id, range_name, service_name="docs_cred"):
        super().__init__(spreadsheet_id=spreadsheet_id, range_name=range_name, service_name=service_name)
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        self.service_name = service_name
        self.service = None
        self.sheet = None

    def initialize(self):
        print(f"[SheetsFetcher] Initializing for spreadsheet: {self.spreadsheet_id}")
        creds = get_credentials(self.service_name)
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet = self.service.spreadsheets()

    def fetch_data(self) -> DataWrapper:
        result = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id, range=self.range_name
        ).execute()
        values = result.get("values", [])
        print(f"[SheetsFetcher] Fetched {len(values)} rows from {self.range_name}")
        return DataWrapper(data=values)
    
    # Default fetch
    def fetch(self) -> DataWrapper:
        """Fetch the entire sheet data as a list of rows."""
        return DataWrapper(self.sheet.get_all_values())

    def fetch_range(self, range_: str) -> DataWrapper:
        """Fetch data from a specific range in the sheet.(params: range_)"""
        return DataWrapper(self.sheet.get(range_))

    def fetch_row(self, row_number: int) -> DataWrapper:
        """Fetch a single row by its index.(params: row_number)"""
        return DataWrapper([self.sheet.row_values(row_number)])

    def fetch_column(self, col_number: int) -> DataWrapper:
        """Fetch a column by its index. (params: col_number)"""
        return DataWrapper([self.sheet.col_values(col_number)])

    def fetch_column_by_header(self, header_name: str) -> DataWrapper:
        """Fetch a column by matching the header name. (params: header_name)"""
        headers = self.sheet.row_values(1)
        col_idx = headers.index(header_name) + 1 if header_name in headers else None
        return DataWrapper([self.sheet.col_values(col_idx)]) if col_idx else DataWrapper([])

    def fetch_rows_by_condition(self, col_name: str, match_value: str) -> DataWrapper:
        """Fetch rows where a column matches a specific value. (params: col_name, match_value)"""
        headers = self.sheet.row_values(1)
        col_idx = headers.index(col_name)
        all_rows = self.sheet.get_all_values()[1:]
        matched = [row for row in all_rows if len(row) > col_idx and row[col_idx] == match_value]
        return DataWrapper(matched)

    def get_headers(self) -> DataWrapper:
        """Get all column headers from the first row."""
        return DataWrapper([self.sheet.row_values(1)])

    def get_dimensions(self) -> DataWrapper:
        """Return the number of rows and columns in the sheet."""
        rows = len(self.sheet.get_all_values())
        cols = len(self.sheet.row_values(1))
        return DataWrapper([[rows, cols]])

    @classmethod
    def get_operations(cls):
        return {
            "fetch": cls.fetch,
            "fetch_range": cls.fetch_range,
            "fetch_row": cls.fetch_row,
            "fetch_column": cls.fetch_column,
            "fetch_column_by_header": cls.fetch_column_by_header,
            "fetch_rows_by_condition": cls.fetch_rows_by_condition,
            "get_headers": cls.get_headers,
            "get_dimensions": cls.get_dimensions,
        }
