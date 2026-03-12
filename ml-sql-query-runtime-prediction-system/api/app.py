from fastapi import FastAPI


app = FastAPI(
	title="SQL Query Runtime Predictor API",
	description="API for ML-based SQL runtime prediction.",
	version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
	"""Project metadata endpoint."""
	return {
		"name": "sql-query-runtime-predictor",
		"status": "initialized",
		"phase": "phase-1",
	}


@app.get("/health")
def health() -> dict[str, str]:
	"""Simple health check endpoint."""
	return {"status": "ok"}
