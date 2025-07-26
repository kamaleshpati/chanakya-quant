import pandas as pd
import os

# Load the CSV with proper datetime parsing
df = pd.read_csv('data/raw/NIFTY50_minute_data.csv', parse_dates=['date'])

# Extract year from the 'date' column
df['Year'] = df['date'].dt.year

# Create output directory
output_dir = 'data/raw'
os.makedirs(output_dir, exist_ok=True)

# Split and save files per year
for year, group in df.groupby('Year'):
    file_path = os.path.join(output_dir, f'nifty_50_mindata_{year}.csv')
    group.drop(columns='Year').to_csv(file_path, index=False)
    print(f"Saved {file_path} with {len(group)} rows")
