---
description: Generate Domain Class Workflow
auto_execution_mode: 3
---

Generate domain classes and services from JSON input with tests and GitHub integration.

## Input JSON Schema

```json
[
  {
    "class_name": "PackagingAudit",
    "layer": "domain/entity",
    "description": "Represents a packaging audit entry for a packaged order.",
    "attributes": ["order_id: int", "timestamp: datetime"],
    "methods": [
      {
        "method_name": "create",
        "parameters": ["order_id: int"],
        "return_type": "PackagingAudit"
      }
    ]
  }
]
```

## Rules

- **Entities**: Pydantic `BaseModel` with validators, `model_config = {"extra": "forbid", "validate_assignment": True}`
- **Services**: Pure functions/classes, no side effects
- **Prohibited**: DB, HTTP calls, file I/O
- **Imports**: stdlib + pydantic only
- **Tests**: ≥85% coverage, deterministic, use `pytest.mark.parametrize` with `ids=`
- **Typing**: primitives `int|str|float|bool|datetime|list|dict`; "or None" → `Optional[...]`
- **Idempotency**: only overwrite files for classes in current JSON

## Steps

### Step 1 – Generate Entities

- **Location**: `backend/app/domain/entities/{snake_case(class_name)}.py`
- **Action**: Parse JSON for `layer == "domain/entity"`, create Pydantic BaseModel with:
  - All fields from `attributes`
  - Validators for non-empty strings/lists, non-negative numbers, enum constraints
  - Methods from `methods` array with exact signatures

**Sample**:

```python
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    model_config = {"extra": "forbid", "validate_assignment": True}

    id: int
    name: str
    category: str

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        allowed = ['electronics', 'books', 'clothing']
        if v not in allowed:
            raise ValueError(f"Invalid category: {v}")
        return v
```

### Step 2 – Generate Services

- **Location**: `backend/app/domain/services/{snake_case(class_name)}.py`
- **Action**: Parse JSON for `layer == "domain/service"`, create pure business logic:
  - Use `@staticmethod`/`@classmethod` when possible
  - Implement methods with exact signatures from JSON
  - Raise precise exceptions (`ValueError`, `PermissionError`)
  - No state, no I/O, deterministic

**Sample**:

```python
from typing import List
from app.domain.entities.product import Product

class ProductRecommendationService:
    @staticmethod
    def calculate_similarity(product1: Product, product2: Product) -> float:
        category_match = 1.0 if product1.category == product2.category else 0.0
        return category_match

    @classmethod
    def recommend_similar(cls, target: Product, candidates: List[Product], limit: int = 5) -> List[Product]:
        scored = [(p, cls.calculate_similarity(target, p)) for p in candidates if p.id != target.id]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, score in scored[:limit]]
```

### Step 3 – Generate Tests

- **Location**: `backend/tests/unit/test_entities_{snake_case}.py`, `test_services_{snake_case}.py`
- **Action**: Create comprehensive test coverage:
  - **Entities**: Valid/invalid cases for each field, method happy-path + edge-cases
  - **Services**: Happy-path + edge-cases for each method
  - Use `pytest.mark.parametrize` with `ids=` for readable case names
  - Deterministic (pass timestamps from tests, no clocks/RNG in code under test)

**Sample**:

```python
import pytest
from pydantic import ValidationError
from app.domain.entities.product import Product

class TestProductEntity:
    def test_create_valid_product(self):
        p = Product(id=1, name="Book A", category="books")
        assert p.id == 1
        assert p.category == "books"

    @pytest.mark.parametrize("bad_category", ["toys", "food", ""], ids=["invalid_toys", "invalid_food", "empty"])
    def test_validate_category_rejects_invalid(self, bad_category):
        with pytest.raises((ValueError, ValidationError)):
            Product(id=1, name="X", category=bad_category)
```

### Step 4 – Run Tests

```bash
# Standard unit run
venv/bin/python -m pytest backend/tests/unit

# With coverage enforcement
venv/bin/python -m pytest backend/tests/unit --cov-fail-under=85

# Exclude non-unit markers
venv/bin/python -m pytest backend/tests/unit -m "not slow and not integration and not ai"
```

**Artifacts**: Coverage HTML (`backend/tests/test_output/coverage/`), JUnit XML, logs

### Step 5 – Push & Update JSON

**Update Input JSON** with generated file locations:

- Add `code_path`, `code_raw_url`, `test_path`, `test_raw_url` to each item
- Raw URL format: `https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/{path}`

**Sample Updated JSON**:

```json
[
  {
    "class_name": "Product",
    "layer": "domain/entity",
    "description": "Product master record",
    "attributes": ["id: int", "name: str", "category: str"],
    "methods": [],
    "code_path": "backend/app/domain/entities/product.py",
    "code_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/app/domain/entities/product.py",
    "test_path": "backend/tests/unit/test_entities_product.py",
    "test_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/tests/unit/test_entities_product.py"
  }
]
```
