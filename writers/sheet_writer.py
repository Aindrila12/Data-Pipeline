# writers/sheet_writer.py

from core.interfaces import Writer
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build


class SheetsWriter(Writer):
    def __init__(self, sheet_id, mode="overwrite", range_name="Sheet1!A1", service_name="sheets_cred"):
        super().__init__(sheet_id=sheet_id, mode=mode, range_name=range_name, service_name=service_name)
        self.sheet_id = sheet_id
        self.mode = mode
        self.range_name = range_name
        self.service_name = service_name
        self.service = None
        self.sheet = None

    def initialize(self):
        print(f"[SheetsWriter] Initializing for spreadsheet: {self.sheet_id}")
        creds = get_credentials(self.service_name)
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet = self.service.spreadsheets().values()

    def write_data(self, data: DataWrapper) -> None:
        mode = self.config.get("mode", "append")
        values = data.data

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

    def update_cell(self, row, col, value):
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


    def update_by_header(self, row_number, header_name, value):
        # Fetch headers from the first row
        result = self.sheet.get(
            spreadsheetId=self.sheet_id,
            range="Sheet1!1:1"
        ).execute()
        headers = result.get("values", [[]])[0]

        if header_name not in headers:
            raise ValueError(f"Header '{header_name}' not found in sheet")

        col_idx = headers.index(header_name) + 1  # 1-based index
        self.update_cell(row_number, col_idx, value)


    def delete_row(self, row_number):
        body = {
            "requests": [{
                "deleteDimension": {
                    "range": {
                        "sheetId": self.sheet_id,  # usually 0 for first sheet; otherwise use actual sheetId
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


    @classmethod
    def get_operations(cls):
        return {
            "write_data": cls.write_data,
            "update_cell": cls.update_cell,
            "update_by_header": cls.update_by_header,
            "delete_row": cls.delete_row,
        }
