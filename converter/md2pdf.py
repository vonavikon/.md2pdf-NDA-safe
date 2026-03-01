from pathlib import Path

import markdown
from weasyprint import HTML, CSS

# CSS for better table rendering (like Cursor preview)
PDF_CSS = """
@page {
    size: A4;
    margin: 1.5cm;
}

body {
    font-family: 'DejaVu Sans', sans-serif;
    font-size: 10pt;
    line-height: 1.4;
    color: #333;
}

h1 { font-size: 18pt; margin-top: 0; }
h2 { font-size: 14pt; margin-top: 1em; }
h3 { font-size: 12pt; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 9pt;
    table-layout: auto;
}

th, td {
    border: 1px solid #ddd;
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

th {
    background-color: #f5f5f5;
    font-weight: bold;
}

tr:nth-child(even) {
    background-color: #fafafa;
}

code {
    background-color: #f4f4f4;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'DejaVu Sans Mono', monospace;
    font-size: 9pt;
}

pre {
    background-color: #f4f4f4;
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 9pt;
}

pre code {
    background: none;
    padding: 0;
}

blockquote {
    border-left: 3px solid #ddd;
    margin: 1em 0;
    padding-left: 1em;
    color: #666;
}

img {
    max-width: 100%;
    height: auto;
}
"""


def convert_md_to_pdf(
    input_path: Path,
    output_path: Path,
) -> None:
    """
    Convert Markdown file to PDF using markdown + weasyprint.
    This gives better table rendering than pandoc+latex.

    Args:
        input_path: Path to input .md file
        output_path: Path to output .pdf file

    Raises:
        ConversionError: If conversion fails
    """
    try:
        # Read markdown content
        content = input_path.read_text(encoding='utf-8')

        # Convert markdown to HTML
        html_content = markdown.markdown(
            content,
            extensions=[
                'tables',
                'fenced_code',
                'codehilite',
                'toc',
                'sane_lists',
            ]
        )

        # Wrap in basic HTML structure
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # Convert HTML to PDF with CSS
        HTML(string=full_html).write_pdf(
            output_path,
            stylesheets=[CSS(string=PDF_CSS)]
        )

    except Exception as error:
        error_name = error.__class__.__name__
        error_text = str(error) or "Unknown conversion failure"
        raise ConversionError(f"{error_name}: {error_text}") from error


class ConversionError(Exception):
    """Raised when markdown to pdf conversion fails."""
    pass
