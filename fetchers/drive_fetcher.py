from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build


class DriveFetcher(Fetcher):

    """
    Fetcher class for interacting with Google Drive. Supports listing files,
    retrieving metadata, and searching for files by name.
    """

    def __init__(self, folder_id=None, service_name="drive_cred"):
        """
        Initialize the DriveFetcher.

        Args:
            folder_id (str, optional): The ID of the folder to operate in. Defaults to None (root folder).
            service_name (str): Credential identifier for Google Drive API access.
        """
        try:
            super().__init__(doc_id=folder_id, service_name=service_name)
            self.folder_id = folder_id
            self.service_name = service_name
            self.service = None
        except Exception as e:
            print(f"[DriveFetcher] Initialization error: {e}")
            raise e

    def initialize(self):
        """
        Set up the Google Drive API service using credentials.
        """
        try:
            print(f"[DriveFetcher] Initializing for folder: {self.folder_id or 'root'}")
            creds = get_credentials(self.service_name)
            self.service = build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"[DriveFetcher] Error initializing service: {e}")
            raise e

    def fetch_data(self) -> DataWrapper:
        """
        Fetches a list of files from the specified folder (or root if none provided).

        Returns:
            DataWrapper: A list of files with ID, name, mime type, and modified time.
        """
        try:
            query = f"'{self.folder_id}' in parents" if self.folder_id else "'root' in parents"
            response = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, modifiedTime)"
            ).execute()

            files = response.get("files", [])
            result = [[file["id"], file["name"], file["mimeType"], file["modifiedTime"]] for file in files]
            print(f"[DriveFetcher] Retrieved {len(result)} files.")
            return DataWrapper(data=result)
        except Exception as e:
            print(f"[DriveFetcher] Error fetching data: {e}")
            return DataWrapper(data=[])

    def get_file_metadata(self, file_id: str) -> DataWrapper:
        """
        Retrieves metadata for a specific file by its ID.

        Args:
            file_id (str): The ID of the file to fetch metadata for.

        Returns:
            DataWrapper: Metadata including ID, name, mime type, size, and created time.
        """
        try:
            metadata = self.service.files().get(fileId=file_id, fields="id, name, mimeType, size, createdTime").execute()
            return DataWrapper(data=[[metadata.get("id"), metadata.get("name"), metadata.get("mimeType"),
                                    metadata.get("size"), metadata.get("createdTime")]])
        except Exception as e:
            print(f"[DriveFetcher] Error fetching file metadata: {e}")
            return DataWrapper(data=[])
    

    def fetch_file_id_by_name(self, filename, parent_folder_id=None, exact_match=True):
        """
        Search for a file by name and return its ID.

        Args:
            filename (str): The name of the file to search for.
            parent_folder_id (str, optional): Limit search to a specific folder. Defaults to None.
            exact_match (bool): If True, searches for exact match; if False, allows partial matches.

        Returns:
            DataWrapper: File metadata of the first match or None if no match is found.
        """
        try:
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
        except Exception as e:
            print(f"[DriveFetcher] Error in fetch_file_id_by_name: {e}")
            return DataWrapper(data=None)


    def get_operations(self):
        return {
            "fetch_data": self.fetch_data,
            "get_file_metadata": self.get_file_metadata,
            "fetch_file_id_by_name": self.fetch_file_id_by_name
        }
