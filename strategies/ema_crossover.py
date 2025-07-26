def ema_crossover(df, fast=12, slow=26):
    df = df.copy()
    df['EMA_fast'] = df['Close'].ewm(span=fast).mean()
    df['EMA_slow'] = df['Close'].ewm(span=slow).mean()
    
    df['Signal'] = 0
    df.loc[fast:, 'Signal'] = (df['EMA_fast'] > df['EMA_slow']).astype(int).loc[fast:]
    df['Position'] = df['Signal'].diff()
    return df