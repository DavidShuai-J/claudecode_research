"""Python-Markdown parser fallback."""

from __future__ import annotations

import importlib.util

from mdconvert_sdk.parsers.base import MarkdownParser


class PythonMarkdownParser(MarkdownParser):
    """Parser using Python-Markdown with popular extensions."""

    name = "python-markdown"
    priority = 20

    def is_available(self) -> bool:
        return importlib.util.find_spec("markdown") is not None

    def to_html(self, markdown_text: str, options: object) -> str:
        from markdown import Markdown

        extensions = getattr(
            options,
            "markdown_extensions",
            [
                "extra",
                "admonition",
                "tables",
                "fenced_code",
                "footnotes",
                "attr_list",
                "md_in_html",
            ],
        )
        md = Markdown(
            extensions=extensions
        )
        return md.convert(markdown_text)
