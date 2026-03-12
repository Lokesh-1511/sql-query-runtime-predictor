"""Execution Plan Feature Extraction.

Parse DuckDB EXPLAIN / EXPLAIN ANALYZE text into numeric plan features.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_EXECUTION_PATH = Path(__file__).parent.parent / "data" / "query_execution_dataset.csv"

PLAN_METRIC_COLUMNS = [
    "query_id",
    "estimated_cost",
    "rows_scanned",
    "operator_count",
    "scan_count",
    "join_count",
    "index_usage",
    "hash_join_count",
    "filter_operator_count",
    "projection_count",
    "aggregate_operator_count",
]

OPERATOR_PATTERNS = {
    "scan_count": r"\b(?:SEQ_SCAN|TABLE_SCAN)\b",
    "hash_join_count": r"\bHASH_JOIN\b",
    "filter_operator_count": r"\bFILTER\b",
    "projection_count": r"\bPROJECTION\b",
    "aggregate_operator_count": r"\b(?:UNGROUPED_AGGREGATE|HASH_GROUP_BY|PERFECT_HASH_GROUP_BY|AGGREGATE)\b",
}
JOIN_PATTERN = r"\b(?:HASH_JOIN|PIECEWISE_MERGE_JOIN|BLOCKWISE_NL_JOIN|NESTED_LOOP_JOIN)\b"
OPERATOR_PATTERN = (
    r"\b(?:SEQ_SCAN|TABLE_SCAN|HASH_JOIN|PIECEWISE_MERGE_JOIN|BLOCKWISE_NL_JOIN|"
    r"NESTED_LOOP_JOIN|FILTER|PROJECTION|UNGROUPED_AGGREGATE|HASH_GROUP_BY|"
    r"PERFECT_HASH_GROUP_BY|TOP_N|ORDER_BY|GROUP)\b"
)
ROW_PATTERNS = [
    r"Rows:\s*([\d,]+)",
    r"rows\s*=\s*([\d,]+)",
    r"~?([\d,]+)\s+rows\b",
]
COST_PATTERNS = [
    r"Cost:\s*([\d.]+)",
    r"estimated_cost:\s*([\d.]+)",
    r"cost\s*=\s*([\d.]+)",
]


def count_pattern(pattern: str, plan_text: str) -> int:
    """Count regex occurrences in plan text."""
    return len(re.findall(pattern, plan_text, flags=re.IGNORECASE))


def extract_max_numeric(patterns: list[str], plan_text: str, as_float: bool = False) -> float | int:
    """Extract the maximum numeric value matched by any of the supplied regex patterns."""
    values: list[float] = []
    for pattern in patterns:
        for match in re.findall(pattern, plan_text, flags=re.IGNORECASE):
            numeric = float(str(match).replace(",", ""))
            values.append(numeric)
    if not values:
        return 0.0 if as_float else 0
    maximum = max(values)
    return maximum if as_float else int(maximum)


def parse_explain_plan(plan_text: str) -> dict[str, Any]:
    """Extract DuckDB execution-plan metrics from one plan section."""
    metrics = {
        "estimated_cost": 0.0,
        "rows_scanned": 0,
        "operator_count": 0,
        "scan_count": 0,
        "join_count": 0,
        "index_usage": 0,
        "hash_join_count": 0,
        "filter_operator_count": 0,
        "projection_count": 0,
        "aggregate_operator_count": 0,
    }

    if not plan_text:
        return metrics

    metrics["operator_count"] = count_pattern(OPERATOR_PATTERN, plan_text)
    metrics["join_count"] = count_pattern(JOIN_PATTERN, plan_text)
    metrics["index_usage"] = int(bool(re.search(r"\bINDEX(?:_SCAN)?\b", plan_text, flags=re.IGNORECASE)))
    metrics["estimated_cost"] = float(extract_max_numeric(COST_PATTERNS, plan_text, as_float=True))
    metrics["rows_scanned"] = int(extract_max_numeric(ROW_PATTERNS, plan_text, as_float=False))

    for column, pattern in OPERATOR_PATTERNS.items():
        metrics[column] = count_pattern(pattern, plan_text)

    return metrics


def extract_plan_features(plan_text: str) -> dict[str, Any]:
    """Extract combined features from EXPLAIN and EXPLAIN ANALYZE sections."""
    result = {
        "estimated_cost": 0.0,
        "rows_scanned": 0,
        "operator_count": 0,
        "scan_count": 0,
        "join_count": 0,
        "index_usage": 0,
        "hash_join_count": 0,
        "filter_operator_count": 0,
        "projection_count": 0,
        "aggregate_operator_count": 0,
    }

    if not plan_text:
        return result

    sections = plan_text.split("[EXPLAIN ANALYZE]")
    explain_text = sections[0].replace("[EXPLAIN]", "").strip() if sections else ""
    analyze_text = sections[1].strip() if len(sections) > 1 else ""

    explain_metrics = parse_explain_plan(explain_text)
    analyze_metrics = parse_explain_plan(analyze_text)

    for key in result:
        if key == "estimated_cost":
            result[key] = max(explain_metrics[key], analyze_metrics[key])
        elif key == "index_usage":
            result[key] = max(explain_metrics[key], analyze_metrics[key])
        else:
            result[key] = max(int(explain_metrics[key]), int(analyze_metrics[key]))

    return result


def extract_plan_metrics_100(
    execution_path: Path = DEFAULT_EXECUTION_PATH,
) -> pd.DataFrame:
    """Load the execution dataset and extract per-query plan metrics."""
    execution_df = pd.read_csv(execution_path)

    plan_metrics_list = []
    for _, row in execution_df.iterrows():
        metrics = extract_plan_features(row["execution_plan"])
        metrics["query_id"] = row["query_id"]
        plan_metrics_list.append(metrics)

    plan_metrics_df = pd.DataFrame(plan_metrics_list)
    return plan_metrics_df[PLAN_METRIC_COLUMNS]
