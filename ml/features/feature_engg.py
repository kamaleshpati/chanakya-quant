import pandas as pd
import ta  

def create_features_labels(df: pd.DataFrame):
    df = df.copy()
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    df['ema_50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
    df['macd'] = ta.trend.MACD(df['close']).macd_diff()
    df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()

    df.dropna(inplace=True)

    X = df[['rsi', 'ema_50', 'macd', 'atr']]
    y = (df['close'].shift(-1) > df['close']).astype(int)  

    return X, y

def create_features_only(df: pd.DataFrame):
    df = df.copy()
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    df['ema_50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
    df['macd'] = ta.trend.MACD(df['close']).macd_diff()
    df['atr'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['close']).average_true_range()

    df.dropna(inplace=True)
    X = df[['rsi', 'ema_50', 'macd', 'atr']]
    return X
