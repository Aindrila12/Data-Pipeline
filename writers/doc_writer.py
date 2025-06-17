from core.interfaces import Writer
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build


class DocsWriter(Writer):
    def __init__(self, doc_id, service_name="docs_cred"):
        super().__init__(doc_id=doc_id, service_name=service_name)
        self.doc_id = doc_id
        self.service_name = service_name
        self.service = None

    def initialize(self):
        print(f"[DocsWriter] Initializing for document: {self.doc_id}")
        creds = get_credentials(self.service_name)
        self.service = build("docs", "v1", credentials=creds)

    def write_data(self, data: DataWrapper) -> None:
        """Appends all lines as paragraphs at the end of the doc. (params: data)"""
        values = data.data
        if not values:
            print("[DocsWriter] No data to write.")
            return

        # Step 1: Get the document to determine the current end index
        doc = self.service.documents().get(documentId=self.doc_id).execute()
        content = doc.get("body", {}).get("content", [])
        end_index = content[-1].get("endIndex", 1) if content else 1

        # Step 2: Create insertText requests using that end index
        requests = []
        for row in values:
            if row:
                requests.append({
                    "insertText": {
                        "location": {
                            "index": end_index - 1
                        },
                        "text": row[0] + "\n"
                    }
                })
                end_index += len(row[0]) + 1  # +1 for newline

        # Step 3: Send the batch update
        self.service.documents().batchUpdate(
            documentId=self.doc_id,
            body={"requests": requests}
        ).execute()
        print(f"[DocsWriter] Appended {len(values)} paragraphs.")


    def clear_document(self):
        """Clears all user-editable content in the document."""
        doc = self.service.documents().get(documentId=self.doc_id).execute()
        end_index = doc.get("body", {}).get("content", [])[-1].get("endIndex", 1)
        self.service.documents().batchUpdate(
            documentId=self.doc_id,
            body={
                "requests": [{
                    "deleteContentRange": {
                        "range": {
                            "startIndex": 1,
                            "endIndex": end_index - 1
                        }
                    }
                }]
            }
        ).execute()
        print("[DocsWriter] Cleared the document content.")

    def insert_heading(self, data, text, level=1):
        """Inserts a heading of a given level. (params: text, level)"""
        style = f"HEADING_{level}"
        self.service.documents().batchUpdate(
            documentId=self.doc_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": text + "\n"
                        }
                    },
                    {
                        "updateParagraphStyle": {
                            "range": {
                                "startIndex": 1,
                                "endIndex": 1 + len(text) + 1
                            },
                            "paragraphStyle": {
                                "namedStyleType": style
                            },
                            "fields": "namedStyleType"
                        }
                    }
                ]
            }
        ).execute()
        print(f"[DocsWriter] Inserted heading '{text}' (level {level}).")

    def set_document_title(self, new_title: str):
        """Set the title of the document using the Drive API."""
        creds = get_credentials("drive_cred")
        drive_service = build("drive", "v3", credentials=creds)
        drive_service.files().update(
            fileId=self.doc_id,
            body={"name": new_title}
        ).execute()


    
    def get_operations(self):
        return {
            "write_data": self.write_data,
            "clear_document": self.clear_document,
            "insert_heading": self.insert_heading,
            "set_document_title": self.set_document_title
        }
