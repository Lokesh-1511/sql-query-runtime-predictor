You are improving the machine learning system in the project:

"Machine Learning Based SQL Query Runtime Prediction System".

The project pipeline already exists and successfully produces:

data/ml_training_dataset.csv

Dataset properties:

* 4000 rows
* 18 columns
* 100 queries × 40 runs each
* structural SQL features
* execution plan features
* runtime target variable

Current best model performance:

R² ≈ 0.84 using XGBoost.

Your task is to improve the model by implementing additional feature engineering, execution plan parsing improvements, and better training strategies.

Do NOT rebuild the project. Extend the existing system.

---

PHASE A — Improve Execution Plan Feature Extraction

The current execution plan parser only detects scan_count reliably.

DuckDB execution plans contain operators such as:

SEQ_SCAN
HASH_JOIN
FILTER
PROJECTION
AGGREGATE

Update:

features/plan_parser.py

Add regex detection for these operators and extract new features:

hash_join_count
filter_operator_count
projection_count
aggregate_operator_count

Each feature should count the number of occurrences in the execution plan text.

Ensure these features are added to:

data/plan_metrics_100.csv

---

PHASE B — Add Interaction Features

Create new derived features in the dataset.

Modify:

features/build_training_dataset.py

Add the following features:

join_filter_complexity = number_of_joins * number_of_filters

join_table_ratio = number_of_joins / (number_of_tables + 1)

aggregation_density = aggregation_count / (number_of_tables + 1)

scan_join_interaction = scan_count * number_of_joins

Ensure the final dataset now includes these features.

---

PHASE C — Add Query Complexity Features

Extract additional query features from SQL text.

Update:

features/feature_extractor.py

Add:

query_length
token_count

Implementation:

query_length = length of SQL query string

token_count = number of tokens from sqlglot parsed query

Add these columns to the features dataset.

---

PHASE D — Improve Training Pipeline

Modify the training script (Phase 9) to include:

1. Cross-validation

Use 5-fold cross validation instead of a single train/test split.

Use:

sklearn.model_selection.cross_val_score

2. Hyperparameter tuning

Add RandomizedSearchCV for XGBoost.

Tune parameters:

max_depth
learning_rate
n_estimators
subsample
colsample_bytree

Use 20 random iterations.

3. Feature importance analysis

After training, compute:

* permutation importance
* feature_importances_

Save plots to:

feature_importance.png

---

PHASE E — Improve Model Evaluation

Extend evaluation to include:

MAE
RMSE
R²
Cross-validation score

Add residual distribution visualization:

predicted vs actual scatter plot
residual histogram

Save plots automatically.

---

PHASE F — Optional Dataset Expansion

Add functionality to generate additional queries.

Update:

pipeline/generate_queries.py

Allow generating up to:

200 queries instead of 100.

This will create a dataset of:

200 queries × 40 runs = 8000 samples.

Ensure the pipeline still works with the larger dataset.

---

Expected Result After Improvements

Model performance target:

Current R² ≈ 0.84

Goal:

R² ≈ 0.88 – 0.92

depending on dataset quality.

---

Important Constraints

* Do not break existing pipeline phases.
* Keep dataset reproducible.
* Maintain compatibility with DuckDB.
* Keep code modular and readable.

Return updated code for all modified modules.
