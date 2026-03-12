from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

import duckdb

try:
    from runner.query_loader import save_query_catalog
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from runner.query_loader import save_query_catalog


DEFAULT_DB_PATH = Path("data") / "tpch.db"
DEFAULT_QUERIES_DIR = Path("queries")
DEFAULT_TARGET_QUERY_COUNT = 100
MAX_TARGET_QUERY_COUNT = 200

CATEGORY_ORDER = [
    "single_table",
    "join_query",
    "aggregation_query",
    "group_by_query",
    "filter_query",
    "analytical_query",
]

# Balanced target profile (for 100 queries this maps to: 22, 32, 12, 12, 11, 11)
CATEGORY_WEIGHTS = {
    "single_table": 22,
    "join_query": 32,
    "aggregation_query": 12,
    "group_by_query": 12,
    "filter_query": 11,
    "analytical_query": 11,
}

CATEGORY_MIN_RATIO = {
    "single_table": 0.20,
    "join_query": 0.30,
    "aggregation_query": 0.10,
    "group_by_query": 0.10,
    "filter_query": 0.10,
    "analytical_query": 0.10,
}

CATEGORY_MAX_RATIO = {
    "single_table": 0.25,
    "join_query": 0.35,
    "aggregation_query": 0.15,
    "group_by_query": 0.15,
    "filter_query": 0.15,
    "analytical_query": 0.15,
}


def normalize_sql(sql: str) -> str:
    """Normalize SQL for stable deduplication checks."""
    return " ".join(sql.strip().split())


def make_query(
    query_id: str,
    category: str,
    tables_used: list[str],
    complexity_level: str,
    sql_query: str,
) -> dict[str, Any]:
    """Create a catalog query record."""
    return {
        "query_id": query_id,
        "category": category,
        "tables_used": tables_used,
        "complexity_level": complexity_level,
        "sql_query": sql_query.strip(),
    }


def curated_base_queries() -> list[dict[str, Any]]:
    """Return a curated starter set across required categories."""
    entries: list[dict[str, Any]] = []

    entries.append(
        make_query(
            "b001",
            "single_table",
            ["orders"],
            "low",
            """
            SELECT o_orderkey, o_orderdate, o_totalprice
            FROM orders
            WHERE o_totalprice > 250000
            ORDER BY o_totalprice DESC
            LIMIT 100
            """,
        )
    )
    entries.append(
        make_query(
            "b002",
            "single_table",
            ["lineitem"],
            "low",
            """
            SELECT l_orderkey, l_partkey, l_quantity, l_extendedprice
            FROM lineitem
            WHERE l_shipdate >= DATE '1997-01-01'
            ORDER BY l_extendedprice DESC
            LIMIT 100
            """,
        )
    )
    entries.append(
        make_query(
            "b003",
            "filter_query",
            ["customer"],
            "low",
            """
            SELECT c_custkey, c_name, c_mktsegment, c_acctbal
            FROM customer
            WHERE c_mktsegment IN ('BUILDING', 'AUTOMOBILE') AND c_acctbal > 1000
            ORDER BY c_acctbal DESC
            LIMIT 100
            """,
        )
    )
    entries.append(
        make_query(
            "b004",
            "join_query",
            ["customer", "orders"],
            "medium",
            """
            SELECT c.c_custkey, c.c_name, o.o_orderkey, o.o_orderdate, o.o_totalprice
            FROM customer c
            JOIN orders o ON c.c_custkey = o.o_custkey
            WHERE o.o_orderdate BETWEEN DATE '1995-01-01' AND DATE '1995-12-31'
            ORDER BY o.o_totalprice DESC
            LIMIT 100
            """,
        )
    )
    entries.append(
        make_query(
            "b005",
            "join_query",
            ["orders", "lineitem"],
            "medium",
            """
            SELECT o.o_orderkey, o.o_orderpriority, l.l_linenumber, l.l_extendedprice
            FROM orders o
            JOIN lineitem l ON o.o_orderkey = l.l_orderkey
            WHERE l.l_discount > 0.05
            ORDER BY l.l_extendedprice DESC
            LIMIT 100
            """,
        )
    )
    entries.append(
        make_query(
            "b006",
            "aggregation_query",
            ["lineitem"],
            "low",
            """
            SELECT
                AVG(l_quantity) AS avg_qty,
                AVG(l_discount) AS avg_discount,
                SUM(l_extendedprice) AS total_extendedprice
            FROM lineitem
            WHERE l_shipdate BETWEEN DATE '1994-01-01' AND DATE '1996-12-31'
            """,
        )
    )
    entries.append(
        make_query(
            "b007",
            "group_by_query",
            ["orders"],
            "low",
            """
            SELECT o_orderpriority, COUNT(*) AS order_count
            FROM orders
            GROUP BY o_orderpriority
            ORDER BY order_count DESC
            """,
        )
    )
    entries.append(
        make_query(
            "b008",
            "analytical_query",
            ["orders"],
            "medium",
            """
            SELECT *
            FROM (
                SELECT
                    o_orderkey,
                    o_custkey,
                    o_totalprice,
                    ROW_NUMBER() OVER (PARTITION BY o_custkey ORDER BY o_totalprice DESC) AS rn
                FROM orders
            ) ranked
            WHERE rn <= 3
            LIMIT 200
            """,
        )
    )
    entries.append(
        make_query(
            "b009",
            "join_query",
            ["supplier", "nation", "region"],
            "medium",
            """
            SELECT s.s_suppkey, s.s_name, n.n_name, r.r_name
            FROM supplier s
            JOIN nation n ON s.s_nationkey = n.n_nationkey
            JOIN region r ON n.n_regionkey = r.r_regionkey
            WHERE r.r_name IN ('ASIA', 'EUROPE')
            ORDER BY s.s_acctbal DESC
            LIMIT 100
            """,
        )
    )
    entries.append(
        make_query(
            "b010",
            "join_query",
            ["part", "partsupp", "supplier"],
            "medium",
            """
            SELECT p.p_partkey, p.p_name, ps.ps_supplycost, s.s_name
            FROM part p
            JOIN partsupp ps ON p.p_partkey = ps.ps_partkey
            JOIN supplier s ON ps.ps_suppkey = s.s_suppkey
            WHERE p.p_size BETWEEN 5 AND 20
            ORDER BY ps.ps_supplycost DESC
            LIMIT 100
            """,
        )
    )

    # Add additional reliable base queries with varying filters/windows.
    dates = ["1993-01-01", "1994-01-01", "1995-01-01", "1996-01-01", "1997-01-01"]
    for idx, dt in enumerate(dates, start=11):
        entries.append(
            make_query(
                f"b{idx:03d}",
                "filter_query",
                ["orders"],
                "low",
                f"""
                SELECT o_orderkey, o_custkey, o_totalprice, o_orderdate
                FROM orders
                WHERE o_orderdate >= DATE '{dt}' AND o_totalprice > {100000 + idx * 5000}
                ORDER BY o_totalprice DESC
                LIMIT 80
                """,
            )
        )

    group_dims = ["l_returnflag", "l_linestatus", "l_shipmode", "l_shipinstruct"]
    for offset, dim in enumerate(group_dims, start=16):
        entries.append(
            make_query(
                f"b{offset:03d}",
                "group_by_query",
                ["lineitem"],
                "low",
                f"""
                SELECT {dim}, COUNT(*) AS cnt, SUM(l_extendedprice) AS total_price
                FROM lineitem
                GROUP BY {dim}
                ORDER BY total_price DESC
                """,
            )
        )

    analytical_offsets = [20, 21, 22, 23, 24]
    for i, month in zip(analytical_offsets, [1, 3, 5, 7, 9]):
        entries.append(
            make_query(
                f"b{i:03d}",
                "analytical_query",
                ["lineitem"],
                "medium",
                f"""
                SELECT *
                FROM (
                    SELECT
                        l_partkey,
                        l_shipdate,
                        l_extendedprice,
                        AVG(l_extendedprice) OVER (
                            PARTITION BY l_partkey
                            ORDER BY l_shipdate
                            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
                        ) AS moving_avg_price
                    FROM lineitem
                    WHERE EXTRACT(MONTH FROM l_shipdate) = {month}
                ) t
                LIMIT 120
                """,
            )
        )

    return entries


def generated_query_candidates() -> list[dict[str, Any]]:
    """Generate large candidate set across categories for validation."""
    entries: list[dict[str, Any]] = []
    idx = 1

    # Single table queries
    single_specs = [
        ("customer", "c_custkey, c_name, c_acctbal", "c_acctbal > {x}", "c_acctbal DESC"),
        ("orders", "o_orderkey, o_custkey, o_totalprice, o_orderdate", "o_totalprice > {x}", "o_totalprice DESC"),
        ("lineitem", "l_orderkey, l_partkey, l_quantity, l_extendedprice", "l_quantity > {x}", "l_extendedprice DESC"),
        ("supplier", "s_suppkey, s_name, s_acctbal", "s_acctbal > {x}", "s_acctbal DESC"),
        ("part", "p_partkey, p_name, p_retailprice", "p_retailprice > {x}", "p_retailprice DESC"),
        ("partsupp", "ps_partkey, ps_suppkey, ps_supplycost, ps_availqty", "ps_availqty > {x}", "ps_supplycost DESC"),
    ]
    thresholds = [10, 50, 100, 500, 1000, 5000, 10000]
    for table, cols, pred, order_by in single_specs:
        for t in thresholds:
            entries.append(
                make_query(
                    f"g{idx:03d}",
                    "single_table",
                    [table],
                    "low",
                    f"""
                    SELECT {cols}
                    FROM {table}
                    WHERE {pred.format(x=t)}
                    ORDER BY {order_by}
                    LIMIT 100
                    """,
                )
            )
            idx += 1

    # Join queries (2-4 tables)
    join_templates = [
        (
            ["customer", "orders"],
            "medium",
            """
            SELECT c.c_custkey, c.c_name, o.o_orderkey, o.o_totalprice
            FROM customer c
            JOIN orders o ON c.c_custkey = o.o_custkey
            WHERE o.o_totalprice > {threshold}
            ORDER BY o.o_totalprice DESC
            LIMIT 120
            """,
        ),
        (
            ["orders", "lineitem"],
            "medium",
            """
            SELECT o.o_orderkey, o.o_orderdate, l.l_partkey, l.l_extendedprice
            FROM orders o
            JOIN lineitem l ON o.o_orderkey = l.l_orderkey
            WHERE l.l_discount > {threshold}
            ORDER BY l.l_extendedprice DESC
            LIMIT 120
            """,
        ),
        (
            ["part", "partsupp", "supplier"],
            "medium",
            """
            SELECT p.p_partkey, p.p_name, ps.ps_supplycost, s.s_name
            FROM part p
            JOIN partsupp ps ON p.p_partkey = ps.ps_partkey
            JOIN supplier s ON ps.ps_suppkey = s.s_suppkey
            WHERE ps.ps_supplycost > {threshold}
            ORDER BY ps.ps_supplycost DESC
            LIMIT 120
            """,
        ),
        (
            ["supplier", "nation", "region"],
            "medium",
            """
            SELECT s.s_name, n.n_name, r.r_name, s.s_acctbal
            FROM supplier s
            JOIN nation n ON s.s_nationkey = n.n_nationkey
            JOIN region r ON n.n_regionkey = r.r_regionkey
            WHERE s.s_acctbal > {threshold}
            ORDER BY s.s_acctbal DESC
            LIMIT 120
            """,
        ),
        (
            ["customer", "orders", "lineitem", "part"],
            "high",
            """
            SELECT c.c_name, o.o_orderkey, p.p_name, l.l_extendedprice
            FROM customer c
            JOIN orders o ON c.c_custkey = o.o_custkey
            JOIN lineitem l ON o.o_orderkey = l.l_orderkey
            JOIN part p ON l.l_partkey = p.p_partkey
            WHERE l.l_extendedprice > {threshold}
            ORDER BY l.l_extendedprice DESC
            LIMIT 120
            """,
        ),
    ]
    join_thresholds = [0.01, 0.03, 0.05, 0.07, 1000, 5000, 10000, 25000, 50000, 100000]
    for tables, complexity, template in join_templates:
        for threshold in join_thresholds:
            entries.append(
                make_query(
                    f"g{idx:03d}",
                    "join_query",
                    tables,
                    complexity,
                    template.format(threshold=threshold),
                )
            )
            idx += 1

    extra_join_templates = [
        (
            ["customer", "orders", "lineitem"],
            "high",
            """
            SELECT c.c_custkey, o.o_orderkey, l.l_linenumber, l.l_extendedprice
            FROM customer c
            JOIN orders o ON c.c_custkey = o.o_custkey
            JOIN lineitem l ON o.o_orderkey = l.l_orderkey
            WHERE o.o_totalprice > {threshold}
            ORDER BY l.l_extendedprice DESC
            LIMIT 120
            """,
        ),
        (
            ["nation", "supplier", "partsupp"],
            "medium",
            """
            SELECT n.n_name, s.s_name, ps.ps_partkey, ps.ps_supplycost
            FROM nation n
            JOIN supplier s ON n.n_nationkey = s.s_nationkey
            JOIN partsupp ps ON s.s_suppkey = ps.ps_suppkey
            WHERE ps.ps_supplycost > {threshold}
            ORDER BY ps.ps_supplycost DESC
            LIMIT 120
            """,
        ),
        (
            ["orders", "lineitem", "part"],
            "high",
            """
            SELECT o.o_orderkey, p.p_name, l.l_quantity, l.l_extendedprice
            FROM orders o
            JOIN lineitem l ON o.o_orderkey = l.l_orderkey
            JOIN part p ON l.l_partkey = p.p_partkey
            WHERE l.l_quantity > {threshold}
            ORDER BY l.l_extendedprice DESC
            LIMIT 120
            """,
        ),
    ]
    extra_join_thresholds = [1, 5, 10, 25, 50, 100, 500, 1000, 5000, 10000]
    for tables, complexity, template in extra_join_templates:
        for threshold in extra_join_thresholds:
            entries.append(
                make_query(
                    f"g{idx:03d}",
                    "join_query",
                    tables,
                    complexity,
                    template.format(threshold=threshold),
                )
            )
            idx += 1

    # Aggregation queries
    agg_templates = [
        (
            ["lineitem"],
            "low",
            """
            SELECT
                SUM(l_extendedprice) AS total_price,
                AVG(l_discount) AS avg_discount,
                SUM(l_quantity) AS total_qty
            FROM lineitem
            WHERE l_quantity > {threshold}
            """,
        ),
        (
            ["orders"],
            "low",
            """
            SELECT
                COUNT(*) AS order_count,
                AVG(o_totalprice) AS avg_price,
                MAX(o_totalprice) AS max_price
            FROM orders
            WHERE o_totalprice > {threshold}
            """,
        ),
        (
            ["partsupp"],
            "low",
            """
            SELECT
                COUNT(*) AS supplier_part_pairs,
                SUM(ps_availqty) AS total_avail,
                AVG(ps_supplycost) AS avg_supplycost
            FROM partsupp
            WHERE ps_supplycost > {threshold}
            """,
        ),
    ]
    agg_thresholds = [1, 5, 10, 20, 50, 100, 500, 1000]
    for tables, complexity, template in agg_templates:
        for threshold in agg_thresholds:
            entries.append(
                make_query(
                    f"g{idx:03d}",
                    "aggregation_query",
                    tables,
                    complexity,
                    template.format(threshold=threshold),
                )
            )
            idx += 1

    # Group-by queries
    group_templates = [
        (
            ["orders"],
            "low",
            """
            SELECT o_orderpriority, COUNT(*) AS cnt, AVG(o_totalprice) AS avg_price
            FROM orders
            WHERE o_totalprice > {threshold}
            GROUP BY o_orderpriority
            ORDER BY cnt DESC
            """,
        ),
        (
            ["lineitem"],
            "low",
            """
            SELECT l_shipmode, COUNT(*) AS cnt, SUM(l_extendedprice) AS revenue
            FROM lineitem
            WHERE l_discount > {threshold}
            GROUP BY l_shipmode
            ORDER BY revenue DESC
            """,
        ),
        (
            ["supplier", "nation"],
            "medium",
            """
            SELECT n.n_name, COUNT(*) AS supplier_count, AVG(s.s_acctbal) AS avg_balance
            FROM supplier s
            JOIN nation n ON s.s_nationkey = n.n_nationkey
            WHERE s.s_acctbal > {threshold}
            GROUP BY n.n_name
            ORDER BY supplier_count DESC
            """,
        ),
    ]
    group_thresholds = [0, 0.01, 0.03, 0.05, 1000, 5000, 10000, 20000]
    for tables, complexity, template in group_templates:
        for threshold in group_thresholds:
            entries.append(
                make_query(
                    f"g{idx:03d}",
                    "group_by_query",
                    tables,
                    complexity,
                    template.format(threshold=threshold),
                )
            )
            idx += 1

    # Filter queries
    filter_templates = [
        (
            ["customer"],
            "low",
            """
            SELECT c_custkey, c_name, c_phone, c_acctbal
            FROM customer
            WHERE c_acctbal BETWEEN {lo} AND {hi}
            ORDER BY c_acctbal DESC
            LIMIT 100
            """,
        ),
        (
            ["orders"],
            "low",
            """
            SELECT o_orderkey, o_orderpriority, o_orderstatus, o_totalprice
            FROM orders
            WHERE o_orderdate BETWEEN DATE '{start_date}' AND DATE '{end_date}'
            ORDER BY o_totalprice DESC
            LIMIT 100
            """,
        ),
        (
            ["part"],
            "low",
            """
            SELECT p_partkey, p_name, p_brand, p_size, p_retailprice
            FROM part
            WHERE p_size BETWEEN {lo} AND {hi}
            ORDER BY p_retailprice DESC
            LIMIT 100
            """,
        ),
    ]
    ranges = [(0, 500), (500, 2000), (2000, 5000), (5000, 10000), (10000, 20000)]
    date_ranges = [
        ("1993-01-01", "1993-12-31"),
        ("1994-01-01", "1994-12-31"),
        ("1995-01-01", "1995-12-31"),
        ("1996-01-01", "1996-12-31"),
        ("1997-01-01", "1997-12-31"),
    ]

    for lo, hi in ranges:
        entries.append(
            make_query(
                f"g{idx:03d}",
                "filter_query",
                ["customer"],
                "low",
                filter_templates[0][2].format(lo=lo, hi=hi),
            )
        )
        idx += 1

    for start_date, end_date in date_ranges:
        entries.append(
            make_query(
                f"g{idx:03d}",
                "filter_query",
                ["orders"],
                "low",
                filter_templates[1][2].format(start_date=start_date, end_date=end_date),
            )
        )
        idx += 1

    for lo, hi in [(1, 5), (6, 10), (11, 20), (21, 30), (31, 40), (41, 50)]:
        entries.append(
            make_query(
                f"g{idx:03d}",
                "filter_query",
                ["part"],
                "low",
                filter_templates[2][2].format(lo=lo, hi=hi),
            )
        )
        idx += 1

    # Analytical queries
    analytical_templates = [
        (
            ["orders"],
            "medium",
            """
            SELECT *
            FROM (
                SELECT
                    o_orderkey,
                    o_custkey,
                    o_totalprice,
                    DENSE_RANK() OVER (PARTITION BY o_orderpriority ORDER BY o_totalprice DESC) AS price_rank
                FROM orders
                WHERE o_totalprice > {threshold}
            ) t
            WHERE price_rank <= 5
            LIMIT 150
            """,
        ),
        (
            ["lineitem"],
            "medium",
            """
            SELECT *
            FROM (
                SELECT
                    l_orderkey,
                    l_partkey,
                    l_shipdate,
                    l_extendedprice,
                    AVG(l_extendedprice) OVER (
                        PARTITION BY l_partkey
                        ORDER BY l_shipdate
                        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
                    ) AS rolling_avg
                FROM lineitem
                WHERE l_discount > {threshold}
            ) t
            LIMIT 150
            """,
        ),
        (
            ["customer", "orders"],
            "high",
            """
            SELECT *
            FROM (
                SELECT
                    c.c_custkey,
                    c.c_name,
                    o.o_orderkey,
                    o.o_totalprice,
                    SUM(o.o_totalprice) OVER (
                        PARTITION BY c.c_custkey
                        ORDER BY o.o_orderdate
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) AS running_total
                FROM customer c
                JOIN orders o ON c.c_custkey = o.o_custkey
                WHERE o.o_totalprice > {threshold}
            ) t
            LIMIT 150
            """,
        ),
    ]
    analytical_thresholds = [0.01, 0.03, 0.05, 5000, 10000, 25000, 50000]
    for tables, complexity, template in analytical_templates:
        for threshold in analytical_thresholds:
            entries.append(
                make_query(
                    f"g{idx:03d}",
                    "analytical_query",
                    tables,
                    complexity,
                    template.format(threshold=threshold),
                )
            )
            idx += 1

    return entries


def validate_queries(
    conn: duckdb.DuckDBPyConnection,
    candidates: list[dict[str, Any]],
    target_count: int,
) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    """Validate candidates on DuckDB and return unique successful queries."""
    valid: list[dict[str, Any]] = []
    errors: list[tuple[str, str]] = []
    seen_sql: set[str] = set()

    for entry in candidates:
        sql_query = entry["sql_query"]
        sql_key = normalize_sql(sql_query)
        if sql_key in seen_sql:
            continue

        try:
            conn.execute(sql_query).fetchone()
            seen_sql.add(sql_key)
            valid.append(entry)
        except Exception as exc:
            errors.append((entry["query_id"], str(exc)))

    return valid, errors


def build_balanced_targets(target_count: int) -> dict[str, int]:
    """Build per-category targets following the recommended balanced workload ratios."""
    if target_count <= 0:
        raise ValueError("target_count must be > 0")

    total_weight = sum(CATEGORY_WEIGHTS.values())
    ideal = {
        category: (target_count * CATEGORY_WEIGHTS[category] / total_weight)
        for category in CATEGORY_ORDER
    }
    minimums = {
        category: math.floor(target_count * CATEGORY_MIN_RATIO[category])
        for category in CATEGORY_ORDER
    }
    maximums = {
        category: math.ceil(target_count * CATEGORY_MAX_RATIO[category])
        for category in CATEGORY_ORDER
    }

    targets = {
        category: min(max(round(ideal[category]), minimums[category]), maximums[category])
        for category in CATEGORY_ORDER
    }

    current_total = sum(targets.values())
    if current_total < target_count:
        deficit = target_count - current_total
        for category in sorted(CATEGORY_ORDER, key=lambda c: (ideal[c] - targets[c]), reverse=True):
            if deficit <= 0:
                break
            room = maximums[category] - targets[category]
            if room <= 0:
                continue
            add = min(room, deficit)
            targets[category] += add
            deficit -= add
    elif current_total > target_count:
        overflow = current_total - target_count
        for category in sorted(CATEGORY_ORDER, key=lambda c: (targets[c] - ideal[c]), reverse=True):
            if overflow <= 0:
                break
            room = targets[category] - minimums[category]
            if room <= 0:
                continue
            remove = min(room, overflow)
            targets[category] -= remove
            overflow -= remove

    if sum(targets.values()) != target_count:
        raise RuntimeError("Unable to resolve balanced category targets to requested query count.")
    return targets


def select_balanced_queries(
    valid_queries: list[dict[str, Any]],
    target_count: int,
) -> list[dict[str, Any]]:
    """Select a balanced subset of validated queries across categories."""
    targets = build_balanced_targets(target_count)
    grouped: dict[str, list[dict[str, Any]]] = {category: [] for category in CATEGORY_ORDER}

    for entry in valid_queries:
        category = str(entry["category"])
        if category in grouped:
            grouped[category].append(entry)

    for category in CATEGORY_ORDER:
        available = len(grouped[category])
        needed = targets[category]
        if available < needed:
            raise RuntimeError(
                f"Not enough validated queries for category '{category}'. needed={needed}, available={available}"
            )

    selected: list[dict[str, Any]] = []
    for category in CATEGORY_ORDER:
        selected.extend(grouped[category][: targets[category]])

    return selected


def write_query_sql_files(
    queries: list[dict[str, Any]],
    base_dir: Path,
    generated_dir: Path,
) -> None:
    """Write SQL files for easier browsing and debugging."""
    base_dir.mkdir(parents=True, exist_ok=True)
    generated_dir.mkdir(parents=True, exist_ok=True)

    # Clean previous generated files to avoid stale artifacts.
    for path in generated_dir.glob("*.sql"):
        path.unlink()
    for path in base_dir.glob("*.sql"):
        path.unlink()

    for entry in queries:
        query_id = entry["query_id"]
        sql_query = entry["sql_query"].strip() + "\n"
        if query_id.startswith("b"):
            out_path = base_dir / f"{query_id}.sql"
        else:
            out_path = generated_dir / f"{query_id}.sql"
        out_path.write_text(sql_query, encoding="utf-8")


def build_queries(
    db_path: str | Path = DEFAULT_DB_PATH,
    queries_dir: str | Path = DEFAULT_QUERIES_DIR,
    target_count: int = DEFAULT_TARGET_QUERY_COUNT,
) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    """Generate, validate, balance, and persist query catalog and SQL artifacts."""
    if target_count <= 0:
        raise ValueError("target_count must be greater than zero")
    if target_count > MAX_TARGET_QUERY_COUNT:
        raise ValueError(f"target_count must be <= {MAX_TARGET_QUERY_COUNT}")

    queries_root = Path(queries_dir)
    base_dir = queries_root / "base_queries"
    generated_dir = queries_root / "generated_queries"
    catalog_path = queries_root / "query_catalog.json"

    candidates = curated_base_queries() + generated_query_candidates()

    conn = duckdb.connect(str(db_path))
    try:
        valid_queries, errors = validate_queries(conn, candidates, target_count=target_count)
    finally:
        conn.close()

    if len(valid_queries) < target_count:
        raise RuntimeError(
            f"Unable to produce target query count. Requested={target_count}, valid={len(valid_queries)}"
        )

    selected_queries = select_balanced_queries(valid_queries, target_count=target_count)

    # Re-number query ids for stable contiguous catalog indexing.
    renumbered: list[dict[str, Any]] = []
    for i, entry in enumerate(selected_queries, start=1):
        new_entry = dict(entry)
        new_entry["query_id"] = f"q{i:03d}"
        # Keep catalog schema focused on requested fields.
        new_entry = {
            "query_id": new_entry["query_id"],
            "category": new_entry["category"],
            "tables_used": new_entry["tables_used"],
            "complexity_level": new_entry["complexity_level"],
            "sql_query": new_entry["sql_query"],
        }
        renumbered.append(new_entry)

    write_query_sql_files(selected_queries, base_dir=base_dir, generated_dir=generated_dir)
    save_query_catalog(renumbered, catalog_path=catalog_path)

    return renumbered, errors


def summarize_by_category(queries: list[dict[str, Any]]) -> dict[str, int]:
    """Return category distribution for generated catalog."""
    summary: dict[str, int] = {}
    for entry in queries:
        category = str(entry["category"])
        summary[category] = summary.get(category, 0) + 1
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI parser for query generation."""
    parser = argparse.ArgumentParser(description="Generate and validate catalog-based SQL workload.")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="Path to DuckDB database file")
    parser.add_argument("--queries-dir", default=str(DEFAULT_QUERIES_DIR), help="Queries root directory")
    parser.add_argument(
        "--target-count",
        type=int,
        default=DEFAULT_TARGET_QUERY_COUNT,
        help=f"Target query count (max {MAX_TARGET_QUERY_COUNT})",
    )
    return parser


def main() -> None:
    """CLI entrypoint for query generation and validation."""
    parser = build_arg_parser()
    args = parser.parse_args()

    valid_queries, errors = build_queries(
        db_path=args.db_path,
        queries_dir=args.queries_dir,
        target_count=args.target_count,
    )

    category_summary = summarize_by_category(valid_queries)

    print("Generated query catalog successfully.")
    print(f"Catalog path: {Path(args.queries_dir) / 'query_catalog.json'}")
    print(f"Total valid queries: {len(valid_queries)}")
    print("Category distribution:")
    for category, count in sorted(category_summary.items()):
        print(f"- {category}: {count}")
    print(f"Validation failures (discarded candidates): {len(errors)}")


if __name__ == "__main__":
    main()
