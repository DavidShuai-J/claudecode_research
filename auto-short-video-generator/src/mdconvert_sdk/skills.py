"""Skill wrapper for document conversion."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from mdconvert_sdk.client import ConversionOptions, ConverterClient


@dataclass(slots=True)
class SkillMetadata:
    """Basic metadata for the conversion skill."""

    name: str = "markdown-document-conversion"
    description: str = "Convert Markdown or HTML to PDF, DOCX, or PPTX outputs."


class MarkdownConversionSkill:
    """Skill wrapper that exposes conversion as a single callable service."""

    def __init__(self, client: ConverterClient | None = None) -> None:
        self.client = client or ConverterClient()
        self.meta = SkillMetadata()

    def convert_markdown(
        self,
        markdown_text: str,
        output_format: str,
        output_path: str | Path,
        options: ConversionOptions | None = None,
    ) -> Path:
        return self.client.convert_markdown(
            markdown_text,
            to=output_format,
            output_path=output_path,
            options=options,
        )

    def convert_file(
        self,
        input_path: str | Path,
        output_format: str,
        output_path: str | Path,
        options: ConversionOptions | None = None,
    ) -> Path:
        return self.client.convert_file(
            input_path,
            to=output_format,
            output_path=output_path,
            options=options,
        )

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generic skill entry point for orchestrators.

        Expected payload:
        {
            "input_type": "markdown" | "file",
            "input": "<markdown_text>" | "<input_path>",
            "output_format": "pdf" | "docx" | "pptx",
            "output_path": "<output_path>",
            "options": { ... ConversionOptions fields ... }
        }
        """

        options_payload = payload.get("options") or {}
        options = ConversionOptions(**options_payload)

        input_type = payload.get("input_type", "markdown")
        output_format = payload["output_format"]
        output_path = payload["output_path"]
        if input_type == "file":
            result_path = self.convert_file(
                input_path=payload["input"],
                output_format=output_format,
                output_path=output_path,
                options=options,
            )
        else:
            result_path = self.convert_markdown(
                markdown_text=payload["input"],
                output_format=output_format,
                output_path=output_path,
                options=options,
            )

        return {"output_path": str(result_path), "output_format": output_format}
