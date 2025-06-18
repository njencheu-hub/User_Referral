# Referral Program Impact Analysis

**Duration:** June 2024  
**Tools Used:** Python, Pandas, Prophet, Seaborn, Matplotlib, SciPy  

## Overview

This project evaluated the impact of a referral program launched on October 31, 2015. Using time-series forecasting and exploratory analysis, it examined changes in user behavior, revenue trends, and signs of cannibalization or fraud post-launch.

---

## Key Steps

### 1. Data Validation & Cleanup
- Verified no referrals before launch; reassigned inconsistent referral flags per user.
- Ensured each user was consistently classified as referred or not based on first appearance.

### 2. Behavioral Insights
- **Users increased by ~22%** post-launch, but revenue only rose **~17%**.
- **Non-referred user count dropped**, indicating **channel cannibalization**.
- Suspicious spike in users per device, suggesting users created multiple accounts to exploit referral rewards.

### 3. Time-Series Forecasting with Prophet
- Trained Prophet model on pre-launch revenue to forecast expected post-launch revenue.
- Actual post-launch revenue consistently exceeded the upper 95% confidence interval.

![Prediction Chart](predictions.png)

- Average actual revenue: **$83,714/day**  
- Predicted baseline: **$79,049/day**

### 4. Statistical Significance
- Conducted **paired t-test** comparing forecast vs. actual revenue.
- Result: **p = 0.00242** → statistically significant uplift, though data irregularities caution against definitive conclusions.

---

## Conclusion

The referral program correlated with increased users and revenue, but evidence of fraud and cannibalization complicates interpretation. Recommends follow-up with engineering/product teams to clean referral logic and audit incentives.

---
  

