import pandas as pd

from strategies.composite_price_strategy import composite_strategy

from backtest.backtest_engine import backtest


capital = 100000  # Initial capital

for i in range(2024,2025):
# === Load Data ===
    df = pd.read_csv(f'data/raw/nifty_50_mindata_{i}.csv', parse_dates=['date'])

    # === Rename Columns ===
    df.rename(columns={
        'date': 'Datetime',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)

    # === Filter NSE Trading Hours: 09:15 to 15:30 ===
    df['Time'] = df['Datetime'].dt.time
    df = df[
        (df['Time'] >= pd.to_datetime('09:15').time()) &
        (df['Time'] <= pd.to_datetime('15:30').time())
    ]
    df.drop(columns=['Time'], inplace=True)

    # === Remove Missing Values and Reorder Columns ===
    df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].dropna()

    strat_df = composite_strategy(df)

    # === Run Backtest ===
    print(f"Running backtest... for {i} data")
    _, capital = backtest(strat_df, initial_capital=capital)