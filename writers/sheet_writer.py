# writers/google_sheets_writer.py

from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class SheetsWriter(Writer):
    def __init__(self, sheet_id, mode="overwrite"):
        self.sheet_id = sheet_id
        self.mode = mode

    def write_data(self, data_wrapper: DataWrapper) -> None:
        print(f"Writing to sheet {self.sheet_id} in {self.mode} mode")
        for row in data_wrapper.data:
            print("→", row)
