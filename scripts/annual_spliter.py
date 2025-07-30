import pandas as pd
import os

df = pd.read_csv('data/market/raw/NIFTY50_minute_data.csv', parse_dates=['date'])

df['Year'] = df['date'].dt.year

output_dir = 'data/market/raw'
os.makedirs(output_dir, exist_ok=True)

for year, group in df.groupby('Year'):
    file_path = os.path.join(output_dir, f'nifty_50_mindata_{year}.csv')
    group.drop(columns='Year').to_csv(file_path, index=False)
    print(f"Saved {file_path} with {len(group)} rows")
