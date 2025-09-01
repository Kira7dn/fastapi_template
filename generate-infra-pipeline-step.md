---
description: Generate Infrastructure Pipeline Step
auto_execution_mode: 3
---

Generate infrastructure pipeline step classes that operate with a simple `run(context)` contract and are wired via DI.

## Input JSON Schema

```json
[
  {
    "class_name": "YourClassName",
    "layer": "domain/entity | domain/service | application/interface | application/use_case | infrastructure/model | infrastructure/repository | infrastructure/adapter | infrastructure/pipeline_step | presentation/schema | presentation/dependency | presentation/router",
    "description": "Short purpose of this class",
    "attributes": ["field_name: type"],
    "methods": [
      {
        "method_name": "method_name",
        "description": "Optional short method description",
        "parameters": ["arg1: type", "arg2: type"],
        "return_type": "ReturnType"
      }
    ],
    "dependencies": ["IExamplePort"]
  }
]
```

## Rules

- Location: `backend/app/infrastructure/pipelines/steps/{snake_case(class_name)}.py`
- Naming: file path = snake_case of `class_name`.
- Keep steps thin: data-in/data-out via `run(context)`; no heavy side effects.
- Dependencies injected through constructor.
- Idempotent: only overwrite files for items in current input.
- JSON Update: always add `code_path`, `code_raw_url`.

## Steps

### Step A – Generate Pipeline Step Class
- Create class with attribute `name` and method `run(context)`.
- Constructor accepts dependencies (from application interfaces) when available; otherwise keep parameters generic.

### Step B – (Optional) Unit Tests
- Create unit tests under `backend/tests/unit/infrastructure/test_pipeline_step_{snake_case}.py`.
- For pure skeletons, keep implementation minimal and test straightforward transformations.

## Sample

```python
# backend/app/infrastructure/pipelines/steps/transcribe_step.py
from typing import Dict, Any
# from app.application.interfaces.media import ITranscriber  # optional if interface not available yet

class TranscribeStep:
    name = "transcribe"
    def __init__(self, transcriber):  # type: ignore[no-untyped-def]
        self.transcriber = transcriber
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Example: attach transcript into context
        # text = self.transcriber.transcribe(context["audio_path"])  # when interface available
        # context["text"] = text
        raise NotImplementedError
```
