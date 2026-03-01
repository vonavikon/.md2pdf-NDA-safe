"""Pytest configuration and fixtures."""
import pytest


@pytest.fixture
def sample_markdown():
    """Sample markdown content for tests."""
    return """
# Test Document

This is a **test** document with *italic* text.

## Features

- List item 1
- List item 2

| Column A | Column B |
|----------|----------|
| Data 1   | Data 2   |

```python
print("Hello, World!")
```
"""
