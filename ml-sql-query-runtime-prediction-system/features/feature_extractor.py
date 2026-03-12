from __future__ import annotations

from typing import Any

import pandas as pd
import sqlglot
from sqlglot import expressions as exp


def extract_structural_features(query_text: str) -> dict[str, Any]:
	"""Extract basic structural SQL features from a query string."""
	tree = sqlglot.parse_one(query_text)

	table_count = len(list(tree.find_all(exp.Table)))
	join_count = len(list(tree.find_all(exp.Join)))
	where_clauses = list(tree.find_all(exp.Where))
	filter_count = sum(len(list(where.find_all(exp.Predicate))) for where in where_clauses)
	aggregation_count = len(list(tree.find_all(exp.AggFunc)))
	group_by_present = int(tree.find(exp.Group) is not None)
	order_by_present = int(tree.find(exp.Order) is not None)
	subquery_count = len(list(tree.find_all(exp.Subquery)))

	return {
		"number_of_tables": table_count,
		"number_of_joins": join_count,
		"number_of_filters": filter_count,
		"aggregation_count": aggregation_count,
		"group_by_present": group_by_present,
		"order_by_present": order_by_present,
		"subquery_depth": subquery_count,
	}


def extract_features_dataframe(queries: list[str]) -> pd.DataFrame:
	"""Convert a list of SQL queries into a feature DataFrame."""
	rows = [extract_structural_features(query) for query in queries]
	return pd.DataFrame(rows)
