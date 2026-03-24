from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import sqlglot
from sqlglot import expressions as exp
from sqlglot.tokens import Tokenizer

DEFAULT_FEATURES_PATH = Path(__file__).parent.parent / "data" / "features_dataset.csv"
DEFAULT_EXECUTION_PATH = Path(__file__).parent.parent / "data" / "query_execution_dataset.csv"
TOKENIZER = Tokenizer()


def _compute_subquery_depth(tree: exp.Expression) -> int:
    """Return the maximum nested subquery depth (0 when no subquery exists)."""
    max_depth = 0
    for subquery in tree.find_all(exp.Subquery):
        depth = 1
        parent = subquery.parent
        while parent is not None:
            if isinstance(parent, exp.Subquery):
                depth += 1
            parent = parent.parent
        max_depth = max(max_depth, depth)
    return max_depth


def extract_structural_features(query_text: str) -> dict[str, Any]:
    """Extract structural and textual SQL features from a query string."""
    normalized_query = query_text.strip()
    tree = sqlglot.parse_one(normalized_query)
    tokens = TOKENIZER.tokenize(normalized_query)

    table_count = len({table.name for table in tree.find_all(exp.Table) if table.name})
    join_count = len(list(tree.find_all(exp.Join)))
    where_clauses = list(tree.find_all(exp.Where))
    filter_count = sum(len(list(where.find_all(exp.Predicate))) for where in where_clauses)
    aggregation_count = len(list(tree.find_all(exp.AggFunc)))
    group_by_present = int(tree.find(exp.Group) is not None)
    order_by_present = int(tree.find(exp.Order) is not None)
    subquery_depth = _compute_subquery_depth(tree)

    return {
        "number_of_tables": table_count,
        "number_of_joins": join_count,
        "number_of_filters": filter_count,
        "aggregation_count": aggregation_count,
        "group_by_present": group_by_present,
        "order_by_present": order_by_present,
        "subquery_depth": subquery_depth,
        "query_length": len(normalized_query),
        "token_count": len(tokens),
    }


def extract_features_dataframe(queries: list[str]) -> pd.DataFrame:
    """Convert a list of SQL queries into a feature DataFrame."""
    rows = [extract_structural_features(query) for query in queries]
    return pd.DataFrame(rows)


def process_execution_dataset(
    execution_path: Path = DEFAULT_EXECUTION_PATH,
) -> pd.DataFrame:
    """Load execution dataset and extract structural features for each query."""
    execution_df = pd.read_csv(execution_path)

    features_list = []
    for _, row in execution_df.iterrows():
        query_text = row["query_text"]
        structural_features = extract_structural_features(query_text)
        combined = {
            "query_id": row["query_id"],
            "runtime": row["runtime"],
            **structural_features,
        }
        features_list.append(combined)

    return pd.DataFrame(features_list)


def save_features_dataset(
    features_df: pd.DataFrame,
    output_path: Path = DEFAULT_FEATURES_PATH,
) -> Path:
    """Save features DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(output_path, index=False)
    return output_path
