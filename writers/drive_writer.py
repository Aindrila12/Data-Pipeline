from core.interfaces import Writer
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import io
from googleapiclient.http import MediaIoBaseDownload


class DriveWriter(Writer):
    """
    Writer class to perform operations on Google Drive such as uploading,
    deleting, renaming, downloading, and sharing files and folders.
    """
    def __init__(self, folder_id=None, service_name="drive_cred"):
        """
        Initialize the DriveWriter.

        Args:
            folder_id (str, optional): ID of the target folder. Defaults to root if None.
            service_name (str): Name of the credential configuration.
        """
        try:
            super().__init__(doc_id=folder_id, service_name=service_name)
            self.folder_id = folder_id
            self.service_name = service_name
            self.service = None
        except Exception as e:
            print(f"[DriveWriter] Initialization error: {e}")
            raise e

    def initialize(self):
        """
        Initialize the Google Drive API service using provided credentials.
        """
        try:
            print(f"[DriveWriter] Initializing for folder: {self.folder_id or 'root'}")
            creds = get_credentials(self.service_name)
            self.service = build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"[DriveWriter] Error initializing service: {e}")
            raise e

    def write_data(self, data: DataWrapper, file_path: str, mime_type: str, file_name: str) -> None:
        """
        Upload a file to Google Drive.

        Args:
            data (DataWrapper): Unused but kept for consistency.
            file_path (str): Path to the local file.
            mime_type (str): MIME type of the file (e.g., "application/pdf").
            file_name (str): Name to assign to the file in Drive.
        """
        try:
            file_metadata = {"name": file_name}
            if self.folder_id:
                file_metadata["parents"] = [self.folder_id]

            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()

            print(f"[DriveWriter] Uploaded file '{file_name}' with ID: {file.get('id')}")
        except Exception as e:
            print(f"[DriveWriter] Error uploading file: {e}")
            raise e

    def delete_file(self, data: DataWrapper) -> None:
        """
        Delete a file from Google Drive by file ID.

        Args:
            data (DataWrapper): Should contain file ID in data['id'].
        """
        try:
            if data.data['id']:
                self.service.files().delete(fileId=data.data['id']).execute()
                print(f"[DriveWriter] Deleted file ID: {data.data['id']}")
            else:
                print(f"Can't Get ID: {data.data['id']}")
        except Exception as e:
            print(f"[DriveWriter] Error deleting file: {e}")
            raise e
        

    def rename_file(self, data: DataWrapper, new_name: str) -> None:
        """
        Rename a file in Google Drive.

        Args:
            data (DataWrapper): Should contain file ID in data['id'].
            new_name (str): New name to assign to the file.
        """
        try:
            self.service.files().update(
                fileId=data.data['id'],
                body={"name": new_name}
            ).execute()
            print(f"[DriveWriter] Renamed file {data.data['id']} to '{new_name}'")
        except Exception as e:  
            print(f"[DriveWriter] Error renaming file: {e}")
            raise e

    def create_folder(self, data: DataWrapper, name: str, parent_id: str = None) -> str:
        """
        Create a new folder in Google Drive.

        Args:
            data (DataWrapper): Unused, kept for interface consistency.
            name (str): Name of the folder to create.
            parent_id (str, optional): ID of the parent folder. Defaults to root.

        Returns:
            str: ID of the created folder.
        """
        try:
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            folder_id = folder.get('id')
            print(f"[DriveWriter] Created folder '{name}' with ID: {folder_id}")
            return folder_id
        except Exception as e:
            print(f"[DriveWriter] Error creating folder: {e}")
            raise e
    
    def move_file(self, data: DataWrapper, new_parent_id: str) -> None:
        """
        Move a file to a different folder.

        Args:
            data (DataWrapper): Should contain file ID in data['id'].
            new_parent_id (str): ID of the destination folder.
        """
        # First get the current parent(s)
        try:
            file = self.service.files().get(fileId=data.data['id'], fields='parents').execute()
            previous_parents = ",".join(file.get('parents', []))

            # Move the file
            self.service.files().update(
                fileId=data.data['id'],
                addParents=new_parent_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()

            print(f"[DriveWriter] Moved file ID: {data.data['id']} to folder ID: {new_parent_id}")
        except Exception as e:
            print(f"[DriveWriter] Error moving file: {e}")
            raise e

    def trash_file(self, data: DataWrapper) -> None:
        """
        Move a file or folder to trash.

        Args:
            data (DataWrapper): Should contain file ID in data['id'].
        """
        try:
            self.service.files().update(
                fileId=data.data['id'],
                body={'trashed': True}
            ).execute()
            print(f"[DriveWriter] Trashed folder ID: {data.data['id']}")
        except Exception as e:
            print(f"[DriveWriter] Error trashing file: {e}")
            raise e

    def download_file(self, data: DataWrapper, destination_path: str) -> None:
        """
        Download a file from Google Drive.

        Args:
            data (DataWrapper): Should contain file ID in data['id'].
            destination_path (str): Local path to save the downloaded file.
        """
        try:
            request = self.service.files().get_media(fileId=data.data['id'])
            fh = io.FileIO(destination_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"[DriveWriter] Downloading... {int(status.progress() * 100)}%")

            print(f"[DriveWriter] Downloaded file ID: {data.data['id']} to '{destination_path}'")
        except Exception as e:
            print(f"[DriveWriter] Error downloading file: {e}")
            raise e

    def share_file_with_email(self, data: DataWrapper, email: str, role: str = "reader", type_: str = "user") -> None:
        """
        Share a file with another user by email.

        Args:
            data (DataWrapper): Should contain file ID in data['id'].
            email (str): Email address to share the file with.
            role (str): Permission role ("reader", "writer", etc.).
            type_ (str): Type of entity ("user", "group", "domain", "anyone").
        """
        try:
            permission = {
                "type": type_,
                "role": role,
                "emailAddress": email
            }

            result = self.service.permissions().create(
                fileId=data.data['id'],
                body=permission,
                fields="id",
                sendNotificationEmail=True
            ).execute()

            print(f"[DriveWriter] Shared file {data.data['id']} with {email}. Permission ID: {result.get('id')}")

        except Exception as e:
            print(f"[DriveWriter] Error sharing file: {e}")




    def get_operations(self):
        return {
            "write_data": self.write_data,
            "delete_file": self.delete_file,
            "rename_file": self.rename_file,
            "create_folder": self.create_folder,
            "move_file": self.move_file,
            "trash_file": self.trash_file,
            "download_file": self.download_file,
            "share_file_with_email": self.share_file_with_email
        }
