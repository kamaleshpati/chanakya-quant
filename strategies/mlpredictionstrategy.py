# strategies/mlPredictionStrategy.py

import pandas as pd
from strategies.basestrategy import BaseStrategy
from utils.logger import log

class MLPredictionStrategy(BaseStrategy):
    def __init__(self, candle_builder, model, feature_builder, executor=None):
        super().__init__(candle_builder, executor)
        self.model = model
        self.feature_builder = feature_builder
        self.name = "mlprediction"

    def evaluate(self, symbol):
        candles = self.candle_builder.get_recent(symbol, lookback=30)
        if len(candles) < 20:
            return

        df = pd.DataFrame(candles)
        features = self.feature_builder.build(df)

        pred = self.model.predict_proba([features])[0][1]  # probability of upward move

        if pred > 0.65:
            log(f"🤖 ML Prediction: BUY {symbol} | Prob: {pred:.2f}")
            if self.executor:
                self.executor.place_order(symbol, qty=1, side="BUY")
