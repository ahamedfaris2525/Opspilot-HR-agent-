from pydantic import BaseModel, Field
from typing import Any


class AgentDecision(BaseModel):
    intent: str
    requires_tool: bool
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
