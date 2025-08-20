---
description:
auto_execution_mode: 1
---

## Description

Generate code for domain classes and services based on a JSON input specification. Ensure deterministic structure, unit tests, and CI-ready output.

---

## Input Specification

**\[INPUT] JSON Schema Example:**

```json
[
  {
    "class_name": "PackagingAudit",
    "layer": "domain/entity",
    "inheritance": [],
    "description": "Represents a packaging audit entry for a packaged order.",
    "attributes": ["order_id: int", "timestamp: datetime"],
    "methods": [
      {
        "method_name": "create",
        "description": "Factory method to instantiate a PackagingAudit for a given order.",
        "parameters": ["order_id: int"],
        "return_type": "PackagingAudit"
      }
    ]
  }
]
```

---

## General Rules (Spec)

- **Entities** → Pydantic `BaseModel` with validators.
- **Services** → Pure functions / AI logic (no side effects).
- **Prohibited** → No DB, HTTP calls, or file I/O.
- **Style** → One class per file, deterministic naming.
- **Pydantic config (entities)** → `model_config = {"extra": "forbid", "validate_assignment": True}`.
- **Typing rules** → primitives `int|str|float|bool|datetime|list|dict`; “or None” → `Optional[...]`; unspecified list/dict element types → `list[Any]`, `dict[str, Any]`.
- **Validators coverage** → non-empty strings/lists, non-negative numbers, enum-like constraints inferred from description (e.g., statuses).
- **Imports policy** → stdlib + `pydantic` only.
- **Determinism** → no implicit time; only use timezone-aware UTC in explicit factory methods.
- **No side effects on import** → absolutely no DB/HTTP/file I/O on module import.
- **Idempotency** → only (over)write files for classes present in current JSON; do not alter unrelated files.

---

## Workflow (Step-by-Step)

### Step 1 – Define Entities classes

- **[Spec]**

  - Folder: `backend/app/domain/entities/*.py`.
  - Uses Pydantic BaseModel and validators
  - No external deps (no DB, HTTP, file I/O).
  - Other rules: see General Rules (Spec).

- **[Action]**

  - **[Parse Input]** Read the JSON and select items where `layer == "domain/*"`.
  - **[File Naming]** One file per class: `backend/app/domain/entities/{snake_case(class_name)}.py`.
  - **[Class Structure]** Define `class {class_name}(BaseModel)` with all fields from `attributes`.
  - **[Validators]** Implement validators appropriate to the fields and description. See General Rules for coverage requirements.
  - **[Methods]** Implement methods from `methods` with exact names/signatures; keep pure (no I/O).
  - For typing, imports, determinism, idempotency, and config, follow General Rules (Spec).

- **[Sample Code]**

  ```python
  # backend/app/domain/entities/product.py
  from pydantic import BaseModel, field_validator

  class Product(BaseModel):
      id: int
      name: str
      category: str  # 'electronics' | 'books' | 'clothing'
      price_range: str  # 'low' | 'medium' | 'high'

      @field_validator('category')
      @classmethod
      def validate_category(cls, v):
          allowed = ['electronics', 'books', 'clothing']
          if v not in allowed:
              raise ValueError(f"Invalid category: {v}")
          return v
  ```

---

### Step 2 – Define Services classes

- **[Spec]**
  - Folder: `backend/app/domain/services/*.py`.
  - Business logic as pure functions/classes (no side effects).
  - No external deps (no DB, HTTP, file I/O). Use stdlib only for imports unless otherwise stated.
  - Other rules: see General Rules (Spec).
- **[Action]**

  - **[Parse Input]** Read the JSON and select items where `layer == "domain/service"`.
  - **[File Naming]** One file per class: `backend/app/domain/services/{snake_case(class_name)}.py`.
  - **[Structure]** Define a class named exactly `{class_name}`. Do not keep state; use `@staticmethod`/`@classmethod` when possible.
  - **[Methods]** Implement each method from `methods` with exact names/signatures and docstrings describing the rule. Keep logic pure and deterministic.
  - **[Error Handling]** Validate inputs and raise precise exceptions (`ValueError`, `PermissionError`) rather than returning sentinel values.
  - **[Determinism]** Do not call clocks or RNG. If time is required, ensure it is passed in by caller (see General Rules).
  - **[Idempotency]** Overwrite files only for services present in the current JSON; do not alter unrelated files.
  - **[Acceptance Checklist]** Correct path/name; method signatures match; pure logic; deterministic; no I/O; imports respect policy.

- **[Sample Code]**

  ```python
  # backend/app/domain/services/recommendation.py
  from typing import List
  import numpy as np
  from app.domain.entities.product import Product

  class ProductRecommendationService:
      """Pure business logic for product recommendations."""

      @staticmethod
      def calculate_similarity(product1: Product, product2: Product) -> float:
          category_match = 1.0 if product1.category == product2.category else 0.0
          price_match = 1.0 if product1.price_range == product2.price_range else 0.5
          return (category_match + price_match) / 2.0

      @classmethod
      def recommend_similar(cls, target: Product, candidates: List[Product], limit: int = 5) -> List[Product]:
          scored = [(p, cls.calculate_similarity(target, p)) for p in candidates if p.id != target.id]
          scored.sort(key=lambda x: x[1], reverse=True)
          return [p for p, score in scored[:limit]]
  ```

---

### Step 3 – Create Unit Tests

- **[Spec]**

  - Location: `backend/tests/unit/`.
  - One test module per generated entity/service, mirroring names (e.g., `test_entities_order.py`, `test_service_orders_per_staff.py`).
  - Tests must be pure and deterministic; no DB/HTTP/file I/O.
  - Use pytest with clear assertions and parametrization; prefer raising exceptions over sentinel returns.
  - Coverage goal: ≥ 85% for `app.domain.*` (see General Rules for shared constraints).
  - Parametrization: use `pytest.mark.parametrize` to cover multiple data cases in a single test; add `ids=` for readable case names.
  - Discovery patterns: files `test_*.py`, classes `Test*`, functions `test_*` (per `pytest.ini`).
  - Markers: available `integration`, `slow`, `ai`. For unit scope, avoid using them or exclude via `-m "not slow and not integration and not ai"`.

- **[Action]**

  - **[Entities]** For each field, add at least:
    - One valid case.
    - One invalid case triggering validators (`ValueError`/`ValidationError`).
  - **[Entity methods]** Add happy-path and edge-case tests for each method.
  - **[Services]** For each service method:
    - Test happy-path with realistic inputs.
    - Test edge-cases and invalid inputs (expect precise exceptions like `ValueError`, `PermissionError`).
  - **[Patterns]** Use `@pytest.mark.parametrize` for matrix-style coverage. Use small helper builders to keep tests readable.
  - **[Determinism]** If time is needed, pass timestamps from tests; do not call clocks in code under test.
  - **[Acceptance Checklist]** Correct test paths/names; covers valid+invalid per field; happy+edge per method; no side effects; deterministic; meets coverage target.

- **[Sample Code]**

  - **[Entity Test Code]**

    ```python
    # backend/tests/unit/test_entities_product.py
    import pytest
    from pydantic import ValidationError
    from app.domain.entities.product import Product

    class TestProductEntity:
        def test_create_valid_product(self):
            p = Product(id=1, name="Book A", category="books", price_range="low")
            assert p.id == 1
            assert p.category == "books"

        @pytest.mark.parametrize("bad_category", ["toys", "food", ""])
        def test_validate_category_rejects_invalid(self, bad_category):
            with pytest.raises((ValueError, ValidationError)):
                Product(id=1, name="X", category=bad_category, price_range="low")
    ```

  - **[Service Test Code]**

    ```python
    # backend/tests/unit/test_services_recommendation.py
    from app.domain.entities.product import Product
    from app.domain.services.recommendation import ProductRecommendationService as Svc

    def _p(i, cat, price):
        return Product(id=i, name=f"P{i}", category=cat, price_range=price)

    def test_calculate_similarity_basic():
        a = _p(1, "books", "low")
        b = _p(2, "books", "low")
        c = _p(3, "electronics", "high")
        assert Svc.calculate_similarity(a, b) >= Svc.calculate_similarity(a, c)

    def test_recommend_similar_orders_by_score():
        target = _p(1, "books", "low")
        candidates = [_p(2, "books", "low"), _p(3, "books", "medium"), _p(4, "electronics", "high")]
        recs = Svc.recommend_similar(target, candidates, limit=2)
        assert len(recs) == 2
        assert recs[0].category == "books"
    ```

  - **[Parametrization Pattern]**

    ```python
    import pytest
    from pydantic import ValidationError
    from app.domain.entities.product import Product

    @pytest.mark.parametrize(
        "data,expect_ok",
        [
            ({"id": 1, "name": "X", "category": "books", "price_range": "low"}, True),
            ({"id": 2, "name": "X", "category": "toys", "price_range": "low"}, False),
        ],
        ids=["valid_books", "invalid_category"],
    )
    def test_entity_matrix(data, expect_ok):
        if expect_ok:
            assert Product(**data)
        else:
            with pytest.raises((ValueError, ValidationError)):
                Product(**data)
    ```

---

### Step 4 – Execution

Run unit tests inside virtual environment:

```bash
# Standard unit run (honors addopts in pytest.ini)
venv/bin/python -m pytest backend/tests/unit

# Exclude non-unit markers
venv/bin/python -m pytest backend/tests/unit -m "not slow and not integration and not ai"

# Enforce coverage threshold (optional, matches ≥85% goal)
venv/bin/python -m pytest backend/tests/unit --cov-fail-under=85
```

Artifacts generated by current config (see `pytest.ini` and `backend/tests/conftest.py`):

- Coverage HTML: `backend/tests/test_output/coverage`
- JUnit XML: `backend/tests/test_output/junit/test-results.xml`
- Test logs: `backend/tests/test_output/logs/test_run.log`

---

### Step 5 – Definition of Done (Checklist)

- [ ] Entities: Pydantic models with validators for all fields
- [ ] Services: Pure, deterministic logic (no side effects)
- [ ] Each entity field tested with at least one valid + one invalid case
- [ ] Each service method tested with happy-path + edge-case
- [ ] Unit tests cover ≥ 85% of `app.domain.*`
- [ ] No file I/O, DB, or HTTP calls
- [ ] Coverage threshold enforced (≥ 85%) using `--cov-fail-under=85`
- [ ] Artifacts generated:
  - [ ] Coverage HTML: `backend/tests/test_output/coverage/index.html`
  - [ ] JUnit XML: `backend/tests/test_output/junit/test-results.xml`
  - [ ] Logs: `backend/tests/test_output/logs/test_run.log`
- [ ] Naming follows discovery: files `test_*.py`, classes `Test*`, functions `test_*`
- [ ] Unit run excludes markers: `not slow and not integration and not ai`
- [ ] Parametrized tests use `ids=` for readable case names
- [ ] Deterministic tests (no clocks/RNG in code under test; timestamps passed from tests when needed)
- [ ] Tests executed via venv shims (e.g., `venv/bin/python -m pytest backend/tests/unit`); CI runs green with provided commands

### Step 6 – Update Input JSON with Generated URLs

- **[Spec]**

  - Locate the input JSON file path used for generation.
  - Augment each JSON item with code and test locations after generation.
  - Fields to add/update per item:
    - `code_path` (repo-relative path)
    - `code_raw_url` (raw GitHub URL)
    - `test_path` (repo-relative path)
    - `test_raw_url` (raw GitHub URL)
  - Raw URL format using repo `Kira7dn/fastapi_template`:
    - `https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/{path}`
  - Idempotent: overwrite these fields if present; do not change unrelated keys.

- **[Action]**

  - Pre-push generated code and tests to GitHub (from repo root):
    - Ensure Git user is configured and remote `origin` points to `github.com/Kira7dn/fastapi_template`
    - Stage generated files:
      - `git add backend/app/domain/entities/ backend/app/domain/services/ backend/tests/unit/`
    - Commit with a clear message:
      - `git commit -m "chore(domain): add/update generated entities and services" || true`
        - The `|| true` allows continuing if there are no changes to commit
    - Push to main:
      - `git push origin main`
  - Read `<input_json_path>` into a list of items.
  - For each item, compute `code_path`, `test_path` based on `layer` and `class_name`.
  - Compute `code_raw_url`, `test_raw_url` using the fixed ref `refs/heads/main` and paths.
  - Write the updated JSON back to `<input_json_path>` (preserve ordering; pretty-print optional).

- **[JSON Update Template]**

  ```json
  [
    {
      "class_name": "Product",
      "layer": "domain/entity",
      "description": "Product master record",
      "attributes": [
        "id: int",
        "name: str",
        "category: str",
        "price_range: str"
      ],
      "methods": [],
      "code_path": "backend/app/domain/entities/product.py",
      "code_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/refs/heads/main/backend/app/domain/entities/product.py",
      "test_path": "backend/tests/unit/test_entities_product.py",
      "test_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/refs/heads/main/backend/tests/unit/test_entities_product.py"
    }
  ]
  ```
