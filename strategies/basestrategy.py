# strategies/baseStrategy.py

from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, candle_builder, executor=None):
        self.candle_builder = candle_builder
        self.executor = executor

    @abstractmethod
    def evaluate(self, symbol):
        """Run on each tick or candle update"""
        pass

    def set_executor(self, executor):
        self.executor = executor
    


class StrategyManager:
    def __init__(self, candle_builder, executor=None):
        self.candle_builder = candle_builder
        self.executor = executor
        self.strategies = []
        self.selector = StrategySelector()

    def add_strategy(self, strategy):
        strategy.set_executor(self.executor)
        self.strategies.append(strategy)

    def evaluate(self, symbol):
        df = self.candle_builder.get_recent_df(symbol, lookback=30)
        if df is None or len(df) < 20:
            return

        active_strategy_name = self.selector.detect(df)

        for strategy in self.strategies:
            if strategy.name == active_strategy_name:
                strategy.evaluate(symbol)


class StrategySelector:
    def __init__(self):
        self.market_state = {}

    def detect(self, df):
        if "rsi" not in df.columns or "close" not in df.columns:
            return "none"

        latest = df.iloc[-1]
        rsi = latest["rsi"]

        # Estimate volatility using rolling Std Dev
        df["volatility"] = df["close"].rolling(window=14).std()
        volatility = df["volatility"].iloc[-1]

        # Simple logic (tune later):
        if volatility > 20 and rsi > 60:
            return "breakout"
        elif volatility < 10 and abs(rsi - 50) < 5:
            return "meanreversion"
        else:
            return "none"


