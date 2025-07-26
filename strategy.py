import pandas as pd
import numpy as np

# === Load Data ===
def load_data(filepath):
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df

# === Indicator Functions ===
def compute_indicators(df, fast=9, slow=21, rsi_period=14):
    df['WEMA_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
    df['WEMA_slow'] = df['close'].ewm(span=slow, adjust=False).mean()

    # RSI manually
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI_mean3'] = df['RSI'].rolling(3).mean()

    # MACD manually
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # ADX manually
    df['+DM'] = df['high'].diff().where(df['high'].diff() > df['low'].diff(), 0)
    df['-DM'] = df['low'].diff().where(df['low'].diff() > df['high'].diff(), 0)
    tr = pd.concat([
        df['high'] - df['low'],
        (df['high'] - df['close'].shift()).abs(),
        (df['low'] - df['close'].shift()).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    df['+DI'] = 100 * (df['+DM'].rolling(14).sum() / atr)
    df['-DI'] = 100 * (df['-DM'].rolling(14).sum() / atr)
    dx = 100 * (abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI']))
    df['ADX'] = dx.rolling(14).mean()

    return df

# === Signal Strategy ===
def generate_signals(df):
    df['Signal'] = 0
    buy_cond = (
        (df['WEMA_fast'] > df['WEMA_slow']) &
        (df['RSI_mean3'] > 45) &
        (df['MACD'] > df['MACD_signal']) &
        (df['ADX'] > 20)
    )
    sell_cond = (
        (df['WEMA_fast'] < df['WEMA_slow']) &
        (df['RSI_mean3'] < 55) &
        (df['MACD'] < df['MACD_signal']) &
        (df['ADX'] > 20)
    )
    df.loc[buy_cond, 'Signal'] = 1
    df.loc[sell_cond, 'Signal'] = -1
    return df

# === Backtest ===
def backtest(df, capital=1000000, sl_pct=0.01, tp_pct=0.02):
    trades = []
    position = None
    entry_price = None
    qty = 0

    equity = capital
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]

        if position is None:
            if row['Signal'] == 1:
                position = 'long'
                entry_price = row['close']
                qty = equity // entry_price
                sl = entry_price * (1 - sl_pct)
                tp = entry_price * (1 + tp_pct)
                entry_time = row.name
            elif row['Signal'] == -1:
                position = 'short'
                entry_price = row['close']
                qty = equity // entry_price
                sl = entry_price * (1 + sl_pct)
                tp = entry_price * (1 - tp_pct)
                entry_time = row.name

        elif position == 'long':
            if row['low'] <= sl:
                pnl = (sl - entry_price) * qty
                equity += pnl
                trades.append((entry_time, row.name, entry_price, sl, 'long', pnl, 'SL', equity))
                position = None
            elif row['high'] >= tp:
                pnl = (tp - entry_price) * qty
                equity += pnl
                trades.append((entry_time, row.name, entry_price, tp, 'long', pnl, 'TP', equity))
                position = None
            elif row['Signal'] == -1:
                pnl = (row['close'] - entry_price) * qty
                equity += pnl
                trades.append((entry_time, row.name, entry_price, row['close'], 'long', pnl, 'REV', equity))
                position = None

        elif position == 'short':
            if row['high'] >= sl:
                pnl = (entry_price - sl) * qty
                equity += pnl
                trades.append((entry_time, row.name, entry_price, sl, 'short', pnl, 'SL', equity))
                position = None
            elif row['low'] <= tp:
                pnl = (entry_price - tp) * qty
                equity += pnl
                trades.append((entry_time, row.name, entry_price, tp, 'short', pnl, 'TP', equity))
                position = None
            elif row['Signal'] == 1:
                pnl = (entry_price - row['close']) * qty
                equity += pnl
                trades.append((entry_time, row.name, entry_price, row['close'], 'short', pnl, 'REV', equity))
                position = None

    trades_df = pd.DataFrame(trades, columns=[
        'Entry Time', 'Exit Time', 'Entry Price', 'Exit Price', 'Side',
        'PnL', 'Exit Reason', 'Equity'
    ])
    return trades_df, equity

# === Metrics ===
def calculate_metrics(trades_df, initial_capital):
    total_return = (trades_df['Equity'].iloc[-1] - initial_capital) / initial_capital * 100
    daily_returns = trades_df['Equity'].pct_change().dropna()
    sharpe_ratio = daily_returns.mean() / daily_returns.std() * (252 ** 0.5)
    drawdown = (trades_df['Equity'].cummax() - trades_df['Equity']).max()
    return total_return, sharpe_ratio, drawdown

# === Main ===
if __name__ == "__main__":
    path = 'data/raw/nifty_50_mindata_2023.csv'  # <-- Change path here
    df = load_data(path)
    df = compute_indicators(df)
    df = generate_signals(df)
    
    trades_df, final_equity = backtest(df)
    total_return, sharpe, max_dd = calculate_metrics(trades_df, 1000000)

    print(f"\nTotal Return: {total_return:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: ₹{max_dd:.2f}")
    print(f"Total Trades: {len(trades_df)}")

    print(trades_df.tail())

    # Optional: plot equity curve
    trades_df.set_index('Exit Time')['Equity'].plot(title="Equity Curve")
