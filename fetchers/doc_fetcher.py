# fetchers/google_docs_fetcher.py

from core.interfaces import Fetcher
from core.data_wrapper import DataWrapper

class DocsFetcher(Fetcher):
    def __init__(self, document_id):
        self.document_id = document_id

    def fetch_data(self) -> DataWrapper:
        # Dummy content
        content = [["Title", "Subtitle"], ["Hello", "World"]]
        return DataWrapper(data=content)
