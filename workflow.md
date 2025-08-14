### Quy Trình Phát Triển Feature Theo Onion Architecture

Dựa trên hướng dẫn từ tài liệu `ai_coding_guide.markdown` (mô tả cấu trúc dự án Onion Architecture với FastAPI, PostgreSQL, SQLAlchemy, Alembic và Pydantic, tích hợp AI coding) và `README.md` (hướng dẫn testing với pytest), tôi sẽ xây dựng một quy trình phát triển sản phẩm rõ ràng, tuần tự. Quy trình này bắt đầu từ việc nhận yêu cầu feature từ người dùng, sau đó triển khai theo thứ tự các layer của Onion Architecture: **Domain → Application → Infrastructure → Presentation → Tests**.

Mục tiêu là đảm bảo tính độc lập giữa các layer, dễ kiểm thử, mở rộng và tích hợp AI một cách an toàn. Tôi sẽ sử dụng tư duy phê phán để nhấn mạnh rủi ro tiềm ẩn (ví dụ: overhead performance cho AI, validation data, hoặc dependency management) và đề xuất giải pháp thực tế (ví dụ: sử dụng Pydantic cho validation, mock trong tests).

Để minh họa, tôi lấy ví dụ cụ thể một yêu cầu feature: **"Thêm tính năng quản lý sản phẩm (Product) với recommendation dựa trên user preferences sử dụng AI đơn giản (cosine similarity trên attributes sản phẩm như category và price range). Người dùng có thể tạo sản phẩm mới và nhận recommendation sản phẩm tương tự."**

Quy trình được thiết kế để lặp lại cho từng feature, với các giai đoạn hành động rõ ràng. Bạn có thể cung cấp thêm chi tiết về yêu cầu để tôi tinh chỉnh (ví dụ: yêu cầu cụ thể về AI model, data validation, hoặc performance constraints).

#### Bước 0: Nhận và Làm Rõ Yêu Cầu Feature

- **Mô tả**: Bắt đầu bằng việc thu thập và làm rõ yêu cầu từ người dùng. Phân tích yêu cầu để xác định entities, logic kinh doanh (bao gồm AI), use cases, và rủi ro ban đầu.
- **Hành động**:
  - Hỏi thêm chi tiết: Entities liên quan? Input/output mong đợi? Tích hợp AI như thế nào (e.g., real-time inference hay offline)? Constraints (e.g., data volume, security)?
  - Phân tích rủi ro: Nếu feature liên quan AI, kiểm tra overhead compute (giải pháp: cache results); validation data để tránh bad input cho AI (sử dụng Pydantic); tích hợp với DB (e.g., lưu embeddings nếu cần).
- **Ví dụ với feature**:
  - Entities: Product (id, name, category, price_range).
  - Logic AI: Recommendation service sử dụng cosine similarity trên vectors từ category và price_range.
  - Use cases: Tạo sản phẩm mới; Recommend sản phẩm tương tự dựa trên preferences user (giả sử preferences là list category).
  - Rủi ro: Dữ liệu lớn có thể chậm (giải pháp: Sử dụng vector DB extension như pgvector nếu scale); Input invalid có thể làm crash AI (giải pháp: Pydantic validation).

Sau khi rõ yêu cầu, triển khai tuần tự các layer.

#### Bước 1: Triển Khai Domain Layer (Lõi – Logic Kinh Doanh và AI Thuần Túy)

- **Mô tả**: Tập trung vào entities và services độc lập, không phụ thuộc DB hay external. Đây là nơi đặt logic AI thuần túy (e.g., models ML). Sử dụng Pydantic cho entities để validation built-in, đảm bảo data integrity trước khi vào AI.
- **Hành động**:
  - Định nghĩa entities với Pydantic BaseModel.
  - Định nghĩa services chứa logic kinh doanh/AI (import thư viện cần thiết như numpy, sklearn).
  - Rủi ro: Logic AI phức tạp có thể khó test (giải pháp: Giữ thuần túy, train offline nếu cần); Validation thiếu (giải pháp: Sử dụng validators trong Pydantic).
- **Ví dụ cụ thể** (thêm vào `domain/entities.py` và `domain/services.py`):

  ```python
  # domain/entities.py
  from pydantic import BaseModel, field_validator

  class Product(BaseModel):
      id: int
      name: str
      category: str  # e.g., 'electronics', 'books'
      price_range: str  # e.g., 'low', 'medium', 'high'

      @field_validator('category')
      @classmethod
      def validate_category(cls, v):
          allowed = ['electronics', 'books', 'clothing']  # Business rule
          if v not in allowed:
              raise ValueError(f"Invalid category: {v}")
          return v

  # domain/services.py
  from domain.entities import Product
  from sklearn.metrics.pairwise import cosine_similarity
  import numpy as np

  class ProductRecommendationService:
      def recommend(self, target_product: Product, all_products: list[Product]) -> list[str]:
          # AI logic: Cosine similarity trên vectors (category + price_range)
          categories = ['electronics', 'books', 'clothing']
          price_ranges = ['low', 'medium', 'high']
          target_vec = np.array([1 if target_product.category == cat else 0 for cat in categories] +
                                [1 if target_product.price_range == pr else 0 for pr in price_ranges])
          recommendations = []
          for product in all_products:
              product_vec = np.array([1 if product.category == cat else 0 for cat in categories] +
                                     [1 if product.price_range == pr else 0 for pr in price_ranges])
              similarity = cosine_similarity([target_vec], [product_vec])[0][0]
              if similarity > 0.5:
                  recommendations.append(product.name)
          return recommendations
  ```

#### Bước 2: Triển Khai Application Layer (Orchestrate Use Cases và Interfaces)

- **Mô tả**: Định nghĩa interfaces cho repositories và use cases để kết nối domain với infrastructure. Use cases orchestrate logic, gọi AI services, và sử dụng Pydantic để validate input nếu cần.
- **Hành động**:
  - Định nghĩa interfaces (ABC) cho repositories.
  - Định nghĩa use cases inject repo và gọi services.
  - Rủi ro: Use cases phức tạp dẫn đến tight coupling (giải pháp: Giữ orchestration đơn giản, dễ mock); Input cho AI không validated (giải pháp: Sử dụng Pydantic trong entities).
- **Ví dụ cụ thể** (thêm vào `application/interfaces.py` và `application/use_cases.py`):

  ```python
  # application/interfaces.py
  from abc import ABC, abstractmethod
  from domain.entities import Product

  class ProductRepositoryInterface(ABC):
      @abstractmethod
      def create(self, product: Product) -> Product:
          pass

      @abstractmethod
      def get_by_id(self, product_id: int) -> Product:
          pass

      @abstractmethod
      def get_all(self) -> list[Product]:
          pass

  # application/use_cases.py
  from application.interfaces import ProductRepositoryInterface
  from domain.entities import Product
  from domain.services import ProductRecommendationService

  class CreateProductUseCase:
      def __init__(self, repo: ProductRepositoryInterface):
          self.repo = repo

      def execute(self, name: str, category: str, price_range: str) -> Product:
          product_data = {"id": 0, "name": name, "category": category, "price_range": price_range}
          product = Product(**product_data)  # Pydantic validates automatically
          return self.repo.create(product)

  class RecommendProductsUseCase:
      def __init__(self, repo: ProductRepositoryInterface):
          self.repo = repo
          self.rec_service = ProductRecommendationService()

      def execute(self, product_id: int) -> list[str]:
          product = self.repo.get_by_id(product_id)
          all_products = self.repo.get_all()
          return self.rec_service.recommend(product, all_products)
  ```

#### Bước 3: Triển Khai Infrastructure Layer (Kết Nối DB và Migration)

- **Mô tả**: Triển khai repositories với SQLAlchemy, map entities Pydantic sang models DB. Sử dụng Alembic cho migration schema.
- **Hành động**:
  - Định nghĩa SQLAlchemy models.
  - Triển khai repositories.
  - Tạo migration với Alembic.
  - Rủi ro: Overhead ORM cho data AI lớn (giải pháp: Raw SQL hoặc pgvector cho vectors); Schema thay đổi (giải pháp: Alembic auto-generate).
- **Ví dụ cụ thể** (thêm vào `infrastructure/repositories.py`, cập nhật `database.py` nếu cần; chạy Alembic commands):

  ```python
  # infrastructure/repositories.py
  from sqlalchemy import Column, Integer, String
  from sqlalchemy.orm import Session
  from application.interfaces import ProductRepositoryInterface
  from domain.entities import Product
  from infrastructure.database import Base

  class ProductModel(Base):
      __tablename__ = "products"
      id = Column(Integer, primary_key=True, index=True)
      name = Column(String)
      category = Column(String)
      price_range = Column(String)

  class ProductRepository(ProductRepositoryInterface):
      def __init__(self, db: Session):
          self.db = db

      def create(self, product: Product) -> Product:
          db_product = ProductModel(name=product.name, category=product.category, price_range=product.price_range)
          self.db.add(db_product)
          self.db.commit()
          self.db.refresh(db_product)
          return Product(id=db_product.id, name=db_product.name, category=db_product.category, price_range=db_product.price_range)

      def get_by_id(self, product_id: int) -> Product:
          db_product = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
          if db_product:
              return Product(id=db_product.id, name=db_product.name, category=db_product.category, price_range=db_product.price_range)
          raise ValueError("Product not found")

      def get_all(self) -> list[Product]:
          db_products = self.db.query(ProductModel).all()
          return [Product(id=p.id, name=p.name, category=p.category, price_range=p.price_range) for p in db_products]
  ```

  - Migration: Chạy `alembic revision --autogenerate -m "add products table"` rồi `alembic upgrade head`.

#### Bước 4: Triển Khai Presentation Layer (API Endpoints)

- **Mô tả**: Expose endpoints với FastAPI, sử dụng Pydantic cho schemas request/response, inject dependencies.
- **Hành động**:
  - Định nghĩa schemas.
  - Định nghĩa dependencies và routers.
  - Rủi ro: API chậm do AI heavy (giải pháp: Async endpoints); Security holes (giải pháp: Pydantic validation).
- **Ví dụ cụ thể** (thêm vào `presentation/api/schemas.py`, `dependencies.py`, `routers.py`; cập nhật `main.py`):

  ```python
  # presentation/api/schemas.py
  from pydantic import BaseModel
  from typing import List

  class CreateProductRequest(BaseModel):
      name: str
      category: str
      price_range: str

  class ProductResponse(BaseModel):
      id: int
      name: str
      category: str
      price_range: str

  class RecommendationResponse(BaseModel):
      recommendations: List[str]

  # presentation/api/dependencies.py (cấu hình đầy đủ, tương tự phần user trong guide)
  from fastapi import Depends
  from sqlalchemy.orm import Session
  from infrastructure.database import SessionLocal
  from infrastructure.repositories import ProductRepository

  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()

  def get_product_repo(db: Session = Depends(get_db)):
      return ProductRepository(db)

  # presentation/api/routers.py
  from fastapi import APIRouter, Depends
  from application.use_cases import CreateProductUseCase, RecommendProductsUseCase
  from presentation.api.dependencies import get_product_repo
  from presentation.api.schemas import CreateProductRequest, ProductResponse, RecommendationResponse

  router = APIRouter()

  @router.post("/products/", response_model=ProductResponse)
  def create_product(request: CreateProductRequest, repo = Depends(get_product_repo)):
      use_case = CreateProductUseCase(repo)
      product = use_case.execute(request.name, request.category, request.price_range)
      # Pydantic v2: ưu tiên model_validate; nếu muốn from_orm, cấu hình ConfigDict(from_attributes=True)
      return ProductResponse.model_validate(product)

  @router.get("/recommend-product/{product_id}", response_model=RecommendationResponse)
  def recommend(product_id: int, repo = Depends(get_product_repo)):
      use_case = RecommendProductsUseCase(repo)
      recs = use_case.execute(product_id)
      return RecommendationResponse(recommendations=recs)
  ```

  - Include router vào `main.py`.

#### Bước 5: Triển Khai Tests (Unit, Integration, E2E)

- **Mô tả**: Viết tests theo cấu trúc từ `README.md`: unit (domain/application), integration (infrastructure), e2e (presentation). Sử dụng pytest markers, fixtures, và coverage.
- **Hành động**:
  - Unit: Test logic thuần (mock repos).
  - Integration: Test với DB in-memory.
  - E2E: Test API endpoints.
  - Rủi ro: Tests chậm (giải pháp: Markers như @slow, exclude integration khi dev); Coverage thấp (giải pháp: Enforce --cov-fail-under=85).
  - Chạy: `venv/bin/python -m pytest -q` (toàn bộ); `-m "not integration"` (chỉ unit).
- **Ví dụ cụ thể** (thêm vào `tests/unit/`, `tests/integration/`, `tests/e2e/`):

  ```python
  # tests/unit/test_product_service.py
  from domain.services import ProductRecommendationService
  from domain.entities import Product

  def test_recommend():
      service = ProductRecommendationService()
      p1 = Product(id=1, name="Laptop", category="electronics", price_range="high")
      p2 = Product(id=2, name="Phone", category="electronics", price_range="medium")
      recs = service.recommend(p1, [p2])
      assert "Phone" in recs  # Similarity cao

  # tests/integration/test_product_repo.py
  import pytest
  from infrastructure.repositories import ProductRepository
  from domain.entities import Product
  # Giả sử fixture db_session từ conftest.py
  @pytest.mark.integration
  def test_create_product(db_session):
      repo = ProductRepository(db_session)
      product = Product(id=0, name="Book", category="books", price_range="low")
      created = repo.create(product)
      assert created.id > 0

  # tests/e2e/test_product_api.py
  import pytest
  from httpx import AsyncClient
  # Giả sử fixture http_client từ conftest.py
  @pytest.mark.asyncio
  async def test_create_and_recommend(http_client: AsyncClient):
      resp = await http_client.post("/products/", json={"name": "Tablet", "category": "electronics", "price_range": "medium"})
      assert resp.status_code == 200
      product_id = resp.json()["id"]
      rec_resp = await http_client.get(f"/recommend-product/{product_id}")
      assert rec_resp.status_code == 200
  ```

#### Kết Thúc Quy Trình và Iteration

- Sau khi hoàn thành, review toàn bộ: Chạy tests với coverage, kiểm tra rủi ro (e.g., performance benchmark cho AI), và deploy (e.g., uvicorn).
- Iteration: Nếu feature cần refine, quay lại Bước 0 với feedback.
- Kế hoạch dự án: Phân giai đoạn (e.g., Week 1: Domain + Application; Week 2: Infrastructure + Presentation; Week 3: Tests + Optimization). Bạn nghĩ sao về ví dụ này? Có yêu cầu feature cụ thể nào để chúng ta áp dụng quy trình?
