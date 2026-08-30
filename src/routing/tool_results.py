from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ToolResult(BaseModel, Generic[T]):
    data: T | None = None
    source: str
    retrieved_at: str
    effective_at: str | None = None
    quality: str = "unknown"
    is_stale: bool = False
    error: str | None = None
