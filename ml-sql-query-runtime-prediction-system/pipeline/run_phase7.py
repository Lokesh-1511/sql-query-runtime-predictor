"""Phase 7: Execution Plan Feature Extraction.

Parse EXPLAIN / EXPLAIN ANALYZE text into per-query numeric plan metrics.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from features.plan_parser import extract_plan_metrics_100


def main():
    """Run Phase 7: Extract execution plan features for all catalog queries."""
    print("Phase 7: Execution Plan Feature Extraction")
    print("=" * 60)

    try:
        print("\nExtracting plan metrics from execution dataset...")
        plan_df = extract_plan_metrics_100()

        print(f"✓ Extracted metrics for {len(plan_df)} queries")
        print(f"✓ Columns: {list(plan_df.columns)}")

        print("\nPlan feature statistics:")
        print(plan_df.describe())

        output_path = Path("data") / "plan_metrics_100.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plan_df.to_csv(output_path, index=False)
        print(f"\n✓ Saved to {output_path}")

        total_queries = len(plan_df)
        print("\nPlan metrics breakdown:")
        print(f"  - Queries with joins: {(plan_df['join_count'] > 0).sum()} / {total_queries}")
        print(f"  - Queries with scans: {(plan_df['scan_count'] > 0).sum()} / {total_queries}")
        print(f"  - Queries with hash joins: {(plan_df['hash_join_count'] > 0).sum()} / {total_queries}")
        print(f"  - Queries with filter operators: {(plan_df['filter_operator_count'] > 0).sum()} / {total_queries}")
        print(f"  - Queries with projections: {(plan_df['projection_count'] > 0).sum()} / {total_queries}")
        print(f"  - Queries with aggregate operators: {(plan_df['aggregate_operator_count'] > 0).sum()} / {total_queries}")
        print(f"  - Avg operators per query: {plan_df['operator_count'].mean():.2f}")
        print(f"  - Avg scans per query: {plan_df['scan_count'].mean():.2f}")
        print(f"  - Avg joins per query: {plan_df['join_count'].mean():.2f}")

        print("\n" + "=" * 60)
        print("Phase 7 completed successfully!")
        print("\nNext step: Phase 8 will merge plan metrics with expanded features")
        return 0

    except Exception as e:
        print(f"\n✗ Error during Phase 7: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
