"""High-level client API for converting Markdown/HTML to PDF/DOCX/PPTX."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from mdconvert_sdk.engines.base import BaseEngine, EngineRegistry
from mdconvert_sdk.engines.pandoc import PandocEngine
from mdconvert_sdk.engines.weasyprint import WeasyPrintEngine
from mdconvert_sdk.parsers.base import MarkdownParser
from mdconvert_sdk.parsers.markdown_it import MarkdownItParser
from mdconvert_sdk.parsers.python_markdown import PythonMarkdownParser
from mdconvert_sdk.pipeline.renderer import RenderPipeline


@dataclass(slots=True)
class ConversionOptions:
    """Configuration shared across engines and renderers."""

    markdown_flavor: str = "commonmark"
    markdown_extensions: list[str] | None = None
    theme_css: str | None = None
    html_template: str | None = None
    docx_template: str | None = None
    pptx_template: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    extra_args: list[str] = field(default_factory=list)
    keep_intermediate: bool = False


class ConverterClient:
    """SDK entry point for document conversion."""

    def __init__(
        self,
        engines: Iterable[BaseEngine] | None = None,
        parsers: Iterable[MarkdownParser] | None = None,
    ) -> None:
        self.registry = EngineRegistry()
        for engine in engines or self._default_engines():
            self.registry.register(engine)
        self.parsers = list(parsers or self._default_parsers())
        self.pipeline = RenderPipeline(parsers=self.parsers, registry=self.registry)

    @staticmethod
    def _default_engines() -> list[BaseEngine]:
        return [PandocEngine(), WeasyPrintEngine()]

    @staticmethod
    def _default_parsers() -> list[MarkdownParser]:
        return [MarkdownItParser(), PythonMarkdownParser()]

    def convert_markdown(
        self,
        markdown_text: str,
        to: str,
        output_path: str | Path,
        options: ConversionOptions | None = None,
        input_format: str = "markdown",
    ) -> Path:
        """Convert Markdown string to target format."""

        output_path = Path(output_path)
        options = options or ConversionOptions()
        return self.pipeline.convert_text(
            markdown_text,
            input_format=input_format,
            output_format=to,
            output_path=output_path,
            options=options,
        )

    def convert_file(
        self,
        input_path: str | Path,
        to: str,
        output_path: str | Path,
        options: ConversionOptions | None = None,
    ) -> Path:
        """Convert file (Markdown or HTML) to target format."""

        input_path = Path(input_path)
        output_path = Path(output_path)
        options = options or ConversionOptions()
        return self.pipeline.convert_file(
            input_path,
            output_format=to,
            output_path=output_path,
            options=options,
        )


def convert_markdown(
    markdown_text: str,
    to: str,
    output_path: str | Path,
    options: ConversionOptions | None = None,
) -> Path:
    """Convenience function to convert Markdown text."""

    client = ConverterClient()
    return client.convert_markdown(markdown_text, to=to, output_path=output_path, options=options)


def convert_file(
    input_path: str | Path,
    to: str,
    output_path: str | Path,
    options: ConversionOptions | None = None,
) -> Path:
    """Convenience function to convert a file."""

    client = ConverterClient()
    return client.convert_file(input_path, to=to, output_path=output_path, options=options)
