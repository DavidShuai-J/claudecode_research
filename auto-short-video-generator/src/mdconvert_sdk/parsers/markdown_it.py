"""Markdown-it parser with common extensions."""

from __future__ import annotations

import importlib.util

from mdconvert_sdk.parsers.base import MarkdownParser


class MarkdownItParser(MarkdownParser):
    """Parser using markdown-it-py and common plugins."""

    name = "markdown-it"
    priority = 10

    def is_available(self) -> bool:
        return importlib.util.find_spec("markdown_it") is not None

    def to_html(self, markdown_text: str, options: object) -> str:
        from markdown_it import MarkdownIt
        from mdit_py_plugins.footnote import footnote_plugin
        from mdit_py_plugins.tasklists import tasklists_plugin
        from mdit_py_plugins.texmath import texmath_plugin
        from mdit_py_plugins.anchors import anchors_plugin

        flavor = getattr(options, "markdown_flavor", "commonmark")
        md = (
            MarkdownIt(flavor, {"html": True})
            .use(footnote_plugin)
            .use(tasklists_plugin)
            .use(texmath_plugin)
            .use(anchors_plugin)
        )
        return md.render(markdown_text)
