from __future__ import annotations

from pathlib import Path

import pandas as pd

from features.feature_extractor import extract_structural_features


def build_dataset_from_logs(
	runtime_log_path: str | Path,
	output_path: str | Path = Path("data") / "features_dataset.csv",
) -> pd.DataFrame:
	"""Build a feature dataset from runtime logs that include SQL text."""
	runtime_df = pd.read_csv(runtime_log_path)

	if "query_text" not in runtime_df.columns:
		raise ValueError("Input runtime log must contain a 'query_text' column.")

	features = runtime_df["query_text"].apply(extract_structural_features)
	features_df = pd.DataFrame(features.tolist())
	dataset = pd.concat([runtime_df.reset_index(drop=True), features_df], axis=1)

	output = Path(output_path)
	output.parent.mkdir(parents=True, exist_ok=True)
	dataset.to_csv(output, index=False)
	return dataset
