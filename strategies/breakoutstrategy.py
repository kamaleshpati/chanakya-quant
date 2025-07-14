# strategies/breakoutStrategy.py

import pandas as pd
import ta

from strategies.baseStrategy import BaseStrategy
from utils.logger import log

class BreakoutStrategy(BaseStrategy):
    def __init__(self, candle_builder, executor=None, min_rsi=60):
        super().__init__(candle_builder, executor)
        self.name = "breakout"
        self.min_rsi = min_rsi
        self.last_signal = {}  # {symbol: timestamp} to avoid duplicate entries

    def evaluate(self, symbol):
        candles = self.candle_builder.get_recent(symbol, lookback=20)
        if len(candles) < 10:
            return  # Not enough data

        df = pd.DataFrame(candles)
        df['vwap'] = ((df['high'] + df['low'] + df['close']) / 3).rolling(5).mean()
        df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # Condition: Close > VWAP + RSI > 60 (Breakout)
        if latest['close'] > latest['vwap'] and latest['rsi'] > self.min_rsi:
            last_time = self.last_signal.get(symbol)
            if last_time != latest['timestamp']:
                log(f"📈 BREAKOUT detected on {symbol} @ {latest['close']} | RSI: {latest['rsi']:.1f}")
                self.last_signal[symbol] = latest['timestamp']

                if self.executor:
                    self.executor.place_order(symbol, qty=1, side="BUY")
