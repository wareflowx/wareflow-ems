"""Tests for the file_storage module.

Unit tests for DocumentStorageManager covering document storage,
retrieval, versioning, and metadata management.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from utils.file_storage import DocumentStorageManager


class TestDocumentStorageManager:
    """Test suite for DocumentStorageManager class."""

    @pytest.fixture
    def temp_base_dir(self, tmp_path):
        """Create a temporary base directory for testing."""
        base_dir = tmp_path / "documents"
        base_dir.mkdir()
        return base_dir

    @pytest.fixture
    def storage_manager(self, temp_base_dir):
        """Create a DocumentStorageManager instance with temporary directory."""
        return DocumentStorageManager(base_dir=temp_base_dir)

    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create a sample test file."""
        test_file = tmp_path / "test_document.pdf"
        test_file.write_text("Sample PDF content")
        return test_file

    # Test: Initialization

    def test_init_creates_base_directory(self, temp_base_dir):
        """Test that initialization creates base directory."""
        base_dir = temp_base_dir / "new_docs"
        manager = DocumentStorageManager(base_dir=base_dir)

        assert base_dir.exists()
        assert manager.base_dir == base_dir

    def test_init_creates_document_type_directories(self, storage_manager, temp_base_dir):
        """Test that initialization creates all document type subdirectories."""
        expected_dirs = ["caces", "medical", "training", "contracts"]

        for doc_type in expected_dirs:
            assert (temp_base_dir / doc_type).exists()
            assert (temp_base_dir / doc_type).is_dir()

    def test_init_with_existing_base_dir(self, storage_manager):
        """Test that initialization works with existing directory."""
        assert storage_manager.base_dir.exists()

    # Test: get_employee_folder

    def test_get_employee_folder_valid_type(self, storage_manager):
        """Test get_employee_folder with valid document type."""
        folder = storage_manager.get_employee_folder("caces", "MATR001")

        assert folder.name == "employee_MATR001"
        assert folder.parent.name == "caces"
        assert folder.exists()

    def test_get_employee_folder_invalid_type_raises_error(self, storage_manager):
        """Test get_employee_folder with invalid document type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid document type"):
            storage_manager.get_employee_folder("invalid_type", "MATR001")

    def test_get_employee_folder_creates_folder(self, storage_manager, temp_base_dir):
        """Test get_employee_folder creates employee folder if it doesn't exist."""
        matricule = "MATR999"
        folder = storage_manager.get_employee_folder("medical", matricule)

        assert folder.exists()
        assert folder.is_dir()

    # Test: store_document

    def test_store_document_copies_file(self, storage_manager, sample_file):
        """Test that store_document copies file to correct location."""
        dest_path = storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata={"file_name": "certificat.pdf"}
        )

        assert dest_path.exists()
        assert dest_path.parent.name == "employee_MATR001"
        assert dest_path.stat().st_size == sample_file.stat().st_size

    def test_store_document_creates_metadata_file(self, storage_manager, sample_file):
        """Test that store_document creates JSON metadata file."""
        dest_path = storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata={"file_name": "certificat.pdf", "caces_type": "1A"}
        )

        # Metadata file is named: v{version}_{date}_{filename}.json
        # So if dest_path is v1_2026-01-27_certificat.pdf, metadata is v1_2026-01-27_certificat.pdf.json
        metadata_path = Path(str(dest_path) + '.json')
        assert metadata_path.exists()

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        assert metadata["file_name"] == "certificat.pdf"
        assert metadata["caces_type"] == "1A"
        assert metadata["employee_matricule"] == "MATR001"
        assert metadata["document_type"] == "caces"

    def test_store_document_auto_increments_version(self, storage_manager, sample_file):
        """Test that store_document auto-increments version number."""
        metadata = {"file_name": "certificat.pdf"}

        # First version
        path1 = storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )
        assert "v1_" in path1.name

        # Second version
        path2 = storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )
        assert "v2_" in path2.name

    def test_store_document_explicit_version(self, storage_manager, sample_file):
        """Test store_document with explicit version number."""
        dest_path = storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata={"file_name": "certificat.pdf"},
            version=5
        )

        assert "v5_" in dest_path.name

    def test_store_document_nonexistent_file_raises_error(self, storage_manager):
        """Test store_document with non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            storage_manager.store_document(
                doc_type="caces",
                matricule="MATR001",
                file_path=Path("nonexistent.pdf"),
                metadata={"file_name": "test.pdf"}
            )

    def test_store_document_adds_hash(self, storage_manager, sample_file):
        """Test that store_document calculates and stores file hash."""
        storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata={"file_name": "certificat.pdf"}
        )

        metadata_file = list((storage_manager.base_dir / "caces" / "employee_MATR001").glob("*.json"))[0]
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        assert "hash" in metadata
        assert metadata["hash"].startswith("sha256:")

    def test_store_document_adds_mime_type(self, storage_manager, sample_file):
        """Test that store_document detects and stores MIME type."""
        storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata={"file_name": "certificat.pdf"}
        )

        metadata_file = list((storage_manager.base_dir / "caces" / "employee_MATR001").glob("*.json"))[0]
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        assert "mime_type" in metadata

    def test_store_document_enhances_metadata(self, storage_manager, sample_file):
        """Test that store_document enhances metadata with system fields."""
        storage_manager.store_document(
            doc_type="training",
            matricule="MATR002",
            file_path=sample_file,
            metadata={"file_name": "certificate.pdf", "training_title": "Safety"}
        )

        metadata_file = list((storage_manager.base_dir / "training" / "employee_MATR002").glob("*.json"))[0]
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        # Check system fields
        assert "document_id" in metadata
        assert "upload_date" in metadata
        assert "file_size_bytes" in metadata
        assert "file_path" in metadata
        assert "version" in metadata

        # Check user metadata preserved
        assert metadata["training_title"] == "Safety"

    # Test: get_document_history

    def test_get_document_history_empty(self, storage_manager):
        """Test get_document_history returns empty list for non-existent document."""
        history = storage_manager.get_document_history("caces", "MATR001", "certificat.pdf")
        assert history == []

    def test_get_document_history_returns_all_versions(self, storage_manager, sample_file):
        """Test get_document_history returns all versions sorted."""
        metadata = {"file_name": "certificat.pdf"}

        # Store 3 versions
        for _ in range(3):
            storage_manager.store_document(
                doc_type="medical",
                matricule="MATR001",
                file_path=sample_file,
                metadata=metadata
            )

        history = storage_manager.get_document_history("medical", "MATR001", "certificat.pdf")

        assert len(history) == 3
        assert history[0]["version"] == 1
        assert history[1]["version"] == 2
        assert history[2]["version"] == 3

    def test_get_document_history_filters_by_filename(self, storage_manager, sample_file):
        """Test get_document_history filters by correct file name."""
        metadata1 = {"file_name": "doc1.pdf"}
        metadata2 = {"file_name": "doc2.pdf"}

        storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata1
        )
        storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata2
        )

        history = storage_manager.get_document_history("caces", "MATR001", "doc1.pdf")

        assert len(history) == 1
        assert history[0]["file_name"] == "doc1.pdf"

    # Test: get_latest_version

    def test_get_latest_version_returns_none_for_nonexistent(self, storage_manager):
        """Test get_latest_version returns None for non-existent document."""
        latest = storage_manager.get_latest_version("caces", "MATR001", "certificat.pdf")
        assert latest is None

    def test_get_latest_version_returns_newest(self, storage_manager, sample_file):
        """Test get_latest_version returns the most recent version."""
        metadata = {"file_name": "certificat.pdf"}

        # Store 3 versions
        storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )
        storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )
        latest_path = storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )

        latest = storage_manager.get_latest_version("caces", "MATR001", "certificat.pdf")

        assert latest is not None
        assert latest["version"] == 3
        assert str(latest["file_path"]) == str(latest_path)

    # Test: get_document_path

    def test_get_document_path_latest(self, storage_manager, sample_file):
        """Test get_document_path returns path to latest version."""
        stored_path = storage_manager.store_document(
            doc_type="medical",
            matricule="MATR001",
            file_path=sample_file,
            metadata={"file_name": "visite.pdf"}
        )

        retrieved_path = storage_manager.get_document_path("medical", "MATR001", "visite.pdf")

        assert retrieved_path == stored_path

    def test_get_document_path_specific_version(self, storage_manager, sample_file):
        """Test get_document_path returns path to specific version."""
        metadata = {"file_name": "doc.pdf"}

        storage_manager.store_document(
            doc_type="training",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )
        v2_path = storage_manager.store_document(
            doc_type="training",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )

        retrieved_path = storage_manager.get_document_path("training", "MATR001", "doc.pdf", version=2)

        assert retrieved_path == v2_path

    def test_get_document_path_nonexistent_returns_none(self, storage_manager):
        """Test get_document_path returns None for non-existent document."""
        path = storage_manager.get_document_path("caces", "MATR999", "nonexistent.pdf")
        assert path is None

    # Test: delete_document

    def test_delete_document_specific_version(self, storage_manager, sample_file):
        """Test delete_document deletes specific version."""
        metadata = {"file_name": "doc.pdf"}

        storage_manager.store_document(
            doc_type="contracts",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )
        v2_path = storage_manager.store_document(
            doc_type="contracts",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )

        # Delete version 2
        result = storage_manager.delete_document("contracts", "MATR001", "doc.pdf", version=2)

        assert result is True
        assert not v2_path.exists()

        # Version 1 should still exist
        history = storage_manager.get_document_history("contracts", "MATR001", "doc.pdf")
        assert len(history) == 1
        assert history[0]["version"] == 1

    def test_delete_document_all_versions(self, storage_manager, sample_file):
        """Test delete_document deletes all versions when version is None."""
        metadata = {"file_name": "doc.pdf"}

        storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )
        storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )

        # Delete all versions
        result = storage_manager.delete_document("caces", "MATR001", "doc.pdf")

        assert result is True
        history = storage_manager.get_document_history("caces", "MATR001", "doc.pdf")
        assert len(history) == 0

    def test_delete_document_nonexistent_returns_false(self, storage_manager):
        """Test delete_document returns False for non-existent document."""
        result = storage_manager.delete_document("caces", "MATR999", "nonexistent.pdf")
        assert result is False

    # Test: list_employee_documents

    def test_list_employee_documents_empty(self, storage_manager):
        """Test list_employee_documents returns empty list for employee with no documents."""
        docs = storage_manager.list_employee_documents("caces", "MATR999")
        assert docs == []

    def test_list_employee_documents_returns_latest_only(self, storage_manager, sample_file):
        """Test list_employee_documents returns only latest version of each document."""
        metadata = {"file_name": "doc.pdf"}

        # Store 3 versions of same document
        storage_manager.store_document(
            doc_type="medical",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )
        storage_manager.store_document(
            doc_type="medical",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )
        storage_manager.store_document(
            doc_type="medical",
            matricule="MATR001",
            file_path=sample_file,
            metadata=metadata
        )

        docs = storage_manager.list_employee_documents("medical", "MATR001")

        # Should only return latest version
        assert len(docs) == 1
        assert docs[0]["version"] == 3

    def test_list_employee_documents_multiple_files(self, storage_manager, sample_file):
        """Test list_employee_documents handles multiple different documents."""
        storage_manager.store_document(
            doc_type="training",
            matricule="MATR001",
            file_path=sample_file,
            metadata={"file_name": "course1.pdf"}
        )
        storage_manager.store_document(
            doc_type="training",
            matricule="MATR001",
            file_path=sample_file,
            metadata={"file_name": "course2.pdf"}
        )

        docs = storage_manager.list_employee_documents("training", "MATR001")

        assert len(docs) == 2
        file_names = [doc["file_name"] for doc in docs]
        assert "course1.pdf" in file_names
        assert "course2.pdf" in file_names

    # Test: get_storage_stats

    def test_get_storage_stats_empty(self, storage_manager):
        """Test get_storage_stats returns zeros for empty storage."""
        stats = storage_manager.get_storage_stats()

        assert stats["total_documents"] == 0
        assert stats["total_size_bytes"] == 0
        assert stats["documents_by_type"]["caces"] == 0
        assert stats["documents_by_type"]["medical"] == 0
        assert stats["documents_by_type"]["training"] == 0
        assert stats["documents_by_type"]["contracts"] == 0

    def test_get_storage_stats_counts_documents(self, storage_manager, sample_file):
        """Test get_storage_stats correctly counts documents."""
        storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata={"file_name": "caces.pdf"}
        )
        storage_manager.store_document(
            doc_type="medical",
            matricule="MATR001",
            file_path=sample_file,
            metadata={"file_name": "medical.pdf"}
        )

        stats = storage_manager.get_storage_stats()

        assert stats["total_documents"] == 2
        assert stats["documents_by_type"]["caces"] == 1
        assert stats["documents_by_type"]["medical"] == 1

    def test_get_storage_stats_includes_file_size(self, storage_manager, sample_file):
        """Test get_storage_stats includes total file size."""
        storage_manager.store_document(
            doc_type="caces",
            matricule="MATR001",
            file_path=sample_file,
            metadata={"file_name": "doc.pdf"}
        )

        stats = storage_manager.get_storage_stats()

        assert stats["total_size_bytes"] > 0

    # Test: _get_mime_type

    def test_get_mime_type_pdf(self, storage_manager, tmp_path):
        """Test MIME type detection for PDF files."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("content")

        assert storage_manager._get_mime_type(pdf_file) == "application/pdf"

    def test_get_mime_type_jpg(self, storage_manager, tmp_path):
        """Test MIME type detection for JPEG files."""
        jpg_file = tmp_path / "test.jpg"
        jpg_file.write_text("content")

        assert storage_manager._get_mime_type(jpg_file) == "image/jpeg"

    def test_get_mime_type_png(self, storage_manager, tmp_path):
        """Test MIME type detection for PNG files."""
        png_file = tmp_path / "test.png"
        png_file.write_text("content")

        assert storage_manager._get_mime_type(png_file) == "image/png"

    def test_get_mime_type_docx(self, storage_manager, tmp_path):
        """Test MIME type detection for DOCX files."""
        docx_file = tmp_path / "test.docx"
        docx_file.write_text("content")

        expected = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert storage_manager._get_mime_type(docx_file) == expected

    def test_get_mime_type_unknown(self, storage_manager, tmp_path):
        """Test MIME type detection for unknown file types."""
        unknown_file = tmp_path / "test.unknown"
        unknown_file.write_text("content")

        assert storage_manager._get_mime_type(unknown_file) == "application/octet-stream"
