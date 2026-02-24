import subprocess
from pathlib import Path

PANDOC_ARGS = [
    "--pdf-engine=xelatex",
    "--variable=mainfont:DejaVu Sans",
    "--variable=geometry:margin=2.5cm",
    "--highlight-style=tango",
    "--from=markdown+tex_math_dollars+raw_tex",
    "--standalone",
]


def convert_md_to_pdf(input_path: Path, output_path: Path) -> None:
    """
    Convert Markdown file to PDF using pandoc.

    Args:
        input_path: Path to input .md file
        output_path: Path to output .pdf file

    Raises:
        ConversionError: If pandoc fails
    """
    cmd = ["pandoc", str(input_path), "-o", str(output_path)] + PANDOC_ARGS

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise ConversionError(f"Pandoc error: {result.stderr}")


class ConversionError(Exception):
    """Raised when markdown to pdf conversion fails."""
    pass
