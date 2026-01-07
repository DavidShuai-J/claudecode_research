"""Parser abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod


class MarkdownParser(ABC):
    """Base parser for Markdown input."""

    name: str = "base"
    priority: int = 100

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the parser can be used."""

    @abstractmethod
    def to_html(self, markdown_text: str, options: object) -> str:
        """Convert Markdown text to HTML."""
