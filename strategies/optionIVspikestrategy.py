# strategies/optionIVSpikeStrategy.py

from strategies.basestrategy import BaseStrategy
from utils.logger import log

class OptionIVSpikeStrategy(BaseStrategy):
    def __init__(self, candle_builder, executor=None, iv_threshold=12):
        super().__init__(candle_builder, executor)
        self.name = "ivspike"
        self.iv_threshold = iv_threshold
        self.last_signal = {}

    def get_option_data(self, symbol):
        # 🚧 STUB: Replace with real-time IV, delta, OI fetch
        return {
            "iv_change": 14.8,
            "delta": 0.55,
            "timestamp": "2025-07-12T11:01:00"
        }

    def evaluate(self, symbol):
        option_data = self.get_option_data(symbol)
        if not option_data:
            return

        iv_change = option_data["iv_change"]
        delta = option_data["delta"]
        ts = option_data["timestamp"]

        if iv_change > self.iv_threshold and 0.3 < delta < 0.7:
            if ts != self.last_signal.get(symbol):
                self.last_signal[symbol] = ts
                log(f"⚡ IV Spike Detected: {symbol} | Δ={delta}, IV↑ {iv_change:.2f}%")
                if self.executor:
                    self.executor.place_order(symbol, qty=1, side="BUY")
