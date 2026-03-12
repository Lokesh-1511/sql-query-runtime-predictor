from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


DEFAULT_DB_PATH = Path("data") / "tpch.db"
REQUIRED_TPCH_TABLES = [
    "customer",
    "orders",
    "lineitem",
    "nation",
    "region",
    "supplier",
    "part",
    "partsupp",
]


def connect_to_database(db_path: str | Path = DEFAULT_DB_PATH) -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection and ensure parent directories exist."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))


def install_and_load_tpch_extension(conn: duckdb.DuckDBPyConnection) -> None:
    """Install and load DuckDB TPC-H extension."""
    conn.execute("INSTALL tpch;")
    conn.execute("LOAD tpch;")


def list_tables(conn: duckdb.DuckDBPyConnection) -> list[str]:
    """Return all base tables in the main schema."""
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'main' AND table_type = 'BASE TABLE'
    ORDER BY table_name;
    """
    rows = conn.execute(query).fetchall()
    return [row[0] for row in rows]


def tpch_tables_exist(conn: duckdb.DuckDBPyConnection) -> bool:
    """Check whether all required TPC-H benchmark tables are present."""
    current_tables = set(list_tables(conn))
    return set(REQUIRED_TPCH_TABLES).issubset(current_tables)


def generate_tpch_data(conn: duckdb.DuckDBPyConnection, scale_factor: int = 1) -> None:
    """Generate TPC-H tables for the provided scale factor."""
    conn.execute(f"CALL dbgen(sf={scale_factor});")


def get_table_row_counts(conn: duckdb.DuckDBPyConnection, table_names: list[str]) -> pd.DataFrame:
    """Return row counts for the provided table names."""
    counts = []
    for table_name in table_names:
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
        counts.append({"table_name": table_name, "row_count": int(row_count)})
    return pd.DataFrame(counts)


def setup_tpch_database(
    db_path: str | Path = DEFAULT_DB_PATH,
    scale_factor: int = 1,
) -> pd.DataFrame:
    """Prepare DuckDB with TPC-H data and return required table row counts."""
    conn = connect_to_database(db_path)
    try:
        install_and_load_tpch_extension(conn)
        if not tpch_tables_exist(conn):
            generate_tpch_data(conn, scale_factor=scale_factor)

        row_counts_df = get_table_row_counts(conn, REQUIRED_TPCH_TABLES)
        return row_counts_df
    finally:
        conn.close()


def main() -> None:
    """Run setup and print generated table metadata."""
    db_path = DEFAULT_DB_PATH
    row_counts_df = setup_tpch_database(db_path=db_path, scale_factor=1)

    print(f"Database ready: {db_path}")
    print("Tables:")
    print("\n".join(REQUIRED_TPCH_TABLES))
    print("\nRow counts:")
    print(row_counts_df.to_string(index=False))


if __name__ == "__main__":
    main()
