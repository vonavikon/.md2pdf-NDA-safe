"""Tests for file validation and conversion pipeline."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from bot.file_pipeline import (
    validate_markdown_document,
    build_conversion_paths,
    convert_document_to_pdf,
)
from bot.errors import InvalidFileFormat, FileTooLarge


class TestValidateMarkdownDocument:
    """Tests for document validation."""

    def test_valid_markdown_file(self):
        """Valid .md file should pass validation."""
        doc = MagicMock()
        doc.file_name = "document.md"
        doc.file_size = 1024  # 1KB

        result = validate_markdown_document(doc, max_file_size_mb=10)
        assert result == "document.md"

    def test_valid_markdown_with_path(self):
        """Path components should be stripped from filename."""
        doc = MagicMock()
        doc.file_name = "../../../etc/passwd.md"
        doc.file_size = 1024

        result = validate_markdown_document(doc, max_file_size_mb=10)
        assert result == "passwd.md"

    def test_missing_extension_fails(self):
        """Files without .md extension should be rejected."""
        doc = MagicMock()
        doc.file_name = "document.txt"
        doc.file_size = 1024

        with pytest.raises(InvalidFileFormat):
            validate_markdown_document(doc, max_file_size_mb=10)

    def test_no_extension_fails(self):
        """Files without extension should be rejected."""
        doc = MagicMock()
        doc.file_name = "README"
        doc.file_size = 1024

        with pytest.raises(InvalidFileFormat):
            validate_markdown_document(doc, max_file_size_mb=10)

    def test_empty_filename_fails(self):
        """Empty filename should be rejected."""
        doc = MagicMock()
        doc.file_name = ""
        doc.file_size = 1024

        with pytest.raises(InvalidFileFormat):
            validate_markdown_document(doc, max_file_size_mb=10)

    def test_none_filename_fails(self):
        """None filename should be rejected."""
        doc = MagicMock()
        doc.file_name = None
        doc.file_size = 1024

        with pytest.raises(InvalidFileFormat):
            validate_markdown_document(doc, max_file_size_mb=10)

    def test_file_too_large_fails(self):
        """Files exceeding size limit should be rejected."""
        doc = MagicMock()
        doc.file_name = "large.md"
        doc.file_size = 20 * 1024 * 1024  # 20MB

        with pytest.raises(FileTooLarge):
            validate_markdown_document(doc, max_file_size_mb=10)

    def test_exact_size_limit_passes(self):
        """File at exact size limit should pass."""
        doc = MagicMock()
        doc.file_name = "exact.md"
        doc.file_size = 10 * 1024 * 1024  # Exactly 10MB

        result = validate_markdown_document(doc, max_file_size_mb=10)
        assert result == "exact.md"


class TestBuildConversionPaths:
    """Tests for path building and validation."""

    def test_normal_paths(self, tmp_path):
        """Normal filenames should produce valid paths."""
        input_path, output_path = build_conversion_paths(tmp_path, "document.md")

        assert input_path == tmp_path / "document.md"
        assert output_path == tmp_path / "document.pdf"
        assert input_path.parent == tmp_path
        assert output_path.parent == tmp_path

    def test_path_traversal_blocked(self, tmp_path):
        """Path traversal attempts should be blocked."""
        with pytest.raises(InvalidFileFormat):
            build_conversion_paths(tmp_path, "../outside.md")

    def test_absolute_path_blocked(self, tmp_path):
        """Absolute paths should be blocked."""
        with pytest.raises(InvalidFileFormat):
            build_conversion_paths(tmp_path, "/etc/passwd.md")

    def test_complex_traversal_blocked(self, tmp_path):
        """Complex path traversal should be blocked."""
        with pytest.raises(InvalidFileFormat):
            build_conversion_paths(tmp_path, "foo/../../bar.md")


class TestConvertDocumentToPdf:
    """Tests for PDF conversion."""

    @pytest.mark.asyncio
    async def test_conversion_success(self, tmp_path):
        """Successful conversion should create PDF."""
        # Create test markdown file
        input_file = tmp_path / "test.md"
        input_file.write_text("# Test\n\nHello **world**!")
        output_file = tmp_path / "test.pdf"

        await convert_document_to_pdf(input_file, output_file, timeout_seconds=30)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_conversion_with_tables(self, tmp_path):
        """Conversion should handle tables."""
        input_file = tmp_path / "tables.md"
        input_file.write_text("""
# Table Test

| Name | Value |
|------|-------|
| A    | 1     |
| B    | 2     |
""")
        output_file = tmp_path / "tables.pdf"

        await convert_document_to_pdf(input_file, output_file, timeout_seconds=30)

        assert output_file.exists()
