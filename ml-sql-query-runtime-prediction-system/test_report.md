# Test Report

This file is append-only and records verification steps after each phase.

## Phase 1 - Smoke Tests
Date: 2026-03-12
Status: Passed
Environment: `e:/ML_Project/sql-query-runtime-predictor/.venv-1/Scripts/python.exe`

### Test Cases and Results
1. Query runner runtime measurement
- Target: `runner/query_runner.py`
- Check: create DuckDB connection and measure runtime for `SELECT 1`
- Result: Passed (`0.001270s`)

2. SQL structural feature extraction
- Target: `features/feature_extractor.py`
- Check: parse join/group/order query and validate feature fields
- Result: Passed
- Output:
  - `number_of_tables=3`
  - `number_of_joins=2`
  - `number_of_filters=1`
  - `aggregation_count=1`
  - `group_by_present=1`
  - `order_by_present=1`
  - `subquery_depth=0`

3. Dataset builder
- Target: `pipeline/build_dataset.py`
- Check: build dataset from a temporary runtime CSV and verify output file/columns
- Result: Passed (`shape=(2, 10)`)

4. FastAPI endpoints
- Target: `api/app.py`
- Check: `GET /` and `GET /health` using `fastapi.testclient.TestClient`
- Result: Passed (`/health` returned `{"status": "ok"}`)

### Command Used
A Python smoke-test script was piped into the configured interpreter from the project directory.

### Notes for Next Phases
- Append one new test section per phase.
- Include failing tests and remediation notes if any failures occur.

## Phase 2 - Database Setup Tests
Date: 2026-03-12
Status: Passed
Environment: `e:/ML_Project/sql-query-runtime-predictor/.venv-1/Scripts/python.exe`

### Test Cases and Results
1. Setup script execution
- Target: `pipeline/setup_database.py`
- Check: run setup end-to-end to install/load extension, generate TPC-H data, and print metadata
- Result: Passed
- Evidence:
  - `Database ready: data\\tpch.db`
  - All required table names printed
  - Row counts printed for all required tables

2. Database artifact presence
- Target: `data/tpch.db`
- Check: verify database file exists after setup
- Result: Passed

3. Required table verification and row counts
- Target: `data/tpch.db`
- Check: connect with DuckDB, assert required table set is present, and fetch row counts
- Result: Passed (`tables_present=True`)
- Output:
  - `customer:150000`
  - `orders:1500000`
  - `lineitem:6001215`
  - `nation:25`
  - `region:5`
  - `supplier:10000`
  - `part:200000`
  - `partsupp:800000`

### Commands Used
- `python pipeline/setup_database.py` from project root directory.
- Additional inline Python verification against `data/tpch.db` for table presence and row counts.

## Phase 3 - Query Workload Tests
Date: 2026-03-12
Status: Passed
Environment: `e:/ML_Project/sql-query-runtime-predictor/.venv-1/Scripts/python.exe`

### Test Cases and Results
1. Query workload file creation
- Target: `queries/`
- Check: verify `q*.sql` files exist for benchmark workload
- Result: Passed (`22` files found)

2. Query loader utility diagnostics
- Target: `runner/query_loader.py`
- Check: editor diagnostics / static checks
- Result: Passed (no errors found)

3. End-to-end query execution on DuckDB
- Target: `queries/q1.sql` ... `queries/q22.sql`
- Check: load each query with `runner.query_loader.load_query` and execute against `data/tpch.db`
- Initial Result: Failed (`21` passed, `1` failed)
- Failure detail:
  - `q9.sql`: binder error due to `l_suppkey` referenced before `lineitem` join binding
- Remediation:
  - Updated `queries/q9.sql` join order so `lineitem` is joined before supplier join predicate references `l_suppkey`
- Final Result: Passed (`22` passed, `0` failed)

### Commands Used
- Inline Python execution to iterate `list_query_files('queries')`, `load_query(...)`, and execute each query on `data/tpch.db`.
- Re-ran the same validation command after patching `q9.sql`.

## Phase 4 - Automated Runner Tests
Date: 2026-03-12
Status: Passed
Environment: `e:/ML_Project/sql-query-runtime-predictor/.venv-1/Scripts/python.exe`

### Test Cases and Results
1. Query runner diagnostics
- Target: `runner/query_runner.py`
- Check: editor diagnostics / static checks
- Result: Passed (no errors found)

2. CLI workload execution
- Target: `runner/query_runner.py`
- Check: execute workload runner with 5 runs per query
- Initial Result: Failed
- Failure detail:
  - `ModuleNotFoundError: No module named 'runner'` when running as direct script
- Remediation:
  - Added import fallback in `query_runner.py` for direct invocation context
- Final Result: Passed
- Output:
  - `Saved runtime logs to: data\\query_runtime_logs.csv`
  - `Rows: 110`
  - `Unique queries: 22`
  - `Runs per query: 5`

3. Runtime dataset schema and quality checks
- Target: `data/query_runtime_logs.csv`
- Check:
  - expected columns exist
  - expected row count (`22 * 5 = 110`)
  - expected unique query count (`22`)
  - run numbers contain `[1,2,3,4,5]`
  - no nulls in required columns
  - all execution times are positive
- Result: Passed
- Output:
  - `columns=query_id,query_text,execution_time,run_number`
  - `rows=110`
  - `query_count=22`
  - `run_numbers=[1, 2, 3, 4, 5]`
  - `nulls=0`
  - `non_positive_times=0`

4. Runtime variability validation
- Target: `data/query_runtime_logs.csv`
- Check: ensure execution times vary across runs for at least some queries
- Result: Passed
- Evidence:
  - `queries_with_variability=22`
  - `total_queries=22`
  - Example per-query `execution_time` standard deviation values:
    - `q18:0.025417875`
    - `q1:0.018908552`
    - `q10:0.013600754`
    - `q20:0.010083204`
    - `q9:0.007686280`

### Commands Used
- `python runner/query_runner.py --runs 5`
- Inline Python validation for CSV schema and data quality metrics.
- Inline Python group-by standard deviation validation for runtime variability.

## Workload Extension Tests - Catalog 100x40
Date: 2026-03-12
Status: Passed
Environment: `e:/ML_Project/sql-query-runtime-predictor/.venv-1/Scripts/python.exe`

### Test Cases and Results
1. Catalog generation and validation
- Target: `pipeline/generate_queries.py`
- Check: generate and validate 100 catalog queries against DuckDB
- Result: Passed
- Output:
  - `Total valid queries: 100`
  - `Validation failures (discarded candidates): 0`

2. Balanced category distribution
- Target: `queries/query_catalog.json`
- Check: verify balanced analytical workload profile
- Result: Passed
- Output:
  - `single_table: 22`
  - `join_query: 32`
  - `aggregation_query: 12`
  - `group_by_query: 12`
  - `filter_query: 11`
  - `analytical_query: 11`

3. Catalog schema and directory structure
- Target: `queries/query_catalog.json`, `queries/base_queries/`, `queries/generated_queries/`
- Check:
  - catalog has 100 entries
  - each entry contains required fields
  - directory structure exists
- Result: Passed
- Output:
  - `query_count=100`
  - `catalog_entries=100`
  - `first_entry_keys=category,complexity_level,query_id,sql_query,tables_used`
  - `has_base_dir=True`
  - `has_generated_dir=True`

4. Full workload execution (100 x 40)
- Target: `runner/query_runner.py`
- Check: execute catalog workload with 40 runs per query
- Result: Passed
- Output summary:
  - `total queries: 100`
  - `runs per query: 40`
  - `total executions: 4000`
  - runtime stats:
    - `min: 0.000458`
    - `max: 1.076223`
    - `mean: 0.040879`
    - `median: 0.008878`

5. Runtime log schema and integrity
- Target: `data/query_runtime_logs.csv`
- Check:
  - required columns present
  - exactly 4000 rows
  - exactly 100 unique queries
  - each query has exactly 40 runs
  - no nulls in required fields
  - all execution times positive
- Result: Passed
- Output:
  - `rows=4000`
  - `columns=query_id,run_number,execution_time,query_category,tables_used`
  - `has_required_columns=True`
  - `query_count=100`
  - `runs_per_query_min=40`
  - `runs_per_query_max=40`
  - `total_nulls_required=0`
  - `non_positive_times=0`

6. Randomized execution order verification
- Target: `data/query_runtime_logs.csv`
- Check: compare query order in run 1 vs run 2
- Result: Passed
- Evidence:
  - `order_diff_run1_run2=True`
  - `first10_run1=q043,q042,q092,q010,q066,q051,q002,q071,q016,q079`
  - `first10_run2=q058,q027,q006,q014,q062,q025,q023,q039,q026,q053`

### Commands Used
- `python pipeline/generate_queries.py --target-count 100`
- `python runner/query_runner.py --runs 40 --catalog-path queries/query_catalog.json`
- Inline Python validation for catalog schema, distribution, runtime CSV integrity, and run-order randomization.

## Phase 5 - Execution Plan Collection Tests
Date: 2026-03-12
Status: Passed
Environment: `e:/ML_Project/sql-query-runtime-predictor/.venv-1/Scripts/python.exe`

### Test Cases and Results
1. Query runner diagnostics after plan-mode extension
- Target: `runner/query_runner.py`
- Check: editor diagnostics / static checks
- Result: Passed (no errors found)

2. Execution plan dataset generation
- Target: `runner/query_runner.py` with `--collect-plans`
- Check: generate execution dataset from `queries/query_catalog.json`
- Initial Result: Failed
- Failure detail:
  - `TabError: inconsistent use of tabs and spaces in indentation`
- Remediation:
  - Normalized indentation in `runner/query_runner.py`
- Final Result: Passed
- Output:
  - `Saved query execution dataset to: data\\query_execution_dataset.csv`
  - `Rows: 100`
  - `Unique queries: 100`

3. Execution dataset schema and quality checks
- Target: `data/query_execution_dataset.csv`
- Check:
  - required columns exist
  - row count equals catalog query count
  - no nulls in required columns
  - all runtime values positive
- Result: Passed
- Output:
  - `rows=100`
  - `columns=query_id,query_text,runtime,execution_plan`
  - `has_required_columns=True`
  - `query_count=100`
  - `nulls_required=0`
  - `non_positive_runtime=0`

4. Plan text presence validation
- Target: `data/query_execution_dataset.csv`
- Check: execution plan text includes both explain sections for each row
- Result: Passed
- Output:
  - `plan_has_explain=100`
  - `plan_has_explain_analyze=100`

### Commands Used
- `python runner/query_runner.py --collect-plans --catalog-path queries/query_catalog.json`
- Inline Python validation for execution dataset schema and plan markers.
