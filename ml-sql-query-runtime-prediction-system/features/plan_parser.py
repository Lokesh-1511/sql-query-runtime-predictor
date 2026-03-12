"""Execution Plan Feature Extraction

Parses DuckDB EXPLAIN/EXPLAIN ANALYZE text output to extract execution metrics:
- estimated_cost
- rows_scanned
- scan_count
- join_count
- operator_count
- index_usage
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_EXECUTION_PATH = Path(__file__).parent.parent / "data" / "query_execution_dataset.csv"


def parse_explain_plan(plan_text: str) -> dict[str, Any]:
    """
    Extract metrics from EXPLAIN text output.
    
    Returns dict with keys:
    - estimated_cost
    - rows_scanned
    - operator_count
    - scan_count
    - join_count
    - index_usage
    """
    metrics = {
        "estimated_cost": 0.0,
        "rows_scanned": 0,
        "operator_count": 0,
        "scan_count": 0,
        "join_count": 0,
        "index_usage": 0,
    }
    
    if not plan_text:
        return metrics
    
    # Count operators (lines that start with common DuckDB operators)
    operator_pattern = r"^\s*(Seq|Index|Hash|Sort|Aggregate|Window|Filter|Project|Cross|Inner|Left|Right|Full|Natural)\s*"
    metrics["operator_count"] = len(re.findall(operator_pattern, plan_text, re.MULTILINE))
    
    # Count sequential scans (table reads)
    scan_pattern = r"Seq\s+Scan|Table\s+Scan|Scan"
    metrics["scan_count"] = len(re.findall(scan_pattern, plan_text, re.IGNORECASE))
    
    # Count join operations
    join_pattern = r"Hash\s+Join|Nested\s+Loop|Merge\s+Join|Cross\s+Product|Inner\s+Join|Left\s+Join|Right\s+Join"
    metrics["join_count"] = len(re.findall(join_pattern, plan_text, re.IGNORECASE))
    
    # Check for index usage (DuckDB doesn't always use explicit indices but check for references)
    if "Index" in plan_text or "index" in plan_text.lower():
        metrics["index_usage"] = 1
    
    # Try to extract estimated cost (format varies by DuckDB version)
    cost_pattern = r"Cost:\s*([\d.]+)|estimated_cost:\s*([\d.]+)|cost\s*=\s*([\d.]+)"
    cost_match = re.search(cost_pattern, plan_text, re.IGNORECASE)
    if cost_match:
        # Extract from first non-None group
        cost_value = next((g for g in cost_match.groups() if g is not None), None)
        if cost_value:
            metrics["estimated_cost"] = float(cost_value)
    
    # Try to extract rows (format varies)
    rows_pattern = r"Rows:\s*(\d+)|rows:\s*(\d+)|rows\s*=\s*(\d+)"
    rows_match = re.search(rows_pattern, plan_text, re.IGNORECASE)
    if rows_match:
        rows_value = next((g for g in rows_match.groups() if g is not None), None)
        if rows_value:
            metrics["rows_scanned"] = int(rows_value)
    
    return metrics


def extract_plan_features(plan_text: str) -> dict[str, Any]:
    """
    Extract both EXPLAIN and EXPLAIN ANALYZE sections and combine metrics.
    
    Expected format in plan_text:
    [EXPLAIN]
    <EXPLAIN output>
    
    [EXPLAIN ANALYZE]
    <EXPLAIN ANALYZE output>
    """
    result = {
        "estimated_cost": 0.0,
        "rows_scanned": 0,
        "operator_count": 0,
        "scan_count": 0,
        "join_count": 0,
        "index_usage": 0,
    }
    
    if not plan_text:
        return result
    
    # Split by section markers
    sections = plan_text.split("[EXPLAIN ANALYZE]")
    
    # Parse EXPLAIN section (first part)
    if sections[0]:
        explain_text = sections[0].replace("[EXPLAIN]", "").strip()
        explain_metrics = parse_explain_plan(explain_text)
        # Keep explain metrics as baseline
        result.update(explain_metrics)
    
    # Parse EXPLAIN ANALYZE section if available (more accurate)
    if len(sections) > 1 and sections[1]:
        analyze_metrics = parse_explain_plan(sections[1].strip())
        if analyze_metrics["rows_scanned"] > 0:
            result["rows_scanned"] = analyze_metrics["rows_scanned"]
        if analyze_metrics["estimated_cost"] > 0:
            result["estimated_cost"] = analyze_metrics["estimated_cost"]
        # Use higher operator counts
        result["operator_count"] = max(result["operator_count"], analyze_metrics["operator_count"])
        result["scan_count"] = max(result["scan_count"], analyze_metrics["scan_count"])
        result["join_count"] = max(result["join_count"], analyze_metrics["join_count"])
        if analyze_metrics["index_usage"] > 0:
            result["index_usage"] = analyze_metrics["index_usage"]
    
    return result


def extract_plan_metrics_100(
    execution_path: Path = DEFAULT_EXECUTION_PATH,
) -> pd.DataFrame:
    """
    Load execution dataset (100 rows) and extract plan metrics for each query.
    Returns 100-row DataFrame with query_id and plan metrics.
    """
    execution_df = pd.read_csv(execution_path)
    
    # Extract plan metrics for each query
    plan_metrics_list = []
    for _, row in execution_df.iterrows():
        plan_text = row["execution_plan"]
        metrics = extract_plan_features(plan_text)
        metrics["query_id"] = row["query_id"]
        plan_metrics_list.append(metrics)
    
    plan_metrics_df = pd.DataFrame(plan_metrics_list)
    
    # Keep only query_id and plan metrics columns
    return plan_metrics_df[["query_id", "estimated_cost", "rows_scanned", "operator_count", "scan_count", "join_count", "index_usage"]]
