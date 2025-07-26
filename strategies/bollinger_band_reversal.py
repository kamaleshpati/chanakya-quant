import ta

def bollinger_band_reversal(df, window=20, std_dev=2):
    df = df.copy()
    bb = ta.volatility.BollingerBands(df['Close'], window=window, window_dev=std_dev)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    
    df['Signal'] = 0
    df.loc[df['Close'] < df['bb_lower'], 'Signal'] = 1
    df.loc[df['Close'] > df['bb_upper'], 'Signal'] = -1
    df['Position'] = df['Signal'].diff()
    return df
