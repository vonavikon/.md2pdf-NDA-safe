import base64
from pathlib import Path

import markdown
from weasyprint import HTML, CSS

# NAUMEN Brand Colors
POWER_ORANGE = "#ff6611"
COOL_GRAY = "#545658"
LIGHT_GRAY = "#f5f5f5"
BORDER_GRAY = "#e0e0e0"

# Path to logo
LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.png"


def _get_logo_base64() -> str:
    """Read logo file and return base64 encoded string."""
    if LOGO_PATH.exists():
        logo_bytes = LOGO_PATH.read_bytes()
        return base64.b64encode(logo_bytes).decode('utf-8')
    return ""


# NAUMEN Brand CSS for PDF
def get_pdf_css(with_logo: bool = True) -> str:
    """Generate PDF CSS with optional logo in header."""

    return f"""
@page {{
    size: A4;
    margin: 2cm 1.5cm;
    @top-right {{
        content: element(header-logo);
    }}
}}

/* Running header logo */
.header-logo {{
    position: running(header-logo);
}}

.header-logo img {{
    height: 32px;
    width: auto;
}}

body {{
    font-family: 'DejaVu Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: {COOL_GRAY};
}}

/* NAUMEN Headers with Power Orange */
h1 {{
    font-size: 22pt;
    margin-top: 0;
    color: {POWER_ORANGE};
    border-bottom: 2px solid {POWER_ORANGE};
    padding-bottom: 0.3em;
}}

h2 {{
    font-size: 16pt;
    margin-top: 1.2em;
    color: {POWER_ORANGE};
}}

h3 {{
    font-size: 13pt;
    color: {COOL_GRAY};
    font-weight: bold;
}}

h4, h5, h6 {{
    color: {COOL_GRAY};
}}

/* Links in brand color */
a {{
    color: {POWER_ORANGE};
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

/* Tables with brand styling */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 9pt;
    table-layout: auto;
}}

th, td {{
    border: 1px solid {BORDER_GRAY};
    padding: 8px 10px;
    text-align: left;
    vertical-align: top;
    word-wrap: break-word;
    overflow-wrap: break-word;
}}

th {{
    background-color: {POWER_ORANGE};
    color: white;
    font-weight: bold;
}}

tr:nth-child(even) {{
    background-color: {LIGHT_GRAY};
}}

/* Code blocks */
code {{
    background-color: {LIGHT_GRAY};
    padding: 2px 5px;
    border-radius: 3px;
    font-family: 'DejaVu Sans Mono', monospace;
    font-size: 9pt;
    color: {COOL_GRAY};
}}

pre {{
    background-color: #2d2d2d;
    padding: 14px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 9pt;
    border-left: 3px solid {POWER_ORANGE};
}}

pre code {{
    background: none;
    padding: 0;
    color: #f8f8f2;
}}

/* Blockquotes */
blockquote {{
    border-left: 3px solid {POWER_ORANGE};
    margin: 1em 0;
    padding: 0.5em 1em;
    background-color: {LIGHT_GRAY};
    color: {COOL_GRAY};
}}

/* Lists */
ul, ol {{
    padding-left: 1.5em;
}}

li {{
    margin-bottom: 0.3em;
}}

/* Horizontal rule */
hr {{
    border: none;
    border-top: 1px solid {BORDER_GRAY};
    margin: 1.5em 0;
}}

/* Images */
img {{
    max-width: 100%;
    height: auto;
}}
"""


# Legacy alias
PDF_CSS = get_pdf_css()


def convert_md_to_pdf(
    input_path: Path,
    output_path: Path,
    include_logo: bool = True,
) -> None:
    """
    Convert Markdown file to PDF using markdown + weasyprint.
    Uses NAUMEN brand styling with Power Orange headers and logo in footer.

    Args:
        input_path: Path to input .md file
        output_path: Path to output .pdf file
        include_logo: Whether to include brand logo in footer

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

        # Build header logo HTML (running element for @top-right)
        header_html = ""
        if include_logo:
            logo_b64 = _get_logo_base64()
            if logo_b64:
                header_html = f'''
        <div class="header-logo">
            <img src="data:image/png;base64,{logo_b64}" alt="NAUMEN">
        </div>'''

        # Wrap in HTML structure with header
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body>
            {header_html}
            <div class="content">
                {html_content}
            </div>
        </body>
        </html>
        """

        # Convert HTML to PDF with NAUMEN brand CSS
        HTML(string=full_html).write_pdf(
            output_path,
            stylesheets=[CSS(string=get_pdf_css())]
        )

    except Exception as error:
        error_name = error.__class__.__name__
        error_text = str(error) or "Unknown conversion failure"
        raise ConversionError(f"{error_name}: {error_text}") from error


class ConversionError(Exception):
    """Raised when markdown to pdf conversion fails."""
    pass
