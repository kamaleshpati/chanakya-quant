import pandas as pd
import ta

def wema_rsi_strategy(
    df, 
    fast=9, 
    slow=21, 
    rsi_period=14, 
    risk_per_trade=0.01, 
    sl_pct=0.01, 
    tp_pct=0.02,
    trend_window=100  # ← Change this value to control the trend filter (e.g., 50, 200, etc.)
):
    df = df.copy()

    # Convert datetime and set index
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)

    # === Indicator Calculations ===

    # Weighted EMAs
    df['WEMA_fast'] = df['Close'].ewm(span=fast, adjust=False).mean()
    df['WEMA_slow'] = df['Close'].ewm(span=slow, adjust=False).mean()

    # Trend Filter EMA (user-controlled)
    df['EMA_trend'] = df['Close'].ewm(span=trend_window, adjust=False).mean()

    # RSI + Rolling mean for smoothing
    rsi_indicator = ta.momentum.RSIIndicator(close=df['Close'], window=rsi_period)
    df['RSI'] = rsi_indicator.rsi()
    df['RSI_mean3'] = df['RSI'].rolling(3).mean()

    # MACD
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    # ADX
    adx = ta.trend.ADXIndicator(
        high=df['High'], low=df['Low'], close=df['Close'], window=14
    )
    df['ADX'] = adx.adx()

    # === Signal Logic ===
    df['Signal'] = 0

    # Buy Signal Conditions
    buy_cond = (
        (df['WEMA_fast'] > df['WEMA_slow']) &
        (df['RSI_mean3'] > 45) &
        (df['MACD'] > df['MACD_signal']) &
        (df['ADX'] > 20) &
        (df['Close'] > df['EMA_trend'])
    )

    # Sell Signal Conditions
    sell_cond = (
        (df['WEMA_fast'] < df['WEMA_slow']) &
        (df['RSI_mean3'] < 55) &
        (df['MACD'] < df['MACD_signal']) &
        (df['ADX'] > 20) &
        (df['Close'] < df['EMA_trend'])
    )

    df.loc[buy_cond, 'Signal'] = 1
    df.loc[sell_cond, 'Signal'] = -1

    # === Risk Management Placeholders ===
    df['Stop_Loss'] = df['Close'] * (1 - sl_pct)
    df['Take_Profit'] = df['Close'] * (1 + tp_pct)
    df['Risk_Amount'] = risk_per_trade  # Assume this is % of capital

    # === Clean up temporary columns ===
    df.drop(['RSI_mean3', 'MACD_signal'], axis=1, inplace=True)

    return df.dropna()
