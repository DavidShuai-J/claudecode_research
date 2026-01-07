"""Engine abstractions and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable


@dataclass(slots=True)
class EngineCapability:
    """Represents a conversion capability (input -> output)."""

    input_format: str
    output_format: str


class BaseEngine(ABC):
    """Base class for all conversion engines."""

    name: str = "base"
    priority: int = 100

    @abstractmethod
    def capabilities(self) -> Iterable[EngineCapability]:
        """Return the conversion capabilities supported by the engine."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the engine can run in the environment."""

    @abstractmethod
    def convert(
        self,
        input_path: str,
        output_path: str,
        input_format: str,
        output_format: str,
        options: object,
    ) -> None:
        """Perform a conversion using the engine."""


class EngineRegistry:
    """Registry that selects the best available engine."""

    def __init__(self) -> None:
        self._engines: list[BaseEngine] = []

    def register(self, engine: BaseEngine) -> None:
        self._engines.append(engine)
        self._engines.sort(key=lambda e: e.priority)

    def find(self, input_format: str, output_format: str) -> BaseEngine:
        for engine in self._engines:
            if not engine.is_available():
                continue
            for capability in engine.capabilities():
                if capability.input_format == input_format and capability.output_format == output_format:
                    return engine
        raise RuntimeError(
            f"No available engine for {input_format} -> {output_format}. "
            f"Registered: {[engine.name for engine in self._engines]}"
        )
