import pandas as pd
df = pd.read_csv('data/tuz5.csv')
print(df.columns.tolist())  # Check column names
print(df.head())  # Check first few rows