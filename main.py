import pandas as pd

from strategies.ema_crossover import ema_crossover
from strategies.rsi_mean_reversion import rsi_mean_reversion
from strategies.bollinger_band_reversal import bollinger_band_reversal
from strategies.donchian_breakout import donchian_breakout
from strategies.rsi_wema_strategy import wema_rsi_strategy

from backtest.backtest_engine import backtest

# === Load Data ===
df = pd.read_csv('data/raw/nifty_50_mindata_2024.csv', parse_dates=['date'])

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

# === Apply Strategy ===
# strat_df = ema_crossover(df)
# strat_df = rsi_mean_reversion(df)
# strat_df = bollinger_band_reversal(df)
# strat_df = donchian_breakout(df)
strat_df = wema_rsi_strategy(df)

# === Run Backtest ===
backtest(strat_df)