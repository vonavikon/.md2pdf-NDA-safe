"""Tests for Markdown to PDF converter."""
import pytest
from pathlib import Path

from converter.md2pdf import (
    convert_md_to_pdf,
    get_pdf_css,
    _get_logo_base64,
    ConversionError,
    POWER_ORANGE,
    COOL_GRAY,
)


class TestGetPdfCss:
    """Tests for CSS generation."""

    def test_css_contains_brand_colors(self):
        """CSS should contain NAUMEN brand colors."""
        css = get_pdf_css()

        assert POWER_ORANGE in css  # #ff6611
        assert COOL_GRAY in css  # #545658

    def test_css_contains_typography(self):
        """CSS should contain typography rules."""
        css = get_pdf_css()

        assert "font-family" in css
        assert "h1" in css
        assert "h2" in css
        assert "table" in css

    def test_css_contains_table_styling(self):
        """CSS should contain table styling."""
        css = get_pdf_css()

        assert "border-collapse" in css
        assert "th" in css


class TestGetLogoBase64:
    """Tests for logo loading."""

    def test_returns_string_when_logo_exists(self):
        """Should return base64 string when logo file exists."""
        result = _get_logo_base64()
        # Logo should exist in assets folder
        assert isinstance(result, str)
        # Base64 of PNG should be substantial
        if result:  # Only if logo exists
            assert len(result) > 1000


class TestConvertMdToPdf:
    """Tests for PDF conversion."""

    def test_simple_markdown(self, tmp_path):
        """Simple markdown should convert successfully."""
        input_file = tmp_path / "test.md"
        input_file.write_text("# Hello\n\nWorld!")
        output_file = tmp_path / "test.pdf"

        convert_md_to_pdf(input_file, output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_complex_markdown(self, tmp_path):
        """Complex markdown with tables, code, lists should work."""
        input_file = tmp_path / "complex.md"
        input_file.write_text("""
# Complex Document

## Tables

| A | B | C |
|---|---|---|
| 1 | 2 | 3 |

## Code

```python
def hello():
    print("Hello")
```

## Lists

- Item 1
- Item 2

1. First
2. Second

## Blockquote

> This is a quote
""")
        output_file = tmp_path / "complex.pdf"

        convert_md_to_pdf(input_file, output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 1000  # Should be substantial

    def test_cyrillic_support(self, tmp_path):
        """Cyrillic text should render correctly."""
        input_file = tmp_path / "cyrillic.md"
        input_file.write_text("# Заголовок\n\nТекст на русском языке.")
        output_file = tmp_path / "cyrillic.pdf"

        convert_md_to_pdf(input_file, output_file)

        assert output_file.exists()

    def test_invalid_input_raises_error(self, tmp_path):
        """Non-existent file should raise ConversionError."""
        input_file = tmp_path / "nonexistent.md"
        output_file = tmp_path / "output.pdf"

        with pytest.raises(ConversionError):
            convert_md_to_pdf(input_file, output_file)

    def test_with_logo(self, tmp_path):
        """Conversion with logo should work."""
        input_file = tmp_path / "with_logo.md"
        input_file.write_text("# Document\n\nWith logo.")
        output_file = tmp_path / "with_logo.pdf"

        convert_md_to_pdf(input_file, output_file, include_logo=True)

        assert output_file.exists()

    def test_without_logo(self, tmp_path):
        """Conversion without logo should work."""
        input_file = tmp_path / "no_logo.md"
        input_file.write_text("# Document\n\nNo logo.")
        output_file = tmp_path / "no_logo.pdf"

        convert_md_to_pdf(input_file, output_file, include_logo=False)

        assert output_file.exists()
