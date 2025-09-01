# Workflow Input Schema – Hướng dẫn nhanh

File tham chiếu: `schema.json` (mẫu ví dụ) và `schema.rules.json` (JSON Schema để validate tự động).

## 1) Cấu trúc chung một phần tử input
Mỗi phần tử trong mảng input là một lớp cần generate.

```json
{
  "class_name": "YourClassName",
  "layer": "domain/entity | domain/service | application/interface | application/use_case | infrastructure/model | infrastructure/repository | infrastructure/adapter | infrastructure/pipeline_step | presentation/schema | presentation/dependency | presentation/router",
  "description": "Short purpose of this class",

  "attributes": ["field_name: type"],
  "methods": [
    {
      "method_name": "method_name",
      "description": "Optional method description",
      "parameters": ["arg1: type"],
      "return_type": "ReturnType"
    }
  ],
  "dependencies": ["IExamplePort"],
  "parameters": ["arg1: type"],
  "return_type": "ReturnType",
  "imports": ["from package.module import Symbol"],
  "inheritance": ["BaseClass"],

  "code_path": "backend/app/.../your_file.py",
  "code_raw_url": "https://repo/raw/.../your_file.py",
  "test_path": "backend/tests/.../test_your_file.py",
  "test_raw_url": "https://repo/raw/.../test_your_file.py"
}
```

Ghi chú:
- `attributes`, `parameters` dùng format chuỗi: `name: type` (có thể kèm default, ví dụ: `limit: int = 10`).
- Các trường `code_*` và `test_*` là hậu sinh (điền sau khi generate), không bắt buộc khi nhập liệu.

## 2) Ràng buộc theo layer (được kiểm tra bằng `schema.rules.json`)
- domain/entity: bắt buộc `attributes`.
- domain/service: bắt buộc `methods`.
- application/interface: bắt buộc `methods`.
- application/use_case: bắt buộc `dependencies`, `parameters`, `return_type`.
- infrastructure/model: bắt buộc `attributes`.
- infrastructure/repository: bắt buộc `attributes`, `methods`.
- infrastructure/adapter: bắt buộc `methods`.
- infrastructure/pipeline_step: bắt buộc `methods`.
- presentation/schema: bắt buộc `attributes`.
- presentation/dependency: bắt buộc `methods` và mỗi method phải có `return_type`.
- presentation/router: bắt buộc `methods`.

## 3) Ví dụ tối giản theo layer
- domain/entity
```json
{"class_name":"Product","layer":"domain/entity","attributes":["id: int","name: str"]}
```

- domain/service
```json
{"class_name":"ProductService","layer":"domain/service","methods":[{"method_name":"run","parameters":[],"return_type":"None"}]}
```

- application/interface
```json
{"class_name":"IProductRepository","layer":"application/interface","methods":[{"method_name":"get_by_id","parameters":["product_id: int"],"return_type":"Product"}]}
```

- application/use_case
```json
{"class_name":"CreateProduct","layer":"application/use_case","dependencies":["IProductRepository"],"parameters":["name: str"],"return_type":"Product"}
```

- infrastructure/model
```json
{"class_name":"ProductModel","layer":"infrastructure/model","attributes":["id: int","name: str"]}
```

- infrastructure/repository
```json
{"class_name":"SqlProductRepository","layer":"infrastructure/repository","attributes":["db: Any"],"methods":[{"method_name":"save","parameters":["product: Product"],"return_type":"Product"}]}
```

- infrastructure/adapter
```json
{"class_name":"StripeClient","layer":"infrastructure/adapter","methods":[{"method_name":"create_payment_intent","parameters":["amount: int","currency: str"],"return_type":"dict"}]}
```

- infrastructure/pipeline_step
```json
{"class_name":"TranscribeStep","layer":"infrastructure/pipeline_step","methods":[{"method_name":"run","parameters":["context: dict"],"return_type":"dict"}]}
```

- presentation/schema
```json
{"class_name":"CreateProductRequest","layer":"presentation/schema","attributes":["name: str","category: str"]}
```

- presentation/dependency
```json
{"class_name":"ProductsDependencies","layer":"presentation/dependency","methods":[{"method_name":"get_repo","parameters":[],"return_type":"IProductRepository"}]}
```

- presentation/router
```json
{"class_name":"ProductsRouter","layer":"presentation/router","methods":[{"method_name":"create","parameters":["request: CreateProductRequest"],"return_type":"ProductResponse"}]}
```

## 4) Cách validate nhanh bằng `schema.rules.json`
- Dùng bất kỳ validator JSON Schema nào (VS Code extension, ajv, `python -m jsonschema`, v.v.).
- Chỉ cần load input (mảng các phần tử) và chọn schema: `schema.rules.json`.

## 5) Lời khuyên
- Giữ `attributes`/`parameters` ngắn gọn, đúng format `name: type`.
- Thêm `imports` nếu có tham chiếu kiểu từ module khác.
- Với `presentation/dependency`, luôn điền `return_type` cho từng method.
