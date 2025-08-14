# Hướng Dẫn Xây Dựng Dự Án Software Với FastAPI, PostgreSQL, SQLAlchemy Và Alembic Theo Onion Architecture

## Giới Thiệu

Tài liệu này hướng dẫn cách xây dựng một dự án phần mềm AI sử dụng **Onion Architecture** – một mô hình kiến trúc phân lớp để đảm bảo tính độc lập, dễ kiểm thử và mở rộng. Chúng ta sẽ tập trung vào việc tích hợp các công nghệ:

- **FastAPI**: Framework web Python để xây dựng API nhanh chóng và hiệu quả.
- **PostgreSQL**: Cơ sở dữ liệu SQL mạnh mẽ để lưu trữ dữ liệu.
- **SQLAlchemy**: ORM (Object-Relational Mapping) để tương tác với database một cách trừu tượng.
- **Alembic**: Công cụ quản lý migration database để đồng bộ schema.
- **Pydantic**: Thư viện để định nghĩa models với validation data, được sử dụng xuyên suốt dự án cho entities, schemas request/response, và validation.

## Cấu Trúc Dự Án

Sử dụng cấu trúc thư mục sau để tổ chức code theo Onion:

```
project/
├── domain/
│   ├── entities.py       # Entities kinh doanh với Pydantic
│   ├── services.py       # Logic kinh doanh và AI
│   └── models/           # AI models (nếu cần lưu trữ)
├── application/
│   ├── use_cases.py      # Use cases orchestrate logic
│   └── interfaces.py     # Interfaces cho repositories
├── infrastructure/
│   ├── repositories.py   # Triển khai repo với SQLAlchemy
│   ├── database.py       # Config database
│   └── migrations/       # Alembic migration scripts
├── presentation/
│   ├── api/
│   │   ├── routers.py    # FastAPI endpoints
│   │   ├── schemas.py    # Pydantic schemas cho API
│   │   └── dependencies.py  # Dependency injection
│   └── main.py           # App entry point
├── tests/                # Unit/integration tests
├── config.py             # Env vars (e.g., DB_URL)
├── requirements.txt      # List dependencies
└── alembic.ini           # Alembic config
```

## Chi Tiết Triển Khai Theo Từng Lớp

### 1. Domain Layer (Lõi – Chứa Logic AI Thuần Túy)

Layer này độc lập, tập trung vào entities và services. Tích hợp AI coding ở đây: Ví dụ, một service recommendation sử dụng ML model. Sử dụng Pydantic BaseModel cho entities để có validation built-in.

- **entities.py**:

  ```python
  from pydantic import BaseModel, EmailStr, validator

  class User(BaseModel):
      id: int
      name: str
      email: EmailStr  # Sử dụng EmailStr để validate email tự động
      preferences: list[str]  # Dữ liệu cho AI recommendation

      @validator('preferences')
      def validate_preferences(cls, v):
          if not v:
              raise ValueError("Preferences cannot be empty")
          return v
  ```

- **services.py** (AI coding example: Recommendation service):

  ```python
  from domain.entities import User
  from sklearn.metrics.pairwise import cosine_similarity  # Import AI lib
  import numpy as np

  class RecommendationService:
      def recommend(self, user: User, all_users: list[User]) -> list[str]:
          # AI logic: Simple cosine similarity trên preferences
          user_vec = np.array([1 if pref in user.preferences else 0 for pref in ['ai', 'ml', 'data']])
          recommendations = []
          for other in all_users:
              other_vec = np.array([1 if pref in other.preferences else 0 for pref in ['ai', 'ml', 'data']])
              similarity = cosine_similarity([user_vec], [other_vec])[0][0]
              if similarity > 0.5:
                  recommendations.append(other.name)
          return recommendations
  ```

  **Hướng dẫn AI coding**: Giữ logic AI thuần túy (không kết nối DB). Train model riêng (offline) và load vào service nếu cần. Pydantic giúp validate input cho AI logic.

### 2. Application Layer (Orchestrate Use Cases)

Định nghĩa interfaces và use cases để kết nối domain với infrastructure. Use cases gọi AI services. Sử dụng Pydantic để validate input trong use cases nếu cần.

- **interfaces.py**:

  ```python
  from abc import ABC, abstractmethod
  from domain.entities import User

  class UserRepositoryInterface(ABC):
      @abstractmethod
      def create(self, user: User) -> User:
          pass

      @abstractmethod
      def get_by_id(self, user_id: int) -> User:
          pass

      @abstractmethod
      def get_all(self) -> list[User]:
          pass
  ```

- **use_cases.py** (Tích hợp AI):

  ```python
  from application.interfaces import UserRepositoryInterface
  from domain.entities import User
  from domain.services import RecommendationService

  class CreateUserUseCase:
      def __init__(self, repo: UserRepositoryInterface):
          self.repo = repo

      def execute(self, name: str, email: str, preferences: list[str]) -> User:
          # Validate với Pydantic
          user_data = {"id": 0, "name": name, "email": email, "preferences": preferences}
          user = User(**user_data)  # Pydantic sẽ validate tự động
          return self.repo.create(user)

  class RecommendUsersUseCase:
      def __init__(self, repo: UserRepositoryInterface):
          self.repo = repo
          self.rec_service = RecommendationService()

      def execute(self, user_id: int) -> list[str]:
          user = self.repo.get_by_id(user_id)
          all_users = self.repo.get_all()
          return self.rec_service.recommend(user, all_users)
  ```

  **Hướng dẫn AI coding**: Use cases là nơi orchestrate AI calls, đảm bảo input/output rõ ràng cho testing. Pydantic validate input trước khi gọi repository.

### 3. Infrastructure Layer (Kết Nối Database Và Migration)

Triển khai interfaces với SQLAlchemy và PostgreSQL. Sử dụng Alembic cho migration. Pydantic không trực tiếp dùng ở đây, nhưng entities Pydantic được map sang SQLAlchemy models.

- **database.py**:

  ```python
  from sqlalchemy import create_engine
  from sqlalchemy.ext.declarative import declarative_base
  from sqlalchemy.orm import sessionmaker
  import config  # DB_URL = "postgresql://user:pass@localhost/db"

  engine = create_engine(config.DB_URL)
  SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  Base = declarative_base()
  ```

- **repositories.py** (Map entities sang models):

  ```python
  from sqlalchemy import Column, Integer, String, ARRAY
  from sqlalchemy.orm import Session
  from application.interfaces import UserRepositoryInterface
  from domain.entities import User
  from infrastructure.database import Base

  class UserModel(Base):
      __tablename__ = "users"
      id = Column(Integer, primary_key=True, index=True)
      name = Column(String)
      email = Column(String, unique=True)
      preferences = Column(ARRAY(String))  # Cho AI data

  class UserRepository(UserRepositoryInterface):
      def __init__(self, db: Session):
          self.db = db

      def create(self, user: User) -> User:
          db_user = UserModel(name=user.name, email=user.email, preferences=user.preferences)
          self.db.add(db_user)
          self.db.commit()
          self.db.refresh(db_user)
          # Trả về Pydantic User
          return User(id=db_user.id, name=db_user.name, email=db_user.email, preferences=db_user.preferences)

      def get_by_id(self, user_id: int) -> User:
          db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
          if db_user:
              return User(id=db_user.id, name=db_user.name, email=db_user.email, preferences=db_user.preferences)
          raise ValueError("User not found")

      def get_all(self) -> list[User]:
          db_users = self.db.query(UserModel).all()
          return [User(id=u.id, name=u.name, email=u.email, preferences=u.preferences) for u in db_users]
  ```

- **Alembic Migration**:

  - Khởi tạo: `alembic init infrastructure/migrations`.
  - Tạo migration: `alembic revision --autogenerate -m "add users table"`.
  - Áp dụng: `alembic upgrade head`.

  **Hướng dẫn AI coding**: Lưu dữ liệu AI (như embeddings) trong columns phù hợp (e.g., JSONB cho vectors). Alembic giúp migrate khi schema AI thay đổi. Pydantic đảm bảo data integrity khi map từ DB.

### 4. Presentation Layer (API Với FastAPI)

Expose endpoints, inject dependencies. Sử dụng Pydantic cho request/response schemas.

- **schemas.py** (Pydantic schemas cho API):

  ```python
  from pydantic import BaseModel
  from typing import List

  class CreateUserRequest(BaseModel):
      name: str
      email: str
      preferences: List[str]

  class UserResponse(BaseModel):
      id: int
      name: str
      email: str
      preferences: List[str]

  class RecommendationResponse(BaseModel):
      recommendations: List[str]
  ```

- **dependencies.py**:

  ```python
  from fastapi import Depends
  from sqlalchemy.orm import Session
  from infrastructure.database import SessionLocal
  from infrastructure.repositories import UserRepository

  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()

  def get_user_repo(db: Session = Depends(get_db)):
      return UserRepository(db)
  ```

- **routers.py** (Endpoints với AI):

  ```python
  from fastapi import APIRouter, Depends
  from application.use_cases import CreateUserUseCase, RecommendUsersUseCase
  from presentation.api.dependencies import get_user_repo
  from presentation.api.schemas import CreateUserRequest, UserResponse, RecommendationResponse

  router = APIRouter()

  @router.post("/users/", response_model=UserResponse)
  def create_user(request: CreateUserRequest, repo = Depends(get_user_repo)):
      use_case = CreateUserUseCase(repo)
      user = use_case.execute(request.name, request.email, request.preferences)
      return UserResponse.from_orm(user)  # Hoặc user.dict() nếu không dùng from_orm

  @router.get("/recommend/{user_id}", response_model=RecommendationResponse)
  def recommend(user_id: int, repo = Depends(get_user_repo)):
      use_case = RecommendUsersUseCase(repo)
      recs = use_case.execute(user_id)
      return RecommendationResponse(recommendations=recs)
  ```

- **main.py**:

  ```python
  from fastapi import FastAPI
  from presentation.api.routers import router

  app = FastAPI()
  app.include_router(router)
  ```

  Chạy: `uvicorn presentation.main:app --reload`.

  **Hướng dẫn AI coding**: Endpoints cho AI inference (e.g., /recommend). Thêm async nếu AI heavy-compute. Pydantic tự động validate request và serialize response.

## Phân Tích Rủi Ro Và Best Practices Cho AI Coding

- **Rủi ro**: Overhead ORM cho dữ liệu AI lớn (giải pháp: Sử dụng raw SQL hoặc vector DB như pgvector cho PostgreSQL). Pydantic có thể thêm overhead validation, nhưng lợi ích validation vượt trội.
- **Security**: Validate input AI để tránh injection; Pydantic và FastAPI's built-in validation hỗ trợ tốt.
- **Performance**: Cache AI results (e.g., Redis); train models offline.
- **Testing**: Unit test domain AI riêng; integration test với mock DB. Test Pydantic validation.
- **Mở rộng**: Tích hợp advanced AI (e.g., PyTorch cho deep learning) ở domain services. Sử dụng Pydantic cho tất cả data models để consistency.

## Testing (pytest)

Tài liệu test chuẩn hóa nằm tại `tests/README.md`. Dưới đây là tóm tắt tích hợp để bạn áp dụng nhanh trong dự án:

- **Cấu trúc** (`tests/`):

  - `tests/unit/` – unit tests nhanh, thuần logic.
  - `tests/integration/` – chạm DB/IO/dịch vụ ngoài (dùng marker `@pytest.mark.integration`).
  - `tests/e2e/` – end-to-end/API flow.
  - `tests/test_output/` – logs, junit, coverage.
  - Cấu hình chung: `pytest.ini`; shared fixtures/logging: `tests/conftest.py`.

- **Quy tắc đặt tên & discovery** (theo `pytest.ini`):

  - File: `test_*.py`
  - Class: `Test*`
  - Function: `test_*`

- **Markers** (khai báo trong `pytest.ini`):

  - `integration`, `slow`, `ai`
  - Lọc chạy bằng `-m` (ví dụ: `-m "not integration"`).

- **Logging & Reports**:

  - Logs: `tests/test_output/logs/test_run.log` (set trong `tests/conftest.py`).
  - JUnit: `tests/test_output/junit/test-results.xml` (set trong `pytest.ini`).
  - Coverage HTML: `tests/test_output/coverage/` (bật sẵn qua `addopts`).

- **Chạy tests (luôn trong venv)**:

  - Toàn bộ: `venv/bin/python -m pytest -q`
  - Chỉ unit (loại integration): `venv/bin/python -m pytest -q -m "not integration"`
  - Chỉ integration: `venv/bin/python -m pytest -q -m integration`
  - Verbose/timings: `venv/bin/python -m pytest -v`
  - Tối đa 3 fail: `--maxfail=3`
  - JUnit: `--junitxml=tests/test_output/junit/test-results.xml`

- **Coverage** (bật mặc định trong `pytest.ini`):

  - `--cov=app --cov-report=term-missing --cov-report=html:tests/test_output/coverage`
  - Mở HTML: `tests/test_output/coverage/index.html`
  - Có thể ép ngưỡng: `--cov-fail-under=85`.

- **Fixtures & mẫu thường dùng** (đặt tại `tests/conftest.py`):

  - Fixtures dữ liệu/utility tái sử dụng.
  - `tmp_path` cho filesystem tạm.
  - `monkeypatch` cho ENV/cấu hình (ví dụ override `app.core.config.settings`).
  - Async tests với `pytest-asyncio` (strict): đánh dấu `@pytest.mark.asyncio`.
  - HTTP client FastAPI bằng `httpx.AsyncClient` với `ASGITransport` (cần `httpx[http2]`).
  - Session DB test (SQLite in-memory) và override dependency FastAPI khi cần.

- **Mẫu chạy subset**:

  - `venv/bin/python -m pytest -q tests/unit`
  - `venv/bin/python -m pytest -q -m integration`
  - `venv/bin/python -m pytest -q -m "not slow"`

- **Cập nhật mới liên quan**:
  - Coverage bật sẵn qua `pytest.ini` (+ `pytest-cov`).
  - Thêm `httpx[http2]` phục vụ test FastAPI.
  - Pydantic v2: response models có `from_attributes=True` để hỗ trợ `from_orm()`.
  - Bổ sung unit/integration tests mẫu cho wiring dependencies, session factories, và API user.

Lưu ý: Giữ unit test nhanh/isolated; mock external deps. Với API/E2E, dùng HTTP client fixture; ưu tiên override dependency thay vì gọi dịch vụ thật.
