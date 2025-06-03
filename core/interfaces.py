# core/interfaces.py

from abc import ABC, abstractmethod
from core.data_wrapper import DataWrapper

class Fetcher(ABC):
    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def fetch_data(self) -> DataWrapper:
        pass

    @classmethod
    def get_operations(cls):
        """Optionally list available fetch operations."""
        return {}

class Writer(ABC):
    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def write_data(self, data: DataWrapper) -> None:
        pass

    @classmethod
    def get_operations(cls):
        """Optionally list available write operations."""
        return {}
