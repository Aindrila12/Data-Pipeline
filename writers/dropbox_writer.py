import dropbox
from utility.auth import get_credentials
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class DropboxWriter(Writer):
    """
    Write operations to Dropbox: upload, create/move/delete folders or files.
    """
    def __init__(self, access_token: str = None):
        self.access_token = access_token or get_credentials("dropbox_cred")
        self.client = None

    def initialize(self):
        self.client = dropbox.Dropbox(self.access_token)

    def write_data(self, data: DataWrapper, dest_path: str, mode: str = "add") -> None:
        """
        Upload a file.

        Args:
            data: DataWrapper containing {"content": bytes}
            dest_path: Dropbox destination path (e.g., "/folder/filename.txt")
            mode: "add" to create a new version or "overwrite" to replace
        """
        content = data.data.get("content") if isinstance(data.data, dict) else data.data
        mode_enum = dropbox.files.WriteMode.overwrite if mode == "overwrite" else dropbox.files.WriteMode.add
        self.client.files_upload(content, dest_path, mode=mode_enum)

    def create_folder(self, data: DataWrapper, path: str) -> None:
        """
        Create a folder at the given path in Dropbox.

        Args:
            path: Dropbox path (e.g., "/new_folder")
        """
        self.client.files_create_folder_v2(path)

    def move(self, data: DataWrapper, from_path: str, to_path: str) -> None:
        """
        Move or rename a file or folder.

        Args:
            from_path: Existing path
            to_path: New path
        """
        self.client.files_move_v2(from_path, to_path)

    def delete(self, data: DataWrapper, path: str) -> None:
        """
        Delete a file or folder at the given path.

        Args:
            path: Dropbox path
        """
        self.client.files_delete_v2(path)

    def save_file(self, data: DataWrapper, save_path: str) -> None:
        content = data.data.get("content")
        with open(save_path, "wb") as f:
            f.write(content)


    def get_operations(self):
        return {
            "write_data": self.write_data,
            "create_folder": self.create_folder,
            "move": self.move,
            "delete": self.delete,
            "save_file": self.save_file
        }
