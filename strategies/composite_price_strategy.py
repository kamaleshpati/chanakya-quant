import pandas as pd
import ta

def detect_candlestick_pattern(df):
    pattern = [None]  # First row has no previous

    for i in range(1, len(df) - 2):
        o, h, l, c = df.iloc[i][['Open', 'High', 'Low', 'Close']]
        o_prev, c_prev = df.iloc[i - 1][['Open', 'Close']]
        o_next, c_next = df.iloc[i + 1][['Open', 'Close']]

        body = abs(c - o)
        prev_body = abs(c_prev - o_prev)
        range_ = h - l

        if (c > o and c_prev < o_prev and o < c_prev and c > o_prev):
            pattern.append("BullishEngulfing")
        elif (c < o and c_prev > o_prev and o > c_prev and c < o_prev):
            pattern.append("BearishEngulfing")
        elif (c_prev < o_prev and abs(df.iloc[i]['Open'] - df.iloc[i]['Close']) < range_ * 0.3 and
              c_next > o_next and c_next > (o_prev + c_prev) / 2):
            pattern.append("MorningStar")
        elif (c_prev > o_prev and abs(df.iloc[i]['Open'] - df.iloc[i]['Close']) < range_ * 0.3 and
              c_next < o_next and c_next < (o_prev + c_prev) / 2):
            pattern.append("EveningStar")
        elif body < range_ * 0.3 and (o - l > body * 2) and (h - c < body):
            pattern.append("Hammer")
        elif body < range_ * 0.3 and (h - o > body * 2) and (c - l < body):
            pattern.append("InvertedHammer")
        elif abs(c - o) <= range_ * 0.1 and df['Volume'].iloc[i] > df['Volume'].rolling(20).mean().iloc[i] * 1.5:
            pattern.append("DojiBreakout")
        elif (df['High'].iloc[i] < df['High'].iloc[i - 1]) and (df['Low'].iloc[i] > df['Low'].iloc[i - 1]):
            pattern.append("InsideBar")
        else:
            pattern.append(None)

    pattern.extend([None] * (len(df) - len(pattern)))
    return pattern

def calculate_supertrend(df, period=10, multiplier=3):
    atr = ta.volatility.AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=period)
    df['ATR'] = atr.average_true_range()

    hl2 = (df['High'] + df['Low']) / 2
    df['UpperBand'] = hl2 + (multiplier * df['ATR'])
    df['LowerBand'] = hl2 - (multiplier * df['ATR'])
    df['SuperTrend'] = 1

    for i in range(1, len(df)):
        if df.loc[df.index[i], 'Close'] > df.loc[df.index[i - 1], 'UpperBand']:
            df.loc[df.index[i], 'SuperTrend'] = 1
        elif df.loc[df.index[i], 'Close'] < df.loc[df.index[i - 1], 'LowerBand']:
            df.loc[df.index[i], 'SuperTrend'] = -1
        else:
            df.loc[df.index[i], 'SuperTrend'] = df.loc[df.index[i - 1], 'SuperTrend']

    return df

def compute_ema_from_resample(df_1m, span=50):
    df_5m = df_1m.resample('5min').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()

    df_5m[f'EMA_{span}'] = df_5m['Close'].ewm(span=span, adjust=False).mean()
    df_1m[f'EMA_{span}_5m'] = df_5m[f'EMA_{span}'].reindex(df_1m.index, method='ffill')
    return df_1m

def composite_strategy(
    df,
    fast=9,
    slow=21,
    rsi_period=14,
    risk_per_trade=0.01,
    sl_pct=0.01,
    tp_pct=0.02,
    trend_window=50,
    use_supertrend=True
):
    df = df.copy()
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)

    df = compute_ema_from_resample(df, span=50)
    df['WEMA_fast'] = df['Close'].ewm(span=fast, adjust=False).mean()
    df['WEMA_slow'] = df['Close'].ewm(span=slow, adjust=False).mean()
    df['EMA_trend'] = df['Close'].ewm(span=trend_window, adjust=False).mean()

    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=rsi_period).rsi()
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    adx = ta.trend.ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14)
    df['ADX'] = adx.adx()

    atr = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], window=14)
    df['ATR'] = atr.average_true_range()

    # df = calculate_supertrend(df)
    df['Pattern'] = detect_candlestick_pattern(df)
    
    # --- Breakout Strategy Parameters ---
    df['Prev_High'] = df['High'].shift(1)
    df['Prev_Low'] = df['Low'].shift(1)

    # --- Gap Strategy ---
    df['Gap_Up'] = (df['Open'] > df['Close'].shift(1)) & ((df['Open'] - df['Close'].shift(1)) > df['ATR'] * 0.5)
    df['Gap_Down'] = (df['Open'] < df['Close'].shift(1)) & ((df['Close'].shift(1) - df['Open']) > df['ATR'] * 0.5)

    # --- Mean Reversion ---
    df['Deviation'] = df['Close'] - df['EMA_trend']
    
    df['Signal'] = 0



    for i in range(len(df)):
        row = df.iloc[i]
        buy_cond = (
            row['Pattern'] in ['BullishEngulfing', 'MorningStar', 'Hammer', 'DojiBreakout'] and
            row['WEMA_fast'] > row['WEMA_slow'] and
            row['RSI'] > 35 and
            row['MACD'] > row['MACD_signal'] and
            row['ADX'] > 15 and
            row['Close'] > row['EMA_trend']
        )

        sell_cond = (
            row['Pattern'] in ['BearishEngulfing', 'EveningStar', 'InvertedHammer', 'DojiBreakout'] and
            row['WEMA_fast'] < row['WEMA_slow'] and
            row['RSI'] < 60 and
            row['MACD'] < row['MACD_signal'] and
            row['ADX'] > 15 and
            row['Close'] < row['EMA_trend']
        )

        if (buy_cond):
            df.at[df.index[i], 'Signal'] = 1
            # print(f"[BUY] Signal at {df.index[i]}: Price={row['Close']:.2f}, Pattern={row['Pattern']}")
        elif (sell_cond):
            df.at[df.index[i], 'Signal'] = -1
            # print(f"[SELL] Signal at {df.index[i]}: Price={row['Close']:.2f}, Pattern={row['Pattern']}")

        # if row['ATR'] > df['ATR'].rolling(20).mean().iloc[i]:
        #     # risk_per_trade = risk_per_trade * row['ATR']
        #     # row["Signal"] = 0  # No action if ATR condition is not met
        #     pass  # Placeholder for ATR condition, can be used to adjust risk or skip signal
        # if row['ATR'] > df['ATR'].rolling(20).mean().iloc[i]:
        #     # risk_per_trade = risk_per_trade * row['ATR']
        #     # row["Signal"] = 0  # No action if ATR condition is not met
        #     pass # Placeholder for ATR condition, can be used to adjust risk or skip signal


        # # === Breakout Strategy ===
        # breakout_buy = row['Close'] > row['Prev_High']
        # breakout_sell = row['Close'] < row['Prev_Low']

        # # === Gap Strategy ===
        # gap_buy = row['Gap_Up'] and row['Close'] > row['Open']
        # gap_sell = row['Gap_Down'] and row['Close'] < row['Open']

        # # === Mean Reversion Strategy ===
        # mean_reversion_buy = row['Deviation'] < -df['ATR'].iloc[i] * 1.5
        # mean_reversion_sell = row['Deviation'] > df['ATR'].iloc[i] * 1.5



        # Check EMA on 5min timeline condition
        # if row['Close'] > row['EMA_50_5m']:
        #     # df.at[df.index[i], 'Signal'] = 0
        #     pass
        # elif row['Close'] < row['EMA_50_5m']:
        #     # df.at[df.index[i], 'Signal'] = 0
        #     pass
        
        

        # if (buy_cond or breakout_buy or gap_buy or mean_reversion_buy) and row['SuperTrend'] == 1:
        #     df.at[df.index[i], 'Signal'] = 1
        #     # print(f"[BUY] Signal at {df.index[i]}: Price={row['Close']:.2f}, Pattern={row['Pattern']}")
        # elif (buy_cond or breakout_buy or gap_buy or mean_reversion_buy) and row['SuperTrend'] == -1:
        #     df.at[df.index[i], 'Signal'] = 1
        #     # print(f"[BUY-ALERT] Signal at {df.index[i]}: Price={row['Close']:.2f}, Pattern={row['Pattern']}")
        # elif (sell_cond or breakout_sell or gap_sell or mean_reversion_sell) and row['SuperTrend'] == 1:
        #     df.at[df.index[i], 'Signal'] = -1
        #     # print(f"[SELL] Signal at {df.index[i]}: Price={row['Close']:.2f}, Pattern={row['Pattern']}")
        # elif (sell_cond or breakout_sell or gap_sell or mean_reversion_sell) and row['SuperTrend'] == -1:
        #     df.at[df.index[i], 'Signal'] = -1
        #     # print(f"[SELL] Signal at {df.index[i]}: Price={row['Close']:.2f}, Pattern={row['Pattern']}")
 
        # # Dummy ML Placeholder: Assume ML confidence > 0.75 always
        # ml_confidence = 0.85
        # if buy_cond and ml_confidence > 0.75:
        #     df.at[df.index[i], 'Signal'] = 1
        #     # print(f"[BUY-ML] Signal at {df.index[i]}: Price={row['Close']:.2f}, Pattern={row['Pattern']}, ML={ml_confidence}")
        # elif sell_cond and ml_confidence > 0.75:
        #     df.at[df.index[i], 'Signal'] = -1
        #     # print(f"[SELL-ML] Signal at {df.index[i]}: Price={row['Close']:.2f}, Pattern={row['Pattern']}, ML={ml_confidence}")
        
        # if df['Signal'] != 0:
        #     reasons = []
        #     if breakout_buy or breakout_sell:
        #         reasons.append("Breakout")
        #     if gap_buy or gap_sell:
        #         reasons.append("Gap")
        #     if mean_reversion_buy or mean_reversion_sell:
        #         reasons.append("MeanReversion")
        #     if row['Pattern']:
        #         reasons.append(row['Pattern'])
        #     df.at[df.index[i], 'Strategy_Reason'] = ', '.join(reasons)

    df['Stop_Loss'] = df['Close'] * (1 - sl_pct)
    df['Take_Profit'] = df['Close'] * (1 + tp_pct)
    df['Risk_Amount'] = risk_per_trade

    return df.dropna()
