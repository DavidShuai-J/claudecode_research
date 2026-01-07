"""Pandoc engine adapter."""

from __future__ import annotations

import shlex
import shutil
import subprocess
from pathlib import Path

from mdconvert_sdk.engines.base import BaseEngine, EngineCapability


class PandocEngine(BaseEngine):
    """Uses the pandoc CLI for conversions."""

    name = "pandoc"
    priority = 10

    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability("markdown", "pdf"),
            EngineCapability("markdown", "docx"),
            EngineCapability("markdown", "pptx"),
            EngineCapability("html", "pdf"),
            EngineCapability("html", "docx"),
            EngineCapability("html", "pptx"),
        ]

    def is_available(self) -> bool:
        return shutil.which("pandoc") is not None

    def convert(
        self,
        input_path: str,
        output_path: str,
        input_format: str,
        output_format: str,
        options: object,
    ) -> None:
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        command = [
            "pandoc",
            "--from",
            input_format,
            "--to",
            output_format,
            "-o",
            str(output_path_obj),
            str(input_path),
        ]

        theme_css = getattr(options, "theme_css", None)
        if theme_css and output_format == "pdf":
            command.extend(["--css", str(theme_css)])

        docx_template = getattr(options, "docx_template", None)
        if docx_template and output_format == "docx":
            command.extend(["--reference-doc", str(docx_template)])

        pptx_template = getattr(options, "pptx_template", None)
        if pptx_template and output_format == "pptx":
            command.extend(["--reference-doc", str(pptx_template)])

        metadata = getattr(options, "metadata", None) or {}
        for key, value in metadata.items():
            command.extend(["--metadata", f"{key}={value}"])

        extra_args = getattr(options, "extra_args", None) or []
        command.extend(extra_args)

        subprocess.run(command, check=True)

    @staticmethod
    def describe_command(command: list[str]) -> str:
        return " ".join(shlex.quote(part) for part in command)
