# CineForecast REST API Reference

The CineForecast Backend API provides endpoints for box office predictions, sensitivity what-if simulations, explainable SHAP attributions, catalog browsing, and aggregate macro trends.

**Interactive OpenAPI Docs:** `http://localhost:8000/docs`  
**Base URL:** `http://localhost:8000/api`  

---

## 1. Prediction Endpoints

### `POST /api/predict`
Predicts worldwide gross revenue and success tier from pre-release features.

#### Request Body (`application/json`)
```json
{
  "title": "Interstellar Horizon",
  "budget": 150000000.0,
  "runtime": 142,
  "genres": ["Science Fiction", "Adventure", "Drama"],
  "release_date": "2026-11-20",
  "director": "Christopher Nolan",
  "cast_size": 8,
  "production_company_count": 3,
  "production_country_count": 2,
  "is_franchise": 0,
  "director_prior_avg_revenue": 450000000.0,
  "director_prior_film_count": 8,
  "primary_production_company_prior_avg_revenue": 380000000.0,
  "primary_production_company_prior_film_count": 25
}
```

#### Response (`200 OK`)
```json
{
  "title": "Interstellar Horizon",
  "budget": 150000000.0,
  "predicted_revenue": 562300000.0,
  "predicted_roi": 2.7487,
  "predicted_tier": "Hit",
  "confidence_tier_probabilities": {
    "Blockbuster": 0.42,
    "Hit": 0.48,
    "Break-even": 0.08,
    "Flop": 0.02
  },
  "base_value": 41200000.0,
  "top_positive_factors": [
    {
      "feature": "budget",
      "value": 150000000.0,
      "shap_value": 0.8421,
      "abs_shap": 0.8421
    },
    {
      "feature": "director_prior_avg_revenue",
      "value": 450000000.0,
      "shap_value": 0.3125,
      "abs_shap": 0.3125
    }
  ],
  "top_negative_factors": []
}
```

---

## 2. What-If Scenario Simulation

### `POST /api/whatif`
Compares a baseline film configuration against user-modified adjustments and returns revenue and ROI deltas.

#### Request Body
```json
{
  "base_params": {
    "title": "Project Eclipse",
    "budget": 40000000.0,
    "runtime": 105,
    "genres": ["Thriller", "Mystery"],
    "release_date": "2026-03-10"
  },
  "adjustments": {
    "budget": 80000000.0,
    "genres": ["Action", "Thriller", "Sci-Fi"],
    "release_date": "2026-07-04",
    "is_franchise": 1
  }
}
```

#### Response (`200 OK`)
```json
{
  "base_budget": 40000000.0,
  "modified_budget": 80000000.0,
  "base_predicted_revenue": 68400000.0,
  "modified_predicted_revenue": 185200000.0,
  "revenue_delta": 116800000.0,
  "revenue_delta_percent": 170.76,
  "base_predicted_roi": 0.71,
  "modified_predicted_roi": 1.315,
  "roi_delta": 0.605,
  "base_predicted_tier": "Break-even",
  "modified_predicted_tier": "Hit",
  "tier_changed": true,
  "modified_top_positive_factors": [],
  "modified_top_negative_factors": []
}
```

---

## 3. Explainability & SHAP

### `GET /api/shap/global`
Returns the global mean absolute SHAP value summary for all 34 pre-release features.

### `GET /api/shap/ablation`
Returns comparative metrics from the Leakage Ablation Study (Pre-Release vs Early-Signal).

### `GET /api/shap/{movie_id}`
Returns cached per-movie SHAP waterfall breakdown for any catalog movie.

---

## 4. Catalog & Trends

### `GET /api/movies`
Query parameters:
- `page` (int, default: 1)
- `size` (int, default: 20)
- `search` (string)
- `genre` (string)
- `tier` (string: Flop, Break-even, Hit, Blockbuster)
- `sort_by` (revenue, budget, roi, predicted_revenue, release_year)
- `order` (asc, desc)

### `GET /api/trends`
Returns aggregate statistics, genre breakdowns, release month seasonality patterns, and yearly box office volume.
