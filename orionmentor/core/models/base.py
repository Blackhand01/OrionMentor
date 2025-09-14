from typing import Protocol, Any

class LLMProvider(Protocol):
    name: str
    def invoke(self, prompt: str) -> Any: ...
