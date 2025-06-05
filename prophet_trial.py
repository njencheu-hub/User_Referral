from prophet import Prophet
import pandas as pd

# Minimal dummy data to trigger compilation
df = pd.DataFrame({
    'ds': pd.date_range(start='2022-01-01', periods=10),
    'y': range(10)
})

model = Prophet()
model.fit(df)