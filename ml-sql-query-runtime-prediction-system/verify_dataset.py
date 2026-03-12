"""Verify final ML training dataset."""

import pandas as pd

df = pd.read_csv("data/ml_training_dataset.csv")

print('='*70)
print('FINAL ML TRAINING DATASET - VERIFICATION')
print('='*70)

print(f'\nShape: {df.shape}')
print(f'Rows: {len(df)} ({df["query_id"].nunique()} queries × {len(df) // df["query_id"].nunique()} runs)')
print(f'Columns: {len(df.columns)}')

print('\nColumn List:')
for i, col in enumerate(df.columns, 1):
    dtype = str(df[col].dtype)
    print(f'  {i:2d}. {col:25s} ({dtype})')

print('\nData Quality Checks:')
print(f'  ✓ Missing values: {df.isnull().sum().sum()}')
print(f'  ✓ Unique queries: {df["query_id"].nunique()}')
print(f'  ✓ Runs per query: {len(df) // df["query_id"].nunique()}')

print('\n' + '='*70)
print('TARGET VARIABLE: execution_time (seconds)')
print('='*70)
print(f'  Type: {df["execution_time"].dtype}')
print(f'  Count: {df["execution_time"].count()}')
print(f'  Min:    {df["execution_time"].min():.6f} s')
print(f'  Max:    {df["execution_time"].max():.6f} s')
print(f'  Mean:   {df["execution_time"].mean():.6f} s')
print(f'  Median: {df["execution_time"].median():.6f} s')
print(f'  Std:    {df["execution_time"].std():.6f} s')
print(f'  Q1:     {df["execution_time"].quantile(0.25):.6f} s')
print(f'  Q3:     {df["execution_time"].quantile(0.75):.6f} s')

print('\n' + '='*70)
print('FEATURES SUMMARY')
print('='*70)

# Metadata features
meta_cols = ['query_id', 'run_number', 'query_category', 'tables_used']
print(f'\nMetadata Features ({len(meta_cols)}):')
for col in meta_cols:
    print(f'  - {col}')

# Structural features
struct_cols = [
    'number_of_tables', 'number_of_joins', 'number_of_filters',
    'aggregation_count', 'group_by_present', 'order_by_present',
    'subquery_depth', 'query_length', 'token_count'
]
print(f'\nStructural Features ({len(struct_cols)}):')
for col in struct_cols:
    print(f'  - {col}: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean():.2f}')

# Plan features
plan_cols = [
    'estimated_cost', 'rows_scanned', 'operator_count', 'scan_count',
    'join_count', 'index_usage', 'hash_join_count', 'filter_operator_count',
    'projection_count', 'aggregate_operator_count'
]
print(f'\nExecution Plan Features ({len(plan_cols)}):')
for col in plan_cols:
    print(f'  - {col}: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean():.2f}')

interaction_cols = [
    'join_filter_complexity', 'join_table_ratio', 'aggregation_density', 'scan_join_interaction'
]
print(f'\nInteraction Features ({len(interaction_cols)}):')
for col in interaction_cols:
    print(f'  - {col}: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean():.2f}')

print('\n' + '='*70)
print('DATASET STATUS: READY FOR ML TRAINING')
print('='*70)
print(f'\nRows (samples): {len(df)}')
print(f'Features: {len(df.columns) - 3} (excluding query_id, run_number, execution_time)')
print(f'Target: execution_time (regression)')
print(f'Classes: N/A (continuous target)')
print(f'\nNext Steps:')
print('  1. Train/test split')
print('  2. Feature scaling/normalization')
print('  3. Model selection (Linear, Decision Tree, Ensemble, Neural Net, etc.)')
print('  4. Cross-validation and hyperparameter tuning')
print('  5. Final evaluation on hold-out test set')
