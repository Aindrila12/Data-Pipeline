from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build


class DriveFetcher(Fetcher):
    def __init__(self, folder_id=None, service_name="drive_cred"):
        super().__init__(doc_id=folder_id, service_name=service_name)
        self.folder_id = folder_id
        self.service_name = service_name
        self.service = None

    def initialize(self):
        print(f"[DriveFetcher] Initializing for folder: {self.folder_id or 'root'}")
        creds = get_credentials(self.service_name)
        self.service = build("drive", "v3", credentials=creds)

    def fetch_data(self) -> DataWrapper:
        """List files in the specified folder (or root if not specified)."""
        query = f"'{self.folder_id}' in parents" if self.folder_id else "'root' in parents"
        response = self.service.files().list(
            q=query,
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()

        files = response.get("files", [])
        result = [[file["id"], file["name"], file["mimeType"], file["modifiedTime"]] for file in files]
        print(f"[DriveFetcher] Retrieved {len(result)} files.")
        return DataWrapper(data=result)

    def get_file_metadata(self, file_id: str) -> DataWrapper:
        """Fetch metadata of a specific file."""
        metadata = self.service.files().get(fileId=file_id, fields="id, name, mimeType, size, createdTime").execute()
        return DataWrapper(data=[[metadata.get("id"), metadata.get("name"), metadata.get("mimeType"),
                                  metadata.get("size"), metadata.get("createdTime")]])
    

    def fetch_file_id_by_name(self, filename, parent_folder_id=None, exact_match=True):
        """
        Fetch the file ID for a given file name in Google Drive.

        Args:
            service (Resource): An authenticated Google Drive API service instance.
            filename (str): The name of the file to search for.
            parent_folder_id (str, optional): If specified, restricts the search to a specific folder.
            exact_match (bool): If True, looks for exact filename match. If False, allows partial matches.

        Returns:
            str or None: The file ID if found, else None.
        """
        query_parts = ["trashed = false"]
        if exact_match:
            query_parts.append(f"name = '{filename}'")
        else:
            query_parts.append(f"name contains '{filename}'")

        if parent_folder_id == "None":
            parent_folder_id = None

        if parent_folder_id:
            query_parts.append(f"'{parent_folder_id}' in parents")

        query = " and ".join(query_parts)

        try:
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=10
            ).execute()
            files = results.get('files', [])
            if files:
                return DataWrapper(data=files[0]) # Return the first matching file
            return DataWrapper(data=None) 
        except Exception as e:
            print(f"Error fetching file ID: {e}")
            return DataWrapper(data=None) 


    def get_operations(self):
        return {
            "fetch_data": self.fetch_data,
            "get_file_metadata": self.get_file_metadata,
            "fetch_file_id_by_name": self.fetch_file_id_by_name
        }
