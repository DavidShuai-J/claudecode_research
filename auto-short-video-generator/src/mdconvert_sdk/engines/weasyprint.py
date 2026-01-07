"""WeasyPrint engine for HTML -> PDF."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from mdconvert_sdk.engines.base import BaseEngine, EngineCapability


class WeasyPrintEngine(BaseEngine):
    """Uses WeasyPrint to convert HTML to PDF."""

    name = "weasyprint"
    priority = 20

    def capabilities(self) -> list[EngineCapability]:
        return [EngineCapability("html", "pdf")]

    def is_available(self) -> bool:
        return importlib.util.find_spec("weasyprint") is not None

    def convert(
        self,
        input_path: str,
        output_path: str,
        input_format: str,
        output_format: str,
        options: object,
    ) -> None:
        if output_format != "pdf":
            raise ValueError("WeasyPrint only supports HTML -> PDF.")

        from weasyprint import HTML

        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        css_files: list[str] = []
        theme_css = getattr(options, "theme_css", None)
        if theme_css:
            css_files.append(str(theme_css))

        HTML(filename=input_path).write_pdf(str(output_path_obj), stylesheets=css_files)
