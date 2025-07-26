import ta

def rsi_mean_reversion(df, rsi_period=14, lower=30, upper=70):
    df = df.copy()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], rsi_period).rsi()
    
    df['Signal'] = 0
    df.loc[df['RSI'] < lower, 'Signal'] = 1  # Buy
    df.loc[df['RSI'] > upper, 'Signal'] = -1 # Sell
    df['Position'] = df['Signal'].diff()
    return df