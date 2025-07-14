# integration/kiteIntegration.py

from datetime import datetime
from engine.tickaggregator import LiveCandleBuilder
from integration.kiteexecutor import KiteExecutor
from strategies.basestrategy import StrategyManager

from strategies.breakoutstrategy import BreakoutStrategy
from strategies.meanreversionstrategy import MeanReversionStrategy
from strategies.optionIVspikestrategy import OptionIVSpikeStrategy

from utils.logger import log

class KiteIntegration:
    def __init__(self, kite_connector, config):
        self.kite_connector = kite_connector
        self.executor = KiteExecutor(kite_connector.kite)
        self.candle_builder = LiveCandleBuilder(interval_sec=60)
        self.strategy = StrategyManager(self.candle_builder, self.executor)

        # Register strategies
        breakout = BreakoutStrategy(self.candle_builder)
        breakout.name = "breakout"
        self.strategy.add_strategy(breakout)

        meanrev = MeanReversionStrategy(self.candle_builder)
        meanrev.name = "meanreversion"
        self.strategy.add_strategy(meanrev)

        option_iv = OptionIVSpikeStrategy(self.candle_builder)
        option_iv.name = "ivspike"
        self.strategy.add_strategy(option_iv)

        log("📈 Strategies initialized: breakout, meanreversion, ivspike")

    def handle_tick(self, tick):
        symbol = tick["symbol"]
        price = tick["price"]
        timestamp = tick["timestamp"]

        self.candle_builder.process_tick(symbol, price, timestamp)
        self.strategy.evaluate(symbol)

    def finalize_bar(self, now: datetime):
        self.candle_builder.finalize_bar(now)
