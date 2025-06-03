# core/data_wrapper.py

from typing import Any, Dict, List

class DataWrapper:
    def __init__(self, data: Any, metadata: Dict[str, Any] = None):
        self.data = data
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<DataWrapper data={type(self.data)} metadata={self.metadata}>"
