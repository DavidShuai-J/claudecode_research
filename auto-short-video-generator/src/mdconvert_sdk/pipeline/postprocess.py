"""Post-processing hooks for output formats."""

from __future__ import annotations

from typing import Callable


class PostprocessHook:
    """Register format-specific post-processing functions."""

    def __init__(self) -> None:
        self._hooks: dict[str, list[Callable[[str], None]]] = {}

    def register(self, output_format: str, hook: Callable[[str], None]) -> None:
        self._hooks.setdefault(output_format, []).append(hook)

    def run(self, output_format: str, output_path: str) -> None:
        for hook in self._hooks.get(output_format, []):
            hook(output_path)
