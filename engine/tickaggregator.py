# engine/tickAggregator.py

from collections import defaultdict
from datetime import datetime, timedelta
from utils.logger import log

class LiveCandleBuilder:
    def __init__(self, interval_sec=60):
        self.interval_sec = interval_sec
        self.active_candles = defaultdict(dict)  # {symbol: active_candle}
        self.history = defaultdict(list)         # {symbol: [candle1, candle2, ...]}

    def _get_candle_start_time(self, timestamp):
        rounded = timestamp.replace(second=0, microsecond=0)
        return rounded - timedelta(seconds=timestamp.second % self.interval_sec)

    def process_tick(self, symbol, price, timestamp):
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        start_time = self._get_candle_start_time(timestamp)
        candle = self.active_candles[symbol]

        if not candle or candle.get("start_time") != start_time:
            # Finalize previous if exists
            if candle:
                self._finalize_candle(symbol, candle)

            # Start new candle
            self.active_candles[symbol] = {
                "timestamp": start_time,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "tick_count": 1
            }
        else:
            # Update current
            candle["high"] = max(candle["high"], price)
            candle["low"] = min(candle["low"], price)
            candle["close"] = price
            candle["tick_count"] += 1

    def finalize_bar(self, now):
        symbols_to_finalize = []

        for symbol, candle in self.active_candles.items():
            start_time = candle["timestamp"]
            if now >= start_time + timedelta(seconds=self.interval_sec):
                self._finalize_candle(symbol, candle)
                symbols_to_finalize.append(symbol)

        for symbol in symbols_to_finalize:
            del self.active_candles[symbol]

    def _finalize_candle(self, symbol, candle):
        log(f"🕒 [{symbol}] Finalized OHLC @ {candle['timestamp'].strftime('%H:%M')} → "
            f"O:{candle['open']} H:{candle['high']} L:{candle['low']} C:{candle['close']} Ticks: {candle['tick_count']}")
        self.history[symbol].append(candle)

        # Optional: Keep only latest 100 bars
        if len(self.history[symbol]) > 100:
            self.history[symbol] = self.history[symbol][-100:]

    def get_recent(self, symbol, lookback=10):
        return self.history.get(symbol, [])[-lookback:]

    def get_recent_df(self, symbol, lookback=30):
        candles = self.get_recent(symbol, lookback)
        if not candles:
            return None
        return pd.DataFrame(candles)
