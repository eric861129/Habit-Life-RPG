from __future__ import annotations

from pathlib import Path

import yaml

from backend.app.main import create_app


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"Duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_contract(text: str) -> dict:
    return yaml.load(text, Loader=UniqueKeyLoader)


def operation_signatures(specification: dict) -> dict[tuple[str, str], tuple[str, ...]]:
    signatures: dict[tuple[str, str], tuple[str, ...]] = {}
    for path, path_item in specification.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS:
                continue
            responses = tuple(sorted(str(code) for code in operation.get("responses", {})))
            signatures[(method.upper(), path)] = responses
    return signatures


def compare_contracts(runtime: dict, committed: dict) -> list[str]:
    runtime_signatures = operation_signatures(runtime)
    committed_signatures = operation_signatures(committed)
    differences: list[str] = []
    for operation in sorted(runtime_signatures.keys() | committed_signatures.keys()):
        method, path = operation
        if operation not in runtime_signatures:
            differences.append(f"{method} {path}: missing from runtime OpenAPI")
            continue
        if operation not in committed_signatures:
            differences.append(f"{method} {path}: missing from committed OpenAPI")
            continue
        runtime_responses = runtime_signatures[operation]
        committed_responses = committed_signatures[operation]
        if runtime_responses != committed_responses:
            differences.append(
                f"{method} {path}: runtime responses {list(runtime_responses)} "
                f"!= committed responses {list(committed_responses)}"
            )
    return differences


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    runtime = create_app().openapi()
    committed = load_contract((root / "docs" / "openapi.yaml").read_text(encoding="utf-8"))
    differences = compare_contracts(runtime, committed)
    if differences:
        print("OpenAPI contract mismatch:")
        for difference in differences:
            print(f"- {difference}")
        return 1
    print(f"OpenAPI contract matches: {len(operation_signatures(runtime))} operations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
