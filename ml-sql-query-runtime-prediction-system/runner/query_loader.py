from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_query(query_file_path: str | Path) -> str:
    """Load a SQL query from file and return it as a normalized string."""
    path = Path(query_file_path)
    if not path.exists():
        raise FileNotFoundError(f"Query file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def list_query_files(queries_dir: str | Path = Path("queries")) -> list[Path]:
    """Return sorted query files matching q*.sql from the queries directory."""
    path = Path(queries_dir)
    if not path.exists():
        return []
    return sorted(path.glob("q*.sql"), key=lambda p: p.stem)


def load_query_catalog(catalog_path: str | Path = Path("queries") / "query_catalog.json") -> list[dict[str, Any]]:
    """Load query catalog JSON and return query entries."""
    path = Path(catalog_path)
    if not path.exists():
        raise FileNotFoundError(f"Query catalog not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or "queries" not in payload:
        raise ValueError("Invalid catalog format. Expected object with 'queries' field.")

    queries = payload["queries"]
    if not isinstance(queries, list):
        raise ValueError("Invalid catalog format. 'queries' must be a list.")
    return queries


def save_query_catalog(
    queries: list[dict[str, Any]],
    catalog_path: str | Path = Path("queries") / "query_catalog.json",
) -> Path:
    """Save query entries to query catalog JSON."""
    path = Path(catalog_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": 1,
        "query_count": len(queries),
        "queries": queries,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
