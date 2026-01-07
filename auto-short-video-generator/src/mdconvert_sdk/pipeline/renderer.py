"""Render pipeline for converting Markdown/HTML via engines."""

from __future__ import annotations

from pathlib import Path
import tempfile

from mdconvert_sdk.engines.base import EngineRegistry
from mdconvert_sdk.parsers.base import MarkdownParser


class RenderPipeline:
    """Coordinates parsing and engine selection."""

    def __init__(self, parsers: list[MarkdownParser], registry: EngineRegistry) -> None:
        self.parsers = sorted(parsers, key=lambda parser: parser.priority)
        self.registry = registry

    def convert_text(
        self,
        text: str,
        input_format: str,
        output_format: str,
        output_path: Path,
        options: object,
    ) -> Path:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            if input_format == "markdown":
                html_text = self._markdown_to_html(text, options=options)
                html_text = self._wrap_html(html_text, options=options)
                temp_path = temp_dir_path / "input.html"
                temp_path.write_text(html_text, encoding="utf-8")
                self._convert_file(
                    input_path=temp_path,
                    input_format="html",
                    output_format=output_format,
                    output_path=output_path,
                    options=options,
                )
            else:
                temp_path = temp_dir_path / f"input.{input_format}"
                temp_path.write_text(text, encoding="utf-8")
                self._convert_file(
                    input_path=temp_path,
                    input_format=input_format,
                    output_format=output_format,
                    output_path=output_path,
                    options=options,
                )
            self._persist_intermediate(temp_dir_path, output_path, options)
        return output_path

    def convert_file(
        self,
        input_path: Path,
        output_format: str,
        output_path: Path,
        options: object,
    ) -> Path:
        input_format = self._infer_format(input_path)
        if input_format == "markdown":
            markdown_text = input_path.read_text(encoding="utf-8")
            return self.convert_text(
                markdown_text,
                input_format="markdown",
                output_format=output_format,
                output_path=output_path,
                options=options,
            )

        self._convert_file(
            input_path=input_path,
            input_format=input_format,
            output_format=output_format,
            output_path=output_path,
            options=options,
        )
        return output_path

    def _convert_file(
        self,
        input_path: Path,
        input_format: str,
        output_format: str,
        output_path: Path,
        options: object,
    ) -> None:
        engine = self.registry.find(input_format=input_format, output_format=output_format)
        engine.convert(
            input_path=str(input_path),
            output_path=str(output_path),
            input_format=input_format,
            output_format=output_format,
            options=options,
        )

    def _markdown_to_html(self, text: str, options: object) -> str:
        for parser in self.parsers:
            if parser.is_available():
                return parser.to_html(text, options=options)
        raise RuntimeError("No available Markdown parser. Install markdown-it-py or markdown.")

    @staticmethod
    def _wrap_html(body_html: str, options: object) -> str:
        template = getattr(options, "html_template", None)
        if template is None:
            template = (
                "<!doctype html>"
                "<html>"
                "<head>"
                "<meta charset=\"utf-8\" />"
                "{style}"
                "</head>"
                "<body>{content}</body>"
                "</html>"
            )
        style_block = RenderPipeline._style_block(options)
        return template.format(content=body_html, style=style_block)

    @staticmethod
    def _style_block(options: object) -> str:
        theme_css = getattr(options, "theme_css", None)
        if not theme_css:
            return ""
        css_path = Path(theme_css)
        if not css_path.exists():
            return ""
        css_text = css_path.read_text(encoding="utf-8")
        return f"<style>{css_text}</style>"

    @staticmethod
    def _persist_intermediate(temp_dir: Path, output_path: Path, options: object) -> None:
        if not getattr(options, "keep_intermediate", False):
            return
        dest_dir = output_path.parent / "intermediate"
        dest_dir.mkdir(parents=True, exist_ok=True)
        for temp_file in temp_dir.iterdir():
            target = dest_dir / temp_file.name
            target.write_bytes(temp_file.read_bytes())

    @staticmethod
    def _infer_format(path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in {".md", ".markdown"}:
            return "markdown"
        if suffix in {".html", ".htm"}:
            return "html"
        return suffix.lstrip(".")
