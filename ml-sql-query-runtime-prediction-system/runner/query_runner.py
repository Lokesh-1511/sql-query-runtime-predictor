from __future__ import annotations

import argparse
import random
import time
from pathlib import Path
from statistics import mean, median
from typing import Any

import duckdb
import pandas as pd

try:
    from runner.query_loader import load_query_catalog
except ModuleNotFoundError:
    from query_loader import load_query_catalog


DEFAULT_DB_PATH = Path("data") / "tpch.db"
DEFAULT_OUTPUT_PATH = Path("data") / "query_runtime_logs.csv"
DEFAULT_CATALOG_PATH = Path("queries") / "query_catalog.json"
DEFAULT_EXECUTION_DATASET_PATH = Path("data") / "query_execution_dataset.csv"


def connect_to_database(db_path: str | Path = DEFAULT_DB_PATH) -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection for the provided database path."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))


def execute_query(conn: duckdb.DuckDBPyConnection, query_text: str) -> pd.DataFrame:
    """Execute SQL and return results as a DataFrame."""
    return conn.execute(query_text).fetch_df()


def measure_runtime(conn: duckdb.DuckDBPyConnection, query_text: str) -> float:
    """Execute SQL and return elapsed runtime in seconds."""
    start = time.perf_counter()
    conn.execute(query_text).fetchall()
    end = time.perf_counter()
    return end - start


def _tables_used_to_string(tables_used: list[str]) -> str:
    """Serialize table list as a stable, comma-separated string for CSV logs."""
    return ",".join(tables_used)


def _explain_text(conn: duckdb.DuckDBPyConnection, query_text: str, analyze: bool = False) -> str:
    """Return EXPLAIN or EXPLAIN ANALYZE text for a query."""
    prefix = "EXPLAIN ANALYZE" if analyze else "EXPLAIN"
    rows = conn.execute(f"{prefix} {query_text}").fetchall()
    parts: list[str] = []
    for row in rows:
        if len(row) == 1:
            parts.append(str(row[0]))
        else:
            parts.append(" | ".join(str(cell) for cell in row))
    return "\n".join(parts)


def collect_execution_dataset(
    db_path: str | Path = DEFAULT_DB_PATH,
    catalog_path: str | Path = DEFAULT_CATALOG_PATH,
) -> pd.DataFrame:
    """Collect runtime and execution plan metadata for each catalog query."""
    query_entries = load_query_catalog(catalog_path)
    if not query_entries:
        raise FileNotFoundError(f"No queries found in catalog: {catalog_path}")

    conn = connect_to_database(db_path)
    try:
        records: list[dict[str, Any]] = []
        for entry in query_entries:
            query_id = str(entry["query_id"])
            query_text = str(entry["sql_query"])

            runtime = measure_runtime(conn, query_text)
            explain_plan = _explain_text(conn, query_text, analyze=False)
            explain_analyze_plan = _explain_text(conn, query_text, analyze=True)

            execution_plan = (
                "[EXPLAIN]\n"
                f"{explain_plan}\n"
                "\n[EXPLAIN ANALYZE]\n"
                f"{explain_analyze_plan}"
            )

            records.append(
                {
                    "query_id": query_id,
                    "query_text": query_text,
                    "runtime": runtime,
                    "execution_plan": execution_plan,
                }
            )

        return pd.DataFrame(records)
    finally:
        conn.close()


def run_workload(
    db_path: str | Path = DEFAULT_DB_PATH,
    catalog_path: str | Path = DEFAULT_CATALOG_PATH,
    runs_per_query: int = 40,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Run catalog queries repeatedly with randomized execution order per run."""
    if runs_per_query < 1:
        raise ValueError("runs_per_query must be >= 1")

    query_entries = load_query_catalog(catalog_path)
    if not query_entries:
        raise FileNotFoundError(f"No queries found in catalog: {catalog_path}")

    rng = random.Random(random_seed)
    conn = connect_to_database(db_path)
    try:
        records: list[dict[str, Any]] = []
        for run_number in range(1, runs_per_query + 1):
            shuffled_entries = list(query_entries)
            rng.shuffle(shuffled_entries)

            for entry in shuffled_entries:
                query_id = str(entry["query_id"])
                category = str(entry["category"])
                tables_used = entry["tables_used"]
                sql_query = str(entry["sql_query"])

                execution_time = measure_runtime(conn, sql_query)
                records.append(
                    {
                        "query_id": query_id,
                        "run_number": run_number,
                        "execution_time": execution_time,
                        "query_category": category,
                        "tables_used": _tables_used_to_string(tables_used),
                    }
                )

        return pd.DataFrame(records)
    finally:
        conn.close()


def save_runtime_logs(runtime_logs_df: pd.DataFrame, output_path: str | Path = DEFAULT_OUTPUT_PATH) -> Path:
    """Persist runtime logs as CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    runtime_logs_df.to_csv(path, index=False)
    return path


def save_execution_dataset(
    execution_df: pd.DataFrame,
    output_path: str | Path = DEFAULT_EXECUTION_DATASET_PATH,
) -> Path:
    """Persist execution-plan dataset as CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    execution_df.to_csv(path, index=False)
    return path


def print_workload_summary(runtime_logs_df: pd.DataFrame, runs_per_query: int) -> None:
    """Print aggregate workload execution statistics."""
    total_queries = int(runtime_logs_df["query_id"].nunique())
    total_executions = int(len(runtime_logs_df))
    runtimes = runtime_logs_df["execution_time"].tolist()

    print("Workload Summary")
    print(f"- total queries: {total_queries}")
    print(f"- runs per query: {runs_per_query}")
    print(f"- total executions: {total_executions}")
    print("Runtime Statistics (seconds)")
    print(f"- min: {min(runtimes):.6f}")
    print(f"- max: {max(runtimes):.6f}")
    print(f"- mean: {mean(runtimes):.6f}")
    print(f"- median: {median(runtimes):.6f}")


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser for workload execution."""
    parser = argparse.ArgumentParser(description="Run catalog SQL workload and save runtime logs.")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="Path to DuckDB database file.")
    parser.add_argument(
        "--catalog-path",
        default=str(DEFAULT_CATALOG_PATH),
        help="Path to query_catalog.json",
    )
    parser.add_argument("--runs", type=int, default=40, help="Number of runs per query.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for per-run query shuffling.")
    parser.add_argument(
        "--output-path",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Output CSV path for runtime logs.",
    )
    parser.add_argument(
        "--collect-plans",
        action="store_true",
        help="Collect EXPLAIN/EXPLAIN ANALYZE plans and write query execution dataset.",
    )
    parser.add_argument(
        "--execution-output-path",
        default=str(DEFAULT_EXECUTION_DATASET_PATH),
        help="Output CSV path for query execution dataset.",
    )
    return parser


def main() -> None:
    """CLI entrypoint for automated workload execution."""
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.collect_plans:
        execution_df = collect_execution_dataset(
            db_path=args.db_path,
            catalog_path=args.catalog_path,
        )
        output_path = save_execution_dataset(execution_df, output_path=args.execution_output_path)
        print(f"Saved query execution dataset to: {output_path}")
        print(f"Rows: {len(execution_df)}")
        print(f"Unique queries: {execution_df['query_id'].nunique()}")
        return

    runtime_logs_df = run_workload(
        db_path=args.db_path,
        catalog_path=args.catalog_path,
        runs_per_query=args.runs,
        random_seed=args.seed,
    )
    output_path = save_runtime_logs(runtime_logs_df, output_path=args.output_path)

    print(f"Saved runtime logs to: {output_path}")
    print_workload_summary(runtime_logs_df, runs_per_query=args.runs)


if __name__ == "__main__":
    main()

