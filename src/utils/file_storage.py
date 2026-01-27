"""Hierarchical document storage management system.

This module provides a structured storage system for employee documents
with version tracking, metadata management, and audit trails.
"""

import hashlib
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class DocumentStorageManager:
    """
    Manages hierarchical document storage with versioning.

    Provides organized storage structure:
    documents/
    ├── caces/
    │   ├── employee_MATR001/
    │   │   ├── v1_2024-01-15_caces_1a_certificat.pdf
    │   │   ├── v1_2024-01-15_caces_1a_certificat.json
    │   │   └── v2_2024-06-20_caces_1a_certificat.pdf
    │   └── ...
    ├── medical/
    │   └── ...
    ├── training/
    │   └── ...
    └── contracts/
        └── ...
    """

    def __init__(self, base_dir: Path = Path("documents")):
        """
        Initialize the storage manager.

        Args:
            base_dir: Base directory for document storage (default: documents/)
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

        # Create document type directories
        self._document_types = ["caces", "medical", "training", "contracts"]
        for doc_type in self._document_types:
            (self.base_dir / doc_type).mkdir(exist_ok=True)

    def get_employee_folder(self, doc_type: str, matricule: str) -> Path:
        """
        Get the folder path for an employee's documents.

        Args:
            doc_type: Document type (caces, medical, training, contracts)
            matricule: Employee matricule

        Returns:
            Path to employee's document folder

        Raises:
            ValueError: If doc_type is invalid
        """
        if doc_type not in self._document_types:
            raise ValueError(f"Invalid document type: {doc_type}. Must be one of {self._document_types}")

        folder = self.base_dir / doc_type / f"employee_{matricule}"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def store_document(
        self,
        doc_type: str,
        matricule: str,
        file_path: Path,
        metadata: Dict[str, Any],
        version: Optional[int] = None
    ) -> Path:
        """
        Store a document in the hierarchical structure.

        Args:
            doc_type: Document type (caces, medical, training, contracts)
            matricule: Employee matricule
            file_path: Path to source file
            metadata: Document metadata (will be enhanced with system fields)
            version: Document version (None = auto-increment)

        Returns:
            Path to stored document

        Raises:
            FileNotFoundError: If source file doesn't exist
            ValueError: If doc_type is invalid
        """
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        # Get employee folder
        folder = self.get_employee_folder(doc_type, matricule)

        # Auto-detect next version if not specified
        if version is None:
            version = self._get_next_version(doc_type, matricule, metadata.get("file_name", source_path.name))

        # Generate filename with date and version
        upload_date = datetime.now()
        date_str = upload_date.strftime("%Y-%m-%d")
        file_name = metadata.get("file_name", source_path.name)
        new_filename = f"v{version}_{date_str}_{file_name}"
        dest_path = folder / new_filename

        # Copy file
        shutil.copy2(source_path, dest_path)

        # Calculate file hash
        with open(dest_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # Enhance metadata with system fields
        enhanced_metadata = {
            "document_id": str(uuid.uuid4()),
            "employee_matricule": matricule,
            "document_type": doc_type,
            "file_name": file_name,
            "upload_date": upload_date.isoformat(),
            "version": version,
            "hash": f"sha256:{file_hash}",
            "file_size_bytes": dest_path.stat().st_size,
            "file_path": str(dest_path),
            **metadata
        }

        # Add MIME type if not present
        if "mime_type" not in enhanced_metadata:
            enhanced_metadata["mime_type"] = self._get_mime_type(dest_path)

        # Save metadata file
        metadata_path = folder / f"v{version}_{date_str}_{file_name}.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(enhanced_metadata, f, indent=2, default=str)

        return dest_path

    def get_document_history(
        self,
        doc_type: str,
        matricule: str,
        file_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get all versions of a document.

        Args:
            doc_type: Document type
            matricule: Employee matricule
            file_name: Base document name (without version prefix)

        Returns:
            List of metadata dicts for each version, sorted by version number

        Raises:
            ValueError: If doc_type is invalid
        """
        folder = self.get_employee_folder(doc_type, matricule)
        versions = []

        # Find all metadata files for this document
        pattern = f"*_*_{file_name}.json"
        for metadata_file in folder.glob(pattern):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    versions.append(metadata)
            except (json.JSONDecodeError, IOError):
                # Skip corrupt metadata files
                continue

        # Sort by version number
        versions.sort(key=lambda x: x.get("version", 0))
        return versions

    def get_latest_version(
        self,
        doc_type: str,
        matricule: str,
        file_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest version of a document.

        Args:
            doc_type: Document type
            matricule: Employee matricule
            file_name: Base document name

        Returns:
            Metadata dict for latest version, or None if not found
        """
        history = self.get_document_history(doc_type, matricule, file_name)
        return history[-1] if history else None

    def get_document_path(
        self,
        doc_type: str,
        matricule: str,
        file_name: str,
        version: Optional[int] = None
    ) -> Optional[Path]:
        """
        Get the file path for a specific document version.

        Args:
            doc_type: Document type
            matricule: Employee matricule
            file_name: Base document name
            version: Specific version (None = latest)

        Returns:
            Path to document file, or None if not found
        """
        if version is None:
            metadata = self.get_latest_version(doc_type, matricule, file_name)
        else:
            folder = self.get_employee_folder(doc_type, matricule)
            pattern = f"v{version}_*_{file_name}.json"
            metadata_files = list(folder.glob(pattern))
            if not metadata_files:
                return None
            with open(metadata_files[0], "r", encoding="utf-8") as f:
                metadata = json.load(f)

        if metadata and "file_path" in metadata:
            return Path(metadata["file_path"])
        return None

    def delete_document(
        self,
        doc_type: str,
        matricule: str,
        file_name: str,
        version: Optional[int] = None
    ) -> bool:
        """
        Delete a document (and its metadata).

        Args:
            doc_type: Document type
            matricule: Employee matricule
            file_name: Document file name
            version: Specific version to delete (None = all versions)

        Returns:
            True if deleted successfully, False otherwise
        """
        folder = self.get_employee_folder(doc_type, matricule)

        try:
            if version:
                # Delete specific version
                pattern = f"v{version}_*_{file_name}*"
                files = list(folder.glob(pattern))
                if not files:
                    return False
                for file in files:
                    file.unlink()
            else:
                # Delete all versions
                pattern = f"*_*_{file_name}*"
                files = list(folder.glob(pattern))
                if not files:
                    return False
                for file in files:
                    file.unlink()

            return True
        except (OSError, FileNotFoundError):
            return False

    def list_employee_documents(
        self,
        doc_type: str,
        matricule: str
    ) -> List[Dict[str, Any]]:
        """
        List all documents for an employee.

        Args:
            doc_type: Document type
            matricule: Employee matricule

        Returns:
            List of metadata dicts for all documents (latest version only)
        """
        folder = self.get_employee_folder(doc_type, matricule)
        documents = {}

        # Find all metadata files
        for metadata_file in folder.glob("*.json"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    file_name = metadata.get("file_name")
                    version = metadata.get("version", 0)

                    # Keep only the latest version of each file
                    if file_name and file_name not in documents:
                        documents[file_name] = metadata
                    elif file_name and version > documents[file_name].get("version", 0):
                        documents[file_name] = metadata
            except (json.JSONDecodeError, IOError):
                continue

        return list(documents.values())

    def _get_next_version(self, doc_type: str, matricule: str, file_name: str) -> int:
        """Get the next version number for a document."""
        history = self.get_document_history(doc_type, matricule, file_name)
        if not history:
            return 1
        return max(v.get("version", 0) for v in history) + 1

    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for a file."""
        # Simple MIME type detection
        suffix = file_path.suffix.lower()
        mime_types = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        return mime_types.get(suffix, "application/octet-stream")

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about document storage.

        Returns:
            Dictionary with storage statistics:
            - total_documents: Total number of documents
            - total_size_bytes: Total size in bytes
            - documents_by_type: Count per document type
            - documents_by_employee: Count per employee
        """
        stats = {
            "total_documents": 0,
            "total_size_bytes": 0,
            "documents_by_type": {},
            "documents_by_employee": {},
        }

        for doc_type in self._document_types:
            type_dir = self.base_dir / doc_type
            if not type_dir.exists():
                continue

            doc_count = 0
            for employee_folder in type_dir.iterdir():
                if not employee_folder.is_dir():
                    continue

                matricule = employee_folder.name.replace("employee_", "")
                employee_docs = list(employee_folder.glob("*.pdf")) + list(employee_folder.glob("*.jpg"))
                employee_doc_count = len(employee_docs)

                doc_count += employee_doc_count
                stats["documents_by_employee"][matricule] = employee_doc_count

                # Calculate total size
                for doc in employee_docs:
                    stats["total_size_bytes"] += doc.stat().st_size

            stats["documents_by_type"][doc_type] = doc_count
            stats["total_documents"] += doc_count

        return stats
