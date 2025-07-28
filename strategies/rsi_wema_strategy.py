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
    df['Pattern'] = detect_candlestick_pattern(df)

    # Buy Signal Conditions
    buy_cond = (
        df['Pattern'].isin(['BullishEngulfing', 'MorningStar', 'Hammer', 'DojiBreakout']) &
        (df['WEMA_fast'] > df['WEMA_slow']) &
        (df['RSI'] > 35) &
        (df['MACD'] > df['MACD_signal']) &
        (df['ADX'] > 15) &
        (df['Close'] > df['EMA_trend'])
    )

    sell_cond = (
       df['Pattern'].isin(['BearishEngulfing', 'EveningStar', 'InvertedHammer', 'DojiBreakout']) &
        (df['WEMA_fast'] < df['WEMA_slow']) &
        (df['RSI'] < 60) &
        (df['MACD'] < df['MACD_signal']) &
        (df['ADX'] > 15) &
        (df['Close'] < df['EMA_trend'])
    )

    df.loc[buy_cond, 'Signal'] = 1
    df.loc[sell_cond, 'Signal'] = -1


    # === Risk Management ===
    df['Stop_Loss'] = df['Close'] * (1 - sl_pct)
    df['Take_Profit'] = df['Close'] * (1 + tp_pct)
    df['Risk_Amount'] = risk_per_trade  # Assume this is % of capital

    # === Clean up temp col ===
    df.drop(['RSI_mean3', 'MACD_signal'], axis=1, inplace=True)

    return df.dropna()


def detect_candlestick_pattern(df):
    pattern = [None]  # First row has no previous

    for i in range(1, len(df) - 2):
        o, h, l, c = df.iloc[i][['Open', 'High', 'Low', 'Close']]
        o_prev, c_prev = df.iloc[i - 1][['Open', 'Close']]
        o_next, c_next = df.iloc[i + 1][['Open', 'Close']]

        body = abs(c - o)
        prev_body = abs(c_prev - o_prev)
        range_ = h - l

        # === Bullish Engulfing ===
        if (c > o and c_prev < o_prev and o < c_prev and c > o_prev):
            pattern.append("BullishEngulfing")

        # === Bearish Engulfing ===
        elif (c < o and c_prev > o_prev and o > c_prev and c < o_prev):
            pattern.append("BearishEngulfing")

        # === Morning Star ===
        elif (c_prev < o_prev and abs(df.iloc[i]['Open'] - df.iloc[i]['Close']) < range_ * 0.3 and
              c_next > o_next and c_next > (o_prev + c_prev) / 2):
            pattern.append("MorningStar")

        # === Evening Star ===
        elif (c_prev > o_prev and abs(df.iloc[i]['Open'] - df.iloc[i]['Close']) < range_ * 0.3 and
              c_next < o_next and c_next < (o_prev + c_prev) / 2):
            pattern.append("EveningStar")

        # === Hammer ===
        elif body < range_ * 0.3 and (o - l > body * 2) and (h - c < body):
            pattern.append("Hammer")

        # === Inverted Hammer ===
        elif body < range_ * 0.3 and (h - o > body * 2) and (c - l < body):
            pattern.append("InvertedHammer")

        # === Doji with Volume Breakout ===
        elif abs(c - o) <= range_ * 0.1 and df['Volume'].iloc[i] > df['Volume'].rolling(20).mean().iloc[i] * 1.5:
            pattern.append("DojiBreakout")

        # === Inside Bar ===
        elif (df['High'].iloc[i] < df['High'].iloc[i - 1]) and (df['Low'].iloc[i] > df['Low'].iloc[i - 1]):
            pattern.append("InsideBar")

        else:
            pattern.append(None)

    pattern.extend([None] * (len(df) - len(pattern)))  # Fill last few entries with None
    return pattern

