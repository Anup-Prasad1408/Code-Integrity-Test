from dataclasses import dataclass, field
from typing import Any

@dataclass
class AnalysisResult:
    file_id: str
    filename: str
    language: str
    status: str = "pending"
    ast: dict[str, Any] = field(default_factory=dict)
    stylometry: dict[str, Any] = field(default_factory=dict)
    llm: dict[str, Any] = field(default_factory=dict)
    similarity: list[dict[str, Any]] = field(default_factory=list)
    risk: dict[str, Any] = field(default_factory=dict)
    summary: str = "Analysis has not been run."
