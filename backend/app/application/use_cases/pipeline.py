from typing import Dict, Any, List

from app.application.interfaces.pipeline import IPipeline, IPipelineStep


class SimplePipeline(IPipeline):
    def __init__(self, steps: List[IPipelineStep]):
        self.steps = steps

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        for step in self.steps:
            context = step.run(context)
        return context
