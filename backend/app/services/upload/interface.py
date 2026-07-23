import os
import uuid
import hashlib
from abc import ABC, abstractmethod
from pydantic import BaseModel

class StorageResult(BaseModel):
    storage_id: str
    stored_path: str
    file_size: int
    checksum: str
    success: bool

class StorageInterface(ABC):
    @abstractmethod
    def store_document(self, file_content: bytes, filename: str) -> StorageResult:
        """
        Stores the binary document and returns a structured StorageResult.
        """
        pass

    @abstractmethod
    def delete_document(self, stored_path: str) -> bool:
        """
        Deletes the file at the specified storage path/key.
        """
        pass

    @abstractmethod
    def get_document(self, stored_path: str) -> bytes:
        """
        Retrieves the binary content from storage.
        """
        pass

class LocalDiskStorage(StorageInterface):
    """
    Local filesystem implementation of the StorageInterface (Ticket #4 stub, completes in Ticket #6).
    """
    def __init__(self, base_dir: str = "storage/uploads"):
        # Resolve path relative to backend root
        backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.base_dir = os.path.join(backend_root, base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def store_document(self, file_content: bytes, filename: str) -> StorageResult:
        try:
            # Generate unique storage UUID
            storage_id = str(uuid.uuid4())
            file_ext = os.path.splitext(filename)[1]
            stored_filename = f"{storage_id}{file_ext}"
            stored_path = os.path.join(self.base_dir, stored_filename)
            
            # Write to disk
            with open(stored_path, "wb") as f:
                f.write(file_content)
                
            # Calculate SHA-256 content checksum
            checksum = hashlib.sha256(file_content).hexdigest()
            
            return StorageResult(
                storage_id=storage_id,
                stored_path=stored_path,
                file_size=len(file_content),
                checksum=checksum,
                success=True
            )
        except Exception as e:
            return StorageResult(
                storage_id="",
                stored_path="",
                file_size=0,
                checksum="",
                success=False
            )

    def delete_document(self, stored_path: str) -> bool:
        try:
            if os.path.exists(stored_path):
                os.remove(stored_path)
                return True
            return False
        except Exception:
            return False

    def get_document(self, stored_path: str) -> bytes:
        if not os.path.exists(stored_path):
            raise FileNotFoundError("Storage resource not found.")
        with open(stored_path, "rb") as f:
            return f.read()
