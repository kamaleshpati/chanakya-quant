# strategies/meanReversionStrategy.py

import pandas as pd
from strategies.basestrategy import BaseStrategy
from engine.indicatorengine import IndicatorEngine
from utils.logger import log

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, candle_builder, executor=None, z_threshold=1.5):
        super().__init__(candle_builder, executor)
        self.name = "meanreversion"
        self.z_threshold = z_threshold
        self.last_signal = {}

    def evaluate(self, symbol):
        candles = self.candle_builder.get_recent(symbol, lookback=30)
        if len(candles) < 20:
            return

        df = pd.DataFrame(candles)
        df = IndicatorEngine(df).add_zscore().result()

        latest = df.iloc[-1]
        z = latest["zscore"]
        ts = latest["timestamp"]

        if abs(z) > self.z_threshold:
            direction = "BUY" if z < 0 else "SELL"
            log(f"🔁 Mean Reversion Triggered for {symbol} | Z-Score: {z:.2f} | {direction}")

            if ts != self.last_signal.get(symbol):
                self.last_signal[symbol] = ts
                if self.executor:
                    self.executor.place_order(symbol, qty=1, side=direction)
