# writers/sheet_writer.py

from core.interfaces import Writer
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build


class SheetsWriter(Writer):
    """
    A writer class to write and manipulate data in Google Sheets.
    Supports append, overwrite, cell updates, and row deletions.
    """
    def __init__(self, sheet_id, range_name="Sheet1!A1", service_name="sheets_cred"):
        """
        Initialize the SheetsWriter.

        Args:
            sheet_id (str): The ID of the target Google Sheet.
            mode (str): Writing mode - either 'append' or 'overwrite'.
            range_name (str): The A1 notation range to write into.
            service_name (str): Credential alias from auth config.
        """
        try:
            super().__init__(sheet_id=sheet_id, range_name=range_name, service_name=service_name)
            self.sheet_id = sheet_id
            self.range_name = range_name
            self.service_name = service_name
            self.service = None
            self.sheet = None
        except Exception as e:
            print(f"[SheetsWriter] Error in __init__: {e}")
            raise

    def initialize(self):
        """
        Initialize the Sheets API service using credentials.
        """
        try:
            print(f"[SheetsWriter] Initializing for spreadsheet: {self.sheet_id}")
            creds = get_credentials(self.service_name)
            self.service = build("sheets", "v4", credentials=creds)
            self.sheet = self.service.spreadsheets().values()
        except Exception as e:
            print(f"[SheetsWriter] Error initializing SheetsWriter: {e}")
            raise

    def write_data(self, data: DataWrapper, mode="append") -> None:
        """
        Write data to the Google Sheet.

        If mode is 'append', data will be appended at the bottom of the range.
        If mode is 'overwrite', the target range is cleared before writing.

        Args:
            data (DataWrapper): Data to write as a list of lists.
        """
        try:
            values = data.data
            print("1111111111111111", data.data)

            if not values:
                print("[SheetsWriter] No data to write.")
                return
            if mode == "append":
                body = {"values": values}
                response = self.sheet.append(
                    spreadsheetId=self.sheet_id,
                    range=self.range_name,
                    valueInputOption="RAW",
                    body=body
                ).execute()
                print(f"[SheetsWriter] Appended {len(values)} rows.")
            elif mode == "overwrite":
                # First clear the range
                self.service.spreadsheets().values().clear(
                    spreadsheetId=self.sheet_id,
                    range=self.range_name,
                    body={}
                ).execute()

                # Then write new data
                body = {"values": values}
                self.sheet.update(
                    spreadsheetId=self.sheet_id,
                    range=self.range_name,
                    valueInputOption="RAW",
                    body=body
                ).execute()
                print(f"[SheetsWriter] Overwrote range with {len(values)} rows.")
            else:
                print(f"[SheetsWriter] Unsupported mode: {mode}")
        except Exception as e:
            print(f"[SheetsWriter] Error in write_data: {e}")
            raise

    def _to_A1(self, row: int, col: int) -> str:
        """
        Convert row and column numbers to A1 notation.

        Args:
            row (int): 1-based row number.
            col (int): 1-based column number.

        Returns:
            str: A1 notation string.
        """
        col_str = ""
        while col > 0:
            col, rem = divmod(col - 1, 26)
            col_str = chr(rem + ord('A')) + col_str
        return f"{col_str}{row}"


    def update_cell(self, data: DataWrapper, row, col, value):
        """
        Update a specific cell based on its row and column.

        Args:
            row (int): 1-based row index.
            col (int): 1-based column index.
            value (str): The value to write to the cell.
        """
        try:
            cell = self._to_A1(row, col)
            body = {
                "values": [[value]]
            }
            self.sheet.update(
                spreadsheetId=self.sheet_id,
                range=cell,
                valueInputOption="RAW",
                body=body
            ).execute()
            print(f"[SheetsWriter] Updated cell {cell} with value: {value}")
        except Exception as e:
            print(f"[SheetsWriter] Error in update_cell: {e}")
            raise


    def update_by_header(self, data: DataWrapper, row_number, header_name, value):
        """
        Update a cell by matching its header name.

        Args:
            row_number (int): 1-based row index.
            header_name (str): Column header name to identify the column.
            value (str): The new value to assign to the cell.
        
        Raises:
            ValueError: If the header name is not found.
        """
        # Fetch headers from the first row
        try:
            result = self.sheet.get(
                spreadsheetId=self.sheet_id,
                range="Sheet1!1:1"
            ).execute()
            headers = result.get("values", [[]])[0]

            if header_name not in headers:
                raise ValueError(f"Header '{header_name}' not found in sheet")

            col_idx = headers.index(header_name) + 1  # 1-based index
            self.update_cell(row_number, col_idx, value)
        except Exception as e:
            print(f"[SheetsWriter] Error in update_by_header: {e}")
            raise


    def delete_row(self, data: DataWrapper, row_number):
        """
        Delete a row by its 1-based index.

        Note:
            - This uses the `batchUpdate` API, which requires the `sheetId`, not the spreadsheetId.
            - Ensure you pass the correct `sheetId` (tab-level ID), not the document-level spreadsheet ID.

        Args:
            row_number (int): 1-based row index to delete.
        """
        try:
            body = {
                "requests": [{
                    "deleteDimension": {
                        "range": {
                            "sheetId": 0,  # usually 0 for first sheet; otherwise use actual sheetId
                            "dimension": "ROWS",
                            "startIndex": row_number - 1,  # 0-based index
                            "endIndex": row_number
                        }
                    }
                }]
            }

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id,
                body=body
            ).execute()
            print(f"[SheetsWriter] Deleted row {row_number}")
        except Exception as e:
            print(f"[SheetsWriter] Error in delete_row: {e}")
            raise


    
    def get_operations(self):
        return {
            "write_data": self.write_data,
            "update_cell": self.update_cell,
            "update_by_header": self.update_by_header,
            "delete_row": self.delete_row,
        }
