from core.interfaces import Writer
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import io
from googleapiclient.http import MediaIoBaseDownload


class DriveWriter(Writer):
    def __init__(self, folder_id=None, service_name="drive_cred"):
        super().__init__(doc_id=folder_id, service_name=service_name)
        self.folder_id = folder_id
        self.service_name = service_name
        self.service = None

    def initialize(self):
        print(f"[DriveWriter] Initializing for folder: {self.folder_id or 'root'}")
        creds = get_credentials(self.service_name)
        self.service = build("drive", "v3", credentials=creds)

    def write_data(self, data: DataWrapper, file_path: str, mime_type: str, file_name: str) -> None:
        """Uploads a local file to the specified folder on Drive. (params: file_path, mime_type, file_name)"""
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

    def delete_file(self, data: DataWrapper) -> None:
        """Deletes a file by its ID. (params: file_id)"""
        if data.data['id']:
            self.service.files().delete(fileId=data.data['id']).execute()
            print(f"[DriveWriter] Deleted file ID: {data.data['id']}")
        else:
            print(f"Can't Get ID: {data.data['id']}")
        

    def rename_file(self, data: DataWrapper, new_name: str) -> None:
        """Renames a file. (params: file_id, new_name)"""
        self.service.files().update(
            fileId=data.data['id'],
            body={"name": new_name}
        ).execute()
        print(f"[DriveWriter] Renamed file {data.data['id']} to '{new_name}'")

    def create_folder(self, data: DataWrapper, name: str, parent_id: str = None) -> str:
        """Creates a folder in Drive. Returns the folder ID."""
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
    
    def move_file(self, data: DataWrapper, new_parent_id: str) -> None:
        """Moves a file to a new folder."""
        # First get the current parent(s)
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

    def trash_file(self, data: DataWrapper) -> None:
        """Moves a folder to trash."""
        self.service.files().update(
            fileId=data.data['id'],
            body={'trashed': True}
        ).execute()
        print(f"[DriveWriter] Trashed folder ID: {data.data['id']}")

    def download_file(self, data: DataWrapper, destination_path: str) -> None:
        """
        Downloads a file from Google Drive.

        Args:
            data (DataWrapper): Not used directly, but kept for interface consistency.
            destination_path (str): Local path where the file will be saved.
        """
        request = self.service.files().get_media(fileId=data.data['id'])
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"[DriveWriter] Downloading... {int(status.progress() * 100)}%")

        print(f"[DriveWriter] Downloaded file ID: {data.data['id']} to '{destination_path}'")

    def share_file_with_email(self, data: DataWrapper, email: str, role: str = "reader", type_: str = "user") -> None:
        """
        Shares a file with a given email.

        Args:
            data (DataWrapper): Unused, kept for interface consistency.
            email (str): The email address to share the file with.
            role (str): The role to assign (e.g., "reader", "writer", "commenter").
            type_ (str): The type of sharing (e.g., "user", "group", "domain", "anyone").
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
