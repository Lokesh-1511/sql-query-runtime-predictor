import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const pickNumber = (...values) => {
  for (const value of values) {
    if (value === null || value === undefined) {
      continue
    }
    const num = Number(value)
    if (Number.isFinite(num)) {
      return num
    }
  }
  return null
}

export const predictQuery = async (query) => {
  try {
    const response = await api.post('/predict', {
      sql_query: query,
    })
    const data = response.data || {}
    const top = data.top_feature_values || {}
    const tableCount = Array.isArray(data.tables_used) ? data.tables_used.length : null

    return {
      ...data,
      number_of_tables: pickNumber(data.number_of_tables, tableCount),
      number_of_joins: pickNumber(data.number_of_joins, top.number_of_joins),
      number_of_filters: pickNumber(data.number_of_filters, top.number_of_filters),
      aggregation_count: pickNumber(data.aggregation_count, top.aggregation_count),
      subquery_depth: pickNumber(data.subquery_depth, top.subquery_depth),
      scan_count: pickNumber(data.scan_count, top.scan_count),
      where_clause_count: pickNumber(data.where_clause_count, top.where_clause_count),
    }
  } catch (error) {
    console.error('Error predicting query:', error)
    throw error
  }
}

export const getModelInfo = async () => {
  try {
    const response = await api.get('/model-info')
    const data = response.data || {}
    const metrics = data.metrics || {}

    return {
      ...data,
      model_name: data.model_name || data.best_model_name || null,
      r2_score: pickNumber(data.r2_score, metrics.r2_score, metrics.r2),
      mae: pickNumber(data.mae, metrics.mae),
      rmse: pickNumber(data.rmse, metrics.rmse),
      training_samples: pickNumber(data.training_samples, metrics.training_samples),
    }
  } catch (error) {
    console.error('Error fetching model info:', error)
    throw error
  }
}

export default api
