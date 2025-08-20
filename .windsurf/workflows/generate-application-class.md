---
description: Generate Application Class Workflow
auto_execution_mode: 3
---

Generate application interfaces (ports) and use cases from JSON input with tests. Aligns with Onion/Clean Architecture: Presentation → Application → Domain. Infrastructure implements Application interfaces.

## Input JSON Schema

```json
[
  {
    "class_name": "Product",
    "layer": "application/interface",
    "description": "Repository port for product access",
    "methods": [
      { "method_name": "create", "parameters": ["product: Product"], "return_type": "Product" },
      { "method_name": "get_by_id", "parameters": ["product_id: int"], "return_type": "Product" },
      { "method_name": "get_all", "parameters": [], "return_type": "list[Product]" }
    ],
    "imports": ["from app.domain.entities.product import Product"]
  },
  {
    "class_name": "CreateProductUseCase",
    "layer": "application/use_case",
    "description": "Create a new product via repository port",
    "dependencies": ["IProductRepository"],
    "parameters": ["name: str", "category: str", "price_range: str"],
    "return_type": "Product",
    "imports": [
      "from app.application.interfaces.product import IProductRepository",
      "from app.domain.entities.product import Product"
    ]
  }
]
```

## Rules

- **Interfaces (Ports)**: `abc.ABC` with `@abstractmethod`, prefix `I<Name>`; location under `application/interfaces/`.
- **Use Cases**: Classes in `application/use_cases/` that orchestrate domain logic via interfaces only.
- **No Infra in Use Cases**: Do not import SDKs/DB/HTTP. Depend solely on interfaces.
- **Imports**: stdlib (`abc`, `typing`) + `app.domain.entities.*` + `app.application.interfaces.*`.
- **Prohibited**: DB sessions, HTTP calls, file I/O inside use cases.
- **Typing**: Use precise types; `Optional[T]` when JSON says "or None".
- **Determinism**: No randomness/time access inside use cases (pass in values from callers/tests).
- **Idempotency**: Only overwrite files for classes present in the current JSON.
- **Tests**: Mock/fake implementations of interfaces. Use `pytest.mark.unit` and `pytest.mark.parametrize(ids=...)` where applicable. Coverage ≥85%.

## Steps

### Step 1 – Generate Interfaces (Ports)

- **Location**: `backend/app/application/interfaces/{snake_case(base_name)}.py`
- **Action**: For `layer == "application/interface"`, generate an `I{ClassName}Repository` or `I{ClassName}` interface (as named in JSON) with abstract methods from `methods`.

**Sample**:

```python
# backend/app/application/interfaces/product.py
from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.product import Product

class IProductRepository(ABC):
    @abstractmethod
    def create(self, product: Product) -> Product: ...

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product: ...

    @abstractmethod
    def get_all(self) -> List[Product]: ...
```

### Step 2 – Generate Use Cases

- **Location**: `backend/app/application/use_cases/{snake_case(class_name)}.py`
- **Action**: For `layer == "application/use_case"`, generate a class with `__init__(self, ...)` injecting required interfaces and an `execute(...)` method with exact signature derived from `parameters`.
- **Notes**: Create/transform domain entities inside the use case. Do not use infra directly.

**Sample**:

```python
# backend/app/application/use_cases/create_product_use_case.py
from app.application.interfaces.product import IProductRepository
from app.domain.entities.product import Product

class CreateProductUseCase:
    def __init__(self, repo: IProductRepository):
        self.repo = repo

    def execute(self, name: str, category: str, price_range: str) -> Product:
        product = Product(id=0, name=name, category=category, price_range=price_range)
        return self.repo.create(product)
```

### Step 3 – Generate Tests (Unit)

- **Location**:
  - Use cases: `backend/tests/unit/application/test_use_case_{snake_case}.py`
  - Interfaces: Optionally generate a smoke test to ensure abstract methods cannot instantiate.
- **Action**: For each use case, create tests with fakes/mocks for interfaces. Cover happy-path and edge-cases. Use `pytest.mark.unit`.

**Sample**:

```python
# backend/tests/unit/application/test_use_case_create_product.py
import pytest
from app.application.use_cases.create_product_use_case import CreateProductUseCase
from app.domain.entities.product import Product

class InMemoryProductRepo:
    def __init__(self):
        self.items = []
    def create(self, product: Product) -> Product:
        product.id = len(self.items) + 1
        self.items.append(product)
        return product
    def get_by_id(self, product_id: int) -> Product:  # minimal for interface parity in tests
        return next(p for p in self.items if p.id == product_id)
    def get_all(self) -> list[Product]:
        return list(self.items)

@pytest.mark.unit
def test_create_product_success():
    repo = InMemoryProductRepo()
    uc = CreateProductUseCase(repo)
    p = uc.execute(name="Phone", category="electronics", price_range="high")
    assert p.id == 1
    assert p.category == "electronics"
```

### Step 4 – Run Tests

```bash
# Unit tests (fast)
venv/bin/python -m pytest -m "not integration" -v

# Enforce coverage
venv/bin/python -m pytest --cov=app --cov-report=html --cov-fail-under=85

# Targeted run
venv/bin/python -m pytest backend/tests/unit -q
```

**Artifacts**: Coverage HTML (`backend/tests/test_output/coverage/`), JUnit XML, logs

### Step 5 – Update JSON with Generated Paths

Add `code_path`, `code_raw_url`, `test_path`, `test_raw_url` for each item.

- Raw URL format: `https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/{path}`

**Sample Updated JSON**:

```json
[
  {
    "class_name": "IProductRepository",
    "layer": "application/interface",
    "description": "Repository port for product access",
    "methods": [
      { "method_name": "create", "parameters": ["product: Product"], "return_type": "Product" },
      { "method_name": "get_by_id", "parameters": ["product_id: int"], "return_type": "Product" },
      { "method_name": "get_all", "parameters": [], "return_type": "list[Product]" }
    ],
    "code_path": "backend/app/application/interfaces/product.py",
    "code_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/app/application/interfaces/product.py"
  },
  {
    "class_name": "CreateProductUseCase",
    "layer": "application/use_case",
    "description": "Create a new product via repository port",
    "dependencies": ["IProductRepository"],
    "parameters": ["name: str", "category: str", "price_range: str"],
    "return_type": "Product",
    "code_path": "backend/app/application/use_cases/create_product_use_case.py",
    "code_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/app/application/use_cases/create_product_use_case.py",
    "test_path": "backend/tests/unit/application/test_use_case_create_product.py",
    "test_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/tests/unit/application/test_use_case_create_product.py"
  }
]
```

## Notes for DI and Presentation

- Wire concrete implementations in `presentation/api/v1/dependencies/` by returning infrastructure classes that implement these interfaces.
- Endpoints should import use cases and request/response schemas only; inject interfaces via dependencies.
