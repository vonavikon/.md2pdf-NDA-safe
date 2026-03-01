"""Tests for secure temporary directory cleanup."""
import os
import time
import pytest
from pathlib import Path

from converter.secure_cleanup import secure_temp_dir, cleanup_old_temp_dirs


class TestSecureTempDir:
    """Tests for secure temporary directory context manager."""

    def test_directory_created(self):
        """Context manager should create a temporary directory."""
        with secure_temp_dir() as temp_dir:
            assert temp_dir.exists()
            assert temp_dir.is_dir()
            assert "md2pdf_" in temp_dir.name

    def test_directory_deleted_after_context(self):
        """Directory should be deleted after context exits."""
        with secure_temp_dir() as temp_dir:
            temp_path = str(temp_dir)
            assert Path(temp_path).exists()

        # Directory should be gone
        assert not Path(temp_path).exists()

    def test_files_inside_deleted(self):
        """Files created inside temp dir should be deleted."""
        with secure_temp_dir() as temp_dir:
            test_file = temp_dir / "test.txt"
            test_file.write_text("secret data")
            assert test_file.exists()

        # Both file and directory should be gone
        assert not test_file.exists()
        assert not temp_dir.exists()

    def test_cleanup_on_exception(self):
        """Directory should be cleaned up even if exception occurs."""
        temp_path = None
        with pytest.raises(ValueError):
            with secure_temp_dir() as temp_dir:
                temp_path = str(temp_dir)
                raise ValueError("Test exception")

        # Directory should still be cleaned up
        assert temp_path is not None
        assert not Path(temp_path).exists()

    def test_nested_directories_deleted(self):
        """Nested directories should be deleted."""
        with secure_temp_dir() as temp_dir:
            nested = temp_dir / "a" / "b" / "c"
            nested.mkdir(parents=True)
            (nested / "deep.txt").write_text("nested file")

        assert not temp_dir.exists()


class TestCleanupOldTempDirs:
    """Tests for orphaned directory cleanup."""

    def test_removes_old_dirs(self, tmp_path, monkeypatch):
        """Should remove directories older than max age."""
        # Create a fake old temp dir
        old_dir = tmp_path / "md2pdf_old_123"
        old_dir.mkdir()
        old_file = old_dir / "data.txt"
        old_file.write_text("old data")

        # Set modification time to 10 minutes ago
        old_time = time.time() - 600
        os.utime(old_dir, (old_time, old_time))

        # Monkeypatch tempfile to use our temp path
        import tempfile
        monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))

        cleanup_old_temp_dirs(max_age_seconds=300)

        assert not old_dir.exists()

    def test_keeps_recent_dirs(self, tmp_path, monkeypatch):
        """Should not remove recent directories."""
        recent_dir = tmp_path / "md2pdf_recent_456"
        recent_dir.mkdir()
        recent_file = recent_dir / "data.txt"
        recent_file.write_text("recent data")

        import tempfile
        monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))

        cleanup_old_temp_dirs(max_age_seconds=300)

        assert recent_dir.exists()
        assert recent_file.exists()

    def test_ignores_non_md2pdf_dirs(self, tmp_path, monkeypatch):
        """Should only remove md2pdf_* directories."""
        other_dir = tmp_path / "other_prefix_789"
        other_dir.mkdir()
        (other_dir / "data.txt").write_text("other data")

        # Make it old
        old_time = time.time() - 600
        os.utime(other_dir, (old_time, old_time))

        import tempfile
        monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))

        cleanup_old_temp_dirs(max_age_seconds=300)

        # Should still exist
        assert other_dir.exists()
