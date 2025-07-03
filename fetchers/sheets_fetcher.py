# fetchers/sheet_fetcher.py

from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build

class SheetsFetcher(Fetcher):
    """
    A fetcher for reading data from Google Sheets.
    """
    def __init__(self, spreadsheet_id, service_name="docs_cred"):
        """
        Initialize the SheetsFetcher.
        
        Args:
            spreadsheet_id (str): The ID of the Google Sheets document.
            range_name (str): The A1 notation of the range to fetch.
            service_name (str): The credential alias in the auth config.
        """
        try:
            super().__init__(spreadsheet_id=spreadsheet_id, service_name=service_name)
            self.spreadsheet_id = spreadsheet_id
            self.service_name = service_name
            self.service = None
            self.sheet = None
        except Exception as e:
            print(f"Error in sheets_fetcher __init__: {e}")

    def initialize(self):
        """
        Initialize the Sheets API service using credentials.
        """
        try:
            print(f"[SheetsFetcher] Initializing for spreadsheet: {self.spreadsheet_id}")
            creds = get_credentials(self.service_name)
            self.service = build("sheets", "v4", credentials=creds)
            self.sheet = self.service.spreadsheets()
        except Exception as e:
            print(f"Error initializing SheetsFetcher: {e}")

    def fetch_data(self, range_name) -> DataWrapper:
        """
        Fetch values from the specified range in the sheet.

        Returns:
            DataWrapper: The list of rows from the given range.
        """
        try:
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id, range=range_name
            ).execute()
            values = result.get("values", [])
            print(f"[SheetsFetcher] Fetched {len(values)} rows from {range_name}")
            return DataWrapper(data=values)
        except Exception as e:
            print(f"Error in fetch-data: {e}")
            return DataWrapper(data=[])
    
    # Default fetch
    def fetch(self) -> DataWrapper:
        """
        Fetch the entire sheet's data.
        
        Returns:
            DataWrapper: All values as a list of rows.
        """
        try:
            return DataWrapper(self.sheet.get_all_values())
        except Exception as e:
            print(f"Error in fetch: {e}")
            return DataWrapper(data=[])

    def fetch_range(self, range_name) -> DataWrapper:
        """
        Fetch data from a specific range.

        Args:
            range_ (str): A1 notation of the range to fetch.
        
        Returns:
            DataWrapper: List of rows from the range.
        """
        try:
            return DataWrapper(self.sheet.values().get(spreadsheetId=self.spreadsheet_id, range=range_name))
        except Exception as e:
            print(f"Error in fetch_range: {e}")
            return DataWrapper(data=[])

    def fetch_row(self, row_number: int) -> DataWrapper:
        """
        Fetch a specific row by its index using A1 notation.

        Args:
            row_number (int): 1-based row index.
            
        Returns:
            DataWrapper: A single row as a list.
        """
        try:
            # e.g., A1:Z1 to get row 1 (adjust column width as needed)
            range_ = f"A{row_number}:Z{row_number}"
            result = self.sheet.get(
                spreadsheetId=self.spreadsheet_id,
                range=range_
            ).execute()
            row = result.get("values", [[]])[0]  # fallback to empty row if missing
            return DataWrapper(data=[row])
        except Exception as e:
            print(f"Error in fetch_row: {e}")
            return DataWrapper(data=[])


    import string

    def fetch_column(self, col_number: int) -> DataWrapper:
        """
        Fetch a specific column by its index using A1 notation.

        Args:
            col_number (int): The 1-based column index to fetch.

        Returns:
            DataWrapper: A single column as a list.
        """
        try:
            # Convert number to column letter, e.g., 1 -> A, 2 -> B, etc.
            def col_number_to_letter(n):
                result = ""
                while n:
                    n, remainder = divmod(n - 1, 26)
                    result = chr(65 + remainder) + result
                return result

            col_letter = col_number_to_letter(col_number)
            range_ = f"{col_letter}1:{col_letter}1000"  # Adjust row range as needed

            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_
            ).execute()
            values = result.get("values", [])

            # Flatten and return as list
            col_values = [row[0] if row else "" for row in values]
            return DataWrapper(data=col_values)

        except Exception as e:
            print(f"Error in fetch_column: {e}")
            return DataWrapper(data=[])


    def fetch_column_by_header(self, header_name: str) -> DataWrapper:
        """
        Fetch a column based on its header name.

        Args:
            header_name (str): The name of the column header.
        
        Returns:
            DataWrapper: A single column as a list.
        """
        try:
            headers = self.sheet.row_values(1)
            col_idx = headers.index(header_name) + 1 if header_name in headers else None
            return DataWrapper([self.sheet.col_values(col_idx)]) if col_idx else DataWrapper([])
        except Exception as e:
            print(f"Error in fetch_column_by_header: {e}")
            return DataWrapper(data=[])

    def fetch_rows_by_condition(self, col_name: str, match_value: str) -> DataWrapper:
        """
        Fetch rows where a given column matches a specific value.

        Args:
            col_name (str): The name of the column to check.
            match_value (str): The value to match.
        
        Returns:
            DataWrapper: List of matching rows.
        """
        try:
            headers = self.sheet.row_values(1)
            col_idx = headers.index(col_name)
            all_rows = self.sheet.get_all_values()[1:]
            matched = [row for row in all_rows if len(row) > col_idx and row[col_idx] == match_value]
            return DataWrapper(matched)
        except Exception as e:
            print(f"Error in fetch_rows_by_condition: {e}")
            return DataWrapper(data=[])

    def get_headers(self) -> DataWrapper:
        """
        Get column headers from the first row.

        Returns:
            DataWrapper: List of header names.
        """
        try:
            return DataWrapper([self.sheet.row_values(1)])
        except Exception as e:
            print(f"Error in get_headers: {e}")
            return DataWrapper(data=[])

    def get_dimensions(self) -> DataWrapper:
        """
        Get number of rows and columns in the sheet.

        Returns:
            DataWrapper: A list with [row_count, column_count].
        """
        try:
            rows = len(self.sheet.get_all_values())
            cols = len(self.sheet.row_values(1))
            return DataWrapper([[rows, cols]])
        except Exception as e:
            print(f"Error in get_dimensions: {e}")
            return DataWrapper(data=[[0, 0]])

    
    def get_operations(self):
        return {
            "fetch": self.fetch,
            "ftech_data": self.fetch_data,
            "fetch_range": self.fetch_range,
            "fetch_row": self.fetch_row,
            "fetch_column": self.fetch_column,
            # "fetch_column_by_header": self.fetch_column_by_header,
            # "fetch_rows_by_condition": self.fetch_rows_by_condition,
            # "get_headers": self.get_headers,
            # "get_dimensions": self.get_dimensions,
        }
