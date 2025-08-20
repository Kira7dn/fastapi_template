---
description: Generate Infrastructure Class Workflow
auto_execution_mode: 3
---

Generate infrastructure artifacts that implement Application layer ports: database models, repositories, external adapters/clients, and pipeline components, plus tests and migrations.

Follows Onion/Clean Architecture: Infrastructure implements interfaces from `application/interfaces/` and is injected into Presentation.

## Input JSON Schema

```json
[
  {
    "class_name": "ProductModel",
    "layer": "infrastructure/model",
    "description": "SQLAlchemy model for products",
    "table_name": "products",
    "columns": [
      "id: Integer primary_key=True",
      "name: String nullable=False",
      "category: String nullable=False",
      "price_range: String nullable=False"
    ],
    "imports": ["from sqlalchemy import Column, Integer, String"]
  },
  {
    "class_name": "ProductRepository",
    "layer": "infrastructure/repository",
    "description": "Implements IProductRepository using SQLAlchemy",
    "implements": "app.application.interfaces.product.IProductRepository",
    "dependencies": ["sqlalchemy.orm.Session"],
    "methods": [
      { "method_name": "create", "parameters": ["product: Product"], "return_type": "Product" },
      { "method_name": "get_by_id", "parameters": ["product_id: int"], "return_type": "Product" },
      { "method_name": "get_all", "parameters": [], "return_type": "list[Product]" }
    ],
    "imports": [
      "from sqlalchemy.orm import Session",
      "from app.domain.entities.product import Product",
      "from app.infrastructure.models.product import ProductModel"
    ]
  },
  {
    "class_name": "StripeClient",
    "layer": "infrastructure/adapter",
    "description": "Implements IPaymentGateway with retry/timeout and error handling",
    "implements": "app.application.interfaces.payment.IPaymentGateway",
    "config": ["STRIPE_SECRET_KEY", "STRIPE_DEFAULT_CURRENCY"],
    "methods": [
      { "method_name": "create_payment_intent", "parameters": ["amount_cents: int", "currency: str", "metadata: dict"], "return_type": "dict" }
    ]
  },
  {
    "class_name": "TranscribeStep",
    "layer": "infrastructure/pipeline_step",
    "description": "Pipeline step using ITranscriber",
    "implements": "app.application.interfaces.media.ITranscriber",
    "methods": [
      { "method_name": "run", "parameters": ["context: dict"], "return_type": "dict" }
    ]
  }
]
```

## Rules

- **Implements Ports**: Repositories/adapters must implement interfaces defined in `application/interfaces/` (e.g., `IProductRepository`).
- **Separation**: No business logic here; map data, call SDKs/DB, handle reliability (retry/backoff), read config from `app/core/config.py`.
- **Models**: SQLAlchemy models under `infrastructure/models/` with clear table names and constraints.
- **Repositories**: Under `infrastructure/repositories/`, inject `Session` or required resources through `__init__`.
- **Adapters**: Under `infrastructure/adapters/`, encapsulate external SDKs/HTTP with timeouts, retries, and idempotency.
- **Pipelines**: Under `infrastructure/pipelines/steps/`, classes with `run(context)` and simple data-in/data-out.
- **Migrations**: Use Alembic to sync DB schema with models; never edit DB directly.
- **Tests**: Integration tests for infra components; unit tests for small mappers/helpers. Coverage ≥85% where practical for non-external calls.
- **Typing**: Use precise types; never return raw SDK objects—map to domain entities or plain dicts/DTOs.
- **Idempotency**: Only overwrite files for classes in current JSON.

## Steps

### Step 1 – Generate SQLAlchemy Models

- **Location**: `backend/app/infrastructure/models/{snake_case(class_name)}.py`
- **Action**: For `layer == "infrastructure/model"`, create model inheriting `Base` from `app.infrastructure.database.base` with provided columns.

**Sample**:

```python
# backend/app/infrastructure/models/product.py
from sqlalchemy import Column, Integer, String
from app.infrastructure.database.base import Base

class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price_range = Column(String, nullable=False)
```

### Step 2 – Generate Repositories (DB Persistence)

- **Location**: `backend/app/infrastructure/repositories/{snake_case(base_name)}.py`
- **Action**: For `layer == "infrastructure/repository"`, implement the specified Application interface. Map between Domain and DB model.

**Sample**:

```python
# backend/app/infrastructure/repositories/product.py
from sqlalchemy.orm import Session
from app.application.interfaces.product import IProductRepository
from app.domain.entities.product import Product
from app.infrastructure.models.product import ProductModel

class ProductRepository(IProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        db_product = ProductModel(
            name=product.name,
            category=product.category,
            price_range=product.price_range,
        )
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return Product(
            id=db_product.id,
            name=db_product.name,
            category=db_product.category,
            price_range=db_product.price_range,
        )

    def get_by_id(self, product_id: int) -> Product:
        p = self.db.query(ProductModel).get(product_id)
        return Product(id=p.id, name=p.name, category=p.category, price_range=p.price_range)

    def get_all(self) -> list[Product]:
        return [
            Product(id=p.id, name=p.name, category=p.category, price_range=p.price_range)
            for p in self.db.query(ProductModel).all()
        ]
```

### Step 3 – Generate External Adapters

- **Location**: `backend/app/infrastructure/adapters/{snake_case(class_name)}.py`
- **Action**: For `layer == "infrastructure/adapter"`, implement the specified Application interface. Read config from `app/core/config.py`, add retry/timeout, and return plain dicts/DTOs.

**Sample**:

```python
# backend/app/infrastructure/adapters/payment.py
from typing import Dict
from app.application.interfaces.payment import IPaymentGateway
from app.core.config import settings

class StripeClient(IPaymentGateway):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.STRIPE_SECRET_KEY

    def create_payment_intent(self, amount_cents: int, currency: str, metadata: dict) -> Dict:
        # TODO: implement with HTTP SDK; ensure timeout/retry and idempotency key
        return {"id": "pi_123", "status": "requires_payment_method", "amount": amount_cents, "currency": currency}
```

### Step 4 – Generate Pipeline Steps

- **Location**: `backend/app/infrastructure/pipelines/steps/{snake_case(class_name)}.py`
- **Action**: For `layer == "infrastructure/pipeline_step"`, create a class with `name` and `run(context)` that mutates/returns context. Dependencies are injected via constructor.

**Sample**:

```python
# backend/app/infrastructure/pipelines/steps/transcribe_step.py
from typing import Dict, Any
from app.application.interfaces.media import ITranscriber

class TranscribeStep:
    name = "transcribe"
    def __init__(self, transcriber: ITranscriber):
        self.transcriber = transcriber
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context["text"] = self.transcriber.transcribe(context["audio_path"])
        return context
```

### Step 5 – Alembic Migrations

```bash
# Generate migration for model changes
venv/bin/alembic revision --autogenerate -m "apply infrastructure changes"
# Apply latest
venv/bin/alembic upgrade head
```

### Step 6 – Tests (Integration and Unit where applicable)

- **Location**:
  - Repositories: `backend/tests/integration/infrastructure/test_repositories_{snake_case}.py`
  - Adapters: `backend/tests/integration/infrastructure/test_adapters_{snake_case}.py`
  - Pipelines: `backend/tests/unit/infrastructure/test_pipeline_step_{snake_case}.py`
- **Action**: Use real DB (test DB) for repository tests, dependency overrides for adapters, and pure unit tests for steps.

**Samples**:

```python
# backend/tests/unit/infrastructure/test_pipeline_step_transcribe.py
import pytest
from app.infrastructure.pipelines.steps.transcribe_step import TranscribeStep

class FakeTranscriber:
    def transcribe(self, path: str):
        return "hello"

@pytest.mark.unit
def test_transcribe_step():
    step = TranscribeStep(FakeTranscriber())
    out = step.run({"audio_path": "/tmp/a.wav"})
    assert out["text"] == "hello"
```

```python
# backend/tests/integration/infrastructure/test_product_repository.py
import pytest
from sqlalchemy.orm import Session
from app.domain.entities.product import Product
from app.infrastructure.repositories.product import ProductRepository

@pytest.mark.integration
def test_create_and_fetch_product(db_session: Session):
    repo = ProductRepository(db_session)
    p = repo.create(Product(id=0, name="Phone", category="electronics", price_range="high"))
    got = repo.get_by_id(p.id)
    assert got.id == p.id
```

#### Testing Commands

```bash
# Unit tests (fast)
venv/bin/python -m pytest -m "not integration" -v

# Integration tests only
venv/bin/python -m pytest -m integration -v

# Coverage
venv/bin/python -m pytest --cov=app --cov-report=html --cov-fail-under=85
```

### Step 7 – Update JSON with Generated Paths

Add `code_path`, `code_raw_url`, `test_path`, `test_raw_url` to each item.

- Raw URL format: `https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/{path}`

**Sample Updated JSON**:

```json
[
  {
    "class_name": "ProductModel",
    "layer": "infrastructure/model",
    "code_path": "backend/app/infrastructure/models/product.py",
    "code_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/app/infrastructure/models/product.py"
  },
  {
    "class_name": "ProductRepository",
    "layer": "infrastructure/repository",
    "code_path": "backend/app/infrastructure/repositories/product.py",
    "code_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/app/infrastructure/repositories/product.py",
    "test_path": "backend/tests/integration/infrastructure/test_product_repository.py",
    "test_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/tests/integration/infrastructure/test_product_repository.py"
  },
  {
    "class_name": "StripeClient",
    "layer": "infrastructure/adapter",
    "code_path": "backend/app/infrastructure/adapters/payment.py",
    "code_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/app/infrastructure/adapters/payment.py",
    "test_path": "backend/tests/integration/infrastructure/test_payment_adapter.py",
    "test_raw_url": "https://raw.githubusercontent.com/Kira7dn/fastapi_template/main/backend/tests/integration/infrastructure/test_payment_adapter.py"
  }
]
```

## DI and Presentation Notes

- Provide factories in `presentation/api/v1/dependencies/` to instantiate repositories/adapters with required dependencies (DB session, API keys, clients).
- Endpoints should depend on interfaces and use cases; inject infrastructure via dependencies.
