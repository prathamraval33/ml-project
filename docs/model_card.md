# CineForecast Model Card

**Model Name:** CineForecast XGBoost Champion Regressor & Multi-Class Classifier  
**Model Family:** Gradient Boosted Decision Trees (`XGBRegressor`, `XGBClassifier`)  
**Version:** 1.0.0  
**Release Date:** September 2026  
**License:** MIT  

---

## 1. Intended Use & Scope

### Primary Intended Uses
- **Pre-Release Revenue Forecasting:** Predict worldwide gross box office revenue (USD) for films prior to theatrical release using known pre-production and distribution variables (budget, genres, historical director/studio track records, release calendar windows, cast size).
- **Success Tier Classification:** Classify project financial return on investment (ROI = (Revenue - Budget) / Budget) into categorical tiers:
  - **Flop:** $\text{ROI} < 0.0$ (Fails to recoup production budget)
  - **Break-even:** $0.0 \le \text{ROI} < 1.0$ (Recoups budget up to 2x gross)
  - **Hit:** $1.0 \le \text{ROI} < 3.0$ (2x to 4x return)
  - **Blockbuster:** $\text{ROI} \ge 3.0$ (4x+ return)
- **Scenario Sensitivity Analysis:** Simulate parameter changes in pre-production via the **What-If Studio** to understand feature elasticity.
- **Model Explainability:** Decompose individual and global feature influences using TreeExplainer SHAP values.

### Out-of-Scope & Misuse
- **Financial Guarantees:** Predictions must NOT be treated as guaranteed returns for investment underwriting without human risk assessment.
- **Unmodeled Exogenous Shocks:** The model cannot anticipate external disruptions such as global pandemic theater closures, unforeseen PR crises, or last-minute marketing strategy pivots.

---

## 2. Dataset Description & Limitations

- **Source Dataset:** Verified TMDB historical box office records (1990–2025).
- **Usable Financial Records:** Out of 9,999 raw rows, 4,774 records lacked budget data ($\text{budget} = 0$) and 4,432 lacked revenue data ($\text{revenue} = 0$). After strict deduplication and financial completeness filtering, **3,931 films** met all quality standards ($\text{budget} > 0, \text{revenue} > 0, \text{year} \ge 1990, \text{runtime} \ge 40\text{m}$).
- **Evaluation Split:** Chronological time-ordered split holding out recent films from 2023–2025 as the unseen test set ($N=383$) while training on 1990–2022 ($N=3,548$).

---

## 3. Leakage Ablation Study

To demonstrate strict machine learning discipline and prevent hindsight target leakage, we compared pure **Pre-Release features** against an **Early-Signal feature set** (which incorporates post-release TMDB popularity and user votes):

| Model Architecture | Feature Set | Feature Count | Test $R^2$ (Log) | Test RMSE (Log) | Test MAE (Log) | Pearson $r$ | MdAPE (%) |
|---|---|---|---|---|---|---|---|
| **Ridge Regression** | Pre-Release (Clean) | 34 | 0.4021 | 1.6950 | 1.1609 | 0.6536 | 70.86% |
| **Ridge Regression** | Early-Signal (+Popularity/Votes) | 40 | 0.2920 | 1.8445 | 1.3596 | 0.6514 | 72.18% |
| **CatBoost** | Pre-Release (Clean) | 34 | 0.3943 | 1.7061 | 1.2109 | 0.6410 | 69.53% |
| **CatBoost** | Early-Signal (+Popularity/Votes) | 40 | 0.4047 | 1.6914 | 1.2174 | 0.6939 | 67.90% |
| **XGBoost (Baseline)** | Pre-Release (Clean) | 34 | 0.3332 | 1.7901 | 1.2518 | 0.6070 | 70.60% |
| **XGBoost (Tuned Champion)** | **Pre-Release (Clean)** | **34** | **0.3747** | **1.7334** | **1.2236** | **0.6267** | **68.40%** |

### Finding
Early-signal models achieve higher Pearson correlation due to post-release audience reaction capturing box-office success after the fact. CineForecast exclusively deploys the **Pre-Release clean model** to maintain true predictive integrity.

---

## 4. Hyperparameter Configuration (Champion XGBoost)

- `n_estimators`: 400
- `max_depth`: 5
- `learning_rate`: 0.0134
- `subsample`: 0.7687
- `colsample_bytree`: 0.8710
- `reg_alpha`: 0.4919
- `reg_lambda`: 0.0418
- `min_child_weight`: 2

---

## 5. Ethical & Environmental Considerations

- **Compute Footprint:** Total training and Bayesian hyperparameter search executed in < 2 minutes on CPU.
- **Fairness & Representation:** Models reflect historical studio distribution bias favoring major domestic releases. Independent international films are flagged with `is_international_coproduction` and evaluated with country-specific priors.
