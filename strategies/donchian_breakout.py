def donchian_breakout(df, window=20):
    df = df.copy()
    df['Upper'] = df['High'].rolling(window=window).max()
    df['Lower'] = df['Low'].rolling(window=window).min()
    
    df['Signal'] = 0
    df.loc[df['Close'] > df['Upper'].shift(1), 'Signal'] = 1
    df.loc[df['Close'] < df['Lower'].shift(1), 'Signal'] = -1
    df['Position'] = df['Signal'].diff()
    return df
