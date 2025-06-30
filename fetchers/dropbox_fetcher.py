import dropbox
from utility.auth import get_credentials
from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class DropboxFetcher(Fetcher):
    """
    Fetch data from Dropbox: list folder contents, download files, read local files.
    """

    def __init__(self, access_token: str = None):
        """
        Initialize Dropbox client.

        Args:
            access_token: Dropbox API token (optional if using get_credentials)
        """
        self.access_token = access_token or get_credentials("dropbox_cred")
        self.client = None

    def initialize(self):
        """
        Initialize the Dropbox client.
        """
        self.client = dropbox.Dropbox(self.access_token)

    def fetch_data(self, path: str = "", recursive: bool = False) -> DataWrapper:
        """
        List files/folders in the given Dropbox path.

        Args:
            path: Dropbox folder path.
            recursive: If True, list subfolders recursively.

        Returns:
            DataWrapper containing file/folder metadata entries.
        """
        res = self.client.files_list_folder(path=path, recursive=recursive)
        entries = res.entries

        # Handle pagination
        while res.has_more:
            res = self.client.files_list_folder_continue(res.cursor)
            entries.extend(res.entries)

        return DataWrapper(data=entries)

    def download_file(self, path: str) -> DataWrapper:
        """
        Download file contents from Dropbox.

        Args:
            path: Dropbox file path to download.

        Returns:
            DataWrapper with file metadata and content bytes.
        """
        md, resp = self.client.files_download(path)
        return DataWrapper(data={"metadata": md, "content": resp.content})

    def get_file_content(self, file_path: str) -> DataWrapper:
        """
        Read binary content from a local file and return wrapped data.

        Args:
            file_path: Local file path to read from.

        Returns:
            DataWrapper with {"content": file_bytes}
        """
        with open(file_path, "rb") as f:
            content = f.read()
        return DataWrapper(data={"content": content})

    def get_operations(self):
        return {
            "fetch_data": self.fetch_data,
            "download_file": self.download_file,
            "get_file_content": self.get_file_content,
        }
