import dropbox
from utility.auth import get_credentials
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class DropboxWriter(Writer):
    """
    Write operations in Dropbox: upload, create/move/delete folders/files.
    """
    def __init__(self, access_token: str = None):
        self.access_token = access_token or get_credentials("dropbox_cred")
        self.client = None

    def initialize(self):
        self.client = dropbox.Dropbox(self.access_token)

    def upload_file(self, data: DataWrapper, dest_path: str, mode: str = "add"):
        """
        Upload a file.

        Args:
            data: DataWrapper with {"content": bytes}
            dest_path: Target Dropbox path
            mode: add or overwrite
        """
        content = data.data.get("content") if isinstance(data.data, dict) else data.data
        mode_enum = dropbox.files.WriteMode.overwrite if mode == "overwrite" else dropbox.files.WriteMode.add
        self.client.files_upload(content, dest_path, mode=mode_enum)

    def create_folder(self, path: str):
        """
        Create a new folder in Dropbox.
        """
        self.client.files_create_folder_v2(path)

    def move(self, from_path: str, to_path: str):
        """
        Move or rename a file or folder.
        """
        self.client.files_move_v2(from_path, to_path)

    def delete(self, path: str):
        """
        Delete a file or folder.
        """
        self.client.files_delete_v2(path)

    def get_operations(self):
        return {
            "upload_file": self.upload_file,
            "create_folder": self.create_folder,
            "move": self.move,
            "delete": self.delete,
        }
