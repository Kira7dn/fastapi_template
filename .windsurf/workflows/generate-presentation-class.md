---
description: Generate Presentation Class Workflow
auto_execution_mode: 3
---

Generate Presentation layer artifacts: request/response schemas, DI dependencies, and FastAPI routers that call Application use cases. Aligns with Onion/Clean Architecture and the directory map in `workflow_llm_friendly.md`.

## Input JSON Schema

```json
[
  {
    "class_name": "Product",
    "layer": "presentation/schema",
    "description": "Request/response schemas for Product endpoints",
    "schemas": [
      { "name": "CreateProductRequest", "fields": ["name: str", "category: str", "price_range: str"] },
      { "name": "ProductResponse", "fields": ["id: int", "name: str", "category: str", "price_range: str"] }
    ]
  },
  {
    "class_name": "ProductDependencies",
    "layer": "presentation/dependency",
    "description": "Factories for injecting infrastructure implementations",
    "factories": [
      { "name": "get_product_repo", "returns": "app.application.interfaces.product.IProductRepository", "impl": "app.infrastructure.repositories.product.ProductRepository", "params": ["db: Session = Depends(get_db)"] }
    ]
  },
  {
    "class_name": "ProductRouter",
    "layer": "presentation/router",
    "description": "FastAPI router for product endpoints",
    "prefix": "/products",
    "tags": ["products"],
    "endpoints": [
      {
        "path": "",
        "method": "post",
        "name": "create_product",
        "request_model": "CreateProductRequest",
        "response_model": "ProductResponse",
        "use_case": "app.application.use_cases.create_product_use_case.CreateProductUseCase",
        "dependencies": ["get_product_repo"],
        "handler": "return CreateProductUseCase(repo).execute(request.name, request.category, request.price_range)"
      }
    ]
  }
]
```

## Rules

- **Schemas**: Pydantic `BaseModel` only. No business logic. Keep field names/types aligned with Domain entities/use case contracts.
- **Dependencies (DI)**: Provide factories in `presentation/api/v1/dependencies/` returning Application interfaces implemented by Infrastructure classes. Read config via `app/core/config.py` as needed.
- **Routers**: Thin endpoints that validate input, call Use Case, and return schema. No direct access to Infrastructure in routers; use DI to inject interfaces.
- **Imports**: stdlib + `fastapi`, `pydantic`, Application use cases/interfaces, DI factories, domain entities for model validation where necessary.
- **Testing**: API tests with `httpx.AsyncClient` (ASGI). Use dependency overrides for adapters/repos. Markers: `e2e` or `integration` accordingly.
- **Idempotency**: Only overwrite files for classes present in current JSON.

## Steps

### Step 1 – Generate Schemas

- **Location**: `backend/app/presentation/api/v1/schemas/{snake_case(base_name)}.py`
- **Action**: For `layer == "presentation/schema"`, create Pydantic models for request/response with fields from JSON.

**Sample**:

```python
# backend/app/presentation/api/v1/schemas/product.py
from pydantic import BaseModel

class CreateProductRequest(BaseModel):
    name: str
    category: str
    price_range: str

class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    price_range: str
```

### Step 2 – Generate Dependencies (DI Factories)

- **Location**: `backend/app/presentation/api/v1/dependencies/{snake_case(base_name)}.py`
- **Action**: For `layer == "presentation/dependency"`, create dependency providers returning concrete implementations of Application interfaces.

**Sample**:

```python
# backend/app/presentation/api/v1/dependencies/product.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.infrastructure.repositories.product import ProductRepository

def get_product_repo(db: Session = Depends(get_db)):
    return ProductRepository(db)
```

### Step 3 – Generate Routers

- **Location**: `backend/app/presentation/api/v1/routers/{snake_case(base_name)}.py`
- **Action**: For `layer == "presentation/router"`, create FastAPI `APIRouter` with endpoints defined in JSON. Use DI factories to resolve dependencies. Instantiate and call the specified Use Case.

**Sample**:

```python
# backend/app/presentation/api/v1/routers/product.py
from fastapi import APIRouter, Depends
from app.application.use_cases.create_product_use_case import CreateProductUseCase
from app.presentation.api.v1.dependencies.product import get_product_repo
from app.presentation.api.v1.schemas.product import CreateProductRequest, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])

@router.post("", response_model=ProductResponse)
def create_product(request: CreateProductRequest, repo=Depends(get_product_repo)):
    product = CreateProductUseCase(repo).execute(
        request.name, request.category, request.price_range
    )
    return ProductResponse.model_validate(product)
```

### Step 4 – Register Routers

- **Location**: `backend/app/presentation/main.py` (or your root app file)
- **Action**: Include routers into the FastAPI app.

**Sample**:

```python
# backend/app/presentation/main.py
from fastapi import FastAPI
from app.presentation.api.v1.routers.product import router as product_router

app = FastAPI()
app.include_router(product_router)
```

### Step 5 – Tests (API / E2E)

- **Location**: `backend/tests/e2e/test_{snake_case}_api.py` or `backend/tests/integration/presentation/test_{snake_case}_router.py`
- **Action**: Use `httpx.AsyncClient` to test endpoints. Override dependencies for external systems.

**Sample**:

```python
# backend/tests/e2e/test_product_api.py
import pytest
from httpx import AsyncClient
from app.presentation.main import app

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_product_create_flow():
    class InMemoryRepo:
        def __init__(self):
            self.items = []
        def create(self, product):
            product.id = len(self.items) + 1
            self.items.append(product)
            return product

    # Override DI for testing
    from app.presentation.api.v1.dependencies.product import get_product_repo
    app.dependency_overrides[get_product_repo] = lambda: InMemoryRepo()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        data = {"name": "Laptop", "category": "electronics", "price_range": "high"}
        res = await ac.post("/products", json=data)
        assert res.status_code == 200
        body = res.json()
        assert body["id"] > 0

    app.dependency_overrides.clear()
```

#### Testing Commands

```bash
# Run E2E/API tests
venv/bin/python -m pytest -m e2e -v

# Run integration tests for presentation
venv/bin/python -m pytest -m integration -v

# Run all with coverage
venv/bin/python -m pytest --cov=app --cov-report=html --cov-fail-under=85
```

### Step 6 – Update JSON with Generated Paths

Add `code_path`, `code_raw_url`, and for routers optionally `register_path` (where to include router) and tests.

- Raw URL format: `https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/{path}`

**Sample Updated JSON**:

```json
[
  {
    "class_name": "Product",
    "layer": "presentation/schema",
    "code_path": "backend/app/presentation/api/v1/schemas/product.py",
    "code_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/app/presentation/api/v1/schemas/product.py"
  },
  {
    "class_name": "ProductDependencies",
    "layer": "presentation/dependency",
    "code_path": "backend/app/presentation/api/v1/dependencies/product.py",
    "code_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/app/presentation/api/v1/dependencies/product.py"
  },
  {
    "class_name": "ProductRouter",
    "layer": "presentation/router",
    "code_path": "backend/app/presentation/api/v1/routers/product.py",
    "code_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/app/presentation/api/v1/routers/product.py",
    "test_path": "backend/tests/e2e/test_product_api.py",
    "test_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/tests/e2e/test_product_api.py",
    "register_path": "backend/app/presentation/main.py"
  }
]
```

## Notes

- Endpoints must remain thin: validate input, call Use Case, return schema.
- Use dependency overrides in tests to isolate external systems.
- Keep request/response models stable; version APIs as needed (e.g., under `api/v1/`).
