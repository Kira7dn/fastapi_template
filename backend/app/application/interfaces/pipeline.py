from typing import Protocol, Any, Dict, List


class IPipelineStep(Protocol):
    name: str

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute step with context, return updated context."""


class IPipeline(Protocol):
    steps: List[IPipelineStep]

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all steps and return final context."""
