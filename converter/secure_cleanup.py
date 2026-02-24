import shutil
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def secure_temp_dir():
    """
    Context manager for secure file handling.
    Guarantees deletion of all files after use.
    """
    temp_dir = tempfile.mkdtemp(prefix="md2pdf_")
    try:
        yield Path(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        cleanup_old_temp_dirs()


def cleanup_old_temp_dirs(max_age_seconds: int = 300):
    """
    Removes orphaned temp directories older than max_age_seconds.
    Protection against file leaks on crashes.
    """
    temp_base = Path(tempfile.gettempdir())
    now = time.time()

    for path in temp_base.glob("md2pdf_*"):
        if path.is_dir() and (now - path.stat().st_mtime) > max_age_seconds:
            shutil.rmtree(path, ignore_errors=True)
