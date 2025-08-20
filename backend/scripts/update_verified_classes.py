from __future__ import annotations

import json
from pathlib import Path
import re

REPO = "Kira7dn/fastapi_template"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main/"

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "projects/warehouse/verified_classes.json"

ENTITY_DIR = Path("backend/app/domain/entities")
SERVICE_DIR = Path("backend/app/domain/services")
TEST_UNIT_DIR = Path("backend/tests/unit")


def to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def compute_paths(layer: str, class_name: str) -> tuple[str, str, str, str]:
    snake = to_snake(class_name)
    if layer == "domain/entity":
        code_path = ENTITY_DIR / f"{snake}.py"
        test_path = TEST_UNIT_DIR / f"test_entities_{snake}.py"
    elif layer == "domain/service":
        code_path = SERVICE_DIR / f"{snake}.py"
        test_path = TEST_UNIT_DIR / f"test_services_{snake}.py"
    else:
        raise ValueError(f"Unsupported layer for path computation: {layer}")
    code_path_str = str(code_path).replace("\\", "/")
    test_path_str = str(test_path).replace("\\", "/")
    return (
        code_path_str,
        RAW_BASE + code_path_str,
        test_path_str,
        RAW_BASE + test_path_str,
    )


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    for item in data:
        layer = item.get("layer", "")
        class_name = item.get("class_name")
        if layer in ("domain/entity", "domain/service") and class_name:
            code_path, code_raw_url, test_path, test_raw_url = compute_paths(layer, class_name)
            item["code_path"] = code_path
            item["code_raw_url"] = code_raw_url
            item["test_path"] = test_path
            item["test_raw_url"] = test_raw_url
    JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
