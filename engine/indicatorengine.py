
import pandas as pd
import ta

class IndicatorEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def add_rsi(self, period=14):
        self.df["rsi"] = ta.momentum.RSIIndicator(close=self.df["close"], window=period).rsi()
        return self

    def add_vwap(self):
        typical_price = (self.df["high"] + self.df["low"] + self.df["close"]) / 3
        volume = self.df["tick_count"] if "tick_count" in self.df.columns else 1
        self.df["vwap"] = (typical_price * volume).cumsum() / volume.cumsum()
        return self

    def add_zscore(self, period=20):
        self.df["mean"] = self.df["close"].rolling(window=period).mean()
        self.df["std"] = self.df["close"].rolling(window=period).std()
        self.df["zscore"] = (self.df["close"] - self.df["mean"]) / self.df["std"]
        return self

    def result(self):
        return self.df
