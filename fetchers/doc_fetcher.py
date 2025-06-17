from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper
from utility.auth import get_credentials
from googleapiclient.discovery import build


class DocsFetcher(Fetcher):
    def __init__(self, doc_id, service_name="docs_cred"):
        super().__init__(document_id=doc_id, service_name=service_name)
        self.document_id = doc_id
        self.service_name = service_name
        self.service = None
        self.document = None

    def initialize(self):
        print(f"[DocsFetcher] Initializing for document: {self.document_id}")
        creds = get_credentials(self.service_name)
        self.service = build("docs", "v1", credentials=creds)
        self.document = self.service.documents().get(documentId=self.document_id).execute()

    def fetch_data(self) -> DataWrapper:
        """Fetch entire document content."""
        body = self.document.get("body", {}).get("content", [])
        text = self._extract_text(body)
        print(f"[DocsFetcher] Fetched document with {len(text)} characters.")
        return DataWrapper(data=[[text]])

    def fetch_paragraphs(self) -> DataWrapper:
        """Return individual paragraphs as list items."""
        body = self.document.get("body", {}).get("content", [])
        paragraphs = self._extract_paragraphs(body)
        return DataWrapper(data=paragraphs)

    def fetch_text_by_heading(self, heading: str) -> DataWrapper:
        """Extract text following a specific heading. (params: heading)"""
        content = self.document.get("body", {}).get("content", [])
        collected, capturing = [], False
        for element in content:
            # print("element >>>>>>>>>>>", element)
            print("\n")
            if "paragraph" in element:
                para = element["paragraph"]
                text = self._paragraph_text(para)
                style = para.get("paragraphStyle", {})
                if heading.lower() in text.lower():
                    capturing = True
                    continue
                if capturing and heading.lower() in text.lower() and text.lower() != heading.lower():
                    break
                if capturing:
                    collected.append(text)

        return DataWrapper(data=[[line] for line in collected if line.strip()])

    def _extract_text(self, content):
        return "\n".join(self._paragraph_text(el["paragraph"]) for el in content if "paragraph" in el)

    def _extract_paragraphs(self, content):
        return [[self._paragraph_text(el["paragraph"])] for el in content if "paragraph" in el]

    def _paragraph_text(self, para):
        return "".join(el.get("textRun", {}).get("content", "") for el in para.get("elements", []))
    
    def get_document_title(self) -> str:
        """Fetch the title of the Google Doc."""
        doc = self.service.documents().get(documentId=self.document_id).execute()
        return doc.get("title", "Untitled")


    
    def get_operations(self):
        return {
            "fetch_data": self.fetch_data,
            "fetch_paragraphs": self.fetch_paragraphs,
            "fetch_text_by_heading": self.fetch_text_by_heading,
            "get_document_title": self.get_document_title
        }
