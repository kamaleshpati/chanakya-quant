# chanakya-quant

## 📊 Annual Performance Metrics
| Year | Total Return (%) | Final Capital (₹) | Sharpe Ratio | Max Drawdown (₹) | Total Trades |
| ---- | ---------------- | ----------------- | ------------ | ---------------- | ------------ |
| 2016 | 49.05%           | ₹149,049.25       | 2.71         | ₹8,819.20        | 718          |
| 2017 | 8.88%            | ₹162,283.30       | 1.08         | ₹8,603.05        | 756          |
| 2018 | 32.53%           | ₹215,071.85       | 2.35         | ₹12,192.25       | 713          |
| 2019 | 18.46%           | ₹254,764.80       | 1.50         | ₹15,635.40       | 714          |
| 2020 | 99.61%           | ₹508,535.25       | 2.65         | ₹46,431.90       | 775          |
| 2021 | 58.14%           | ₹804,193.95       | 3.29         | ₹24,753.00       | 734          |
| 2022 | 68.55%           | ₹1,355,487.50     | 3.55         | ₹40,808.10       | 741          |
| 2023 | 20.69%           | ₹1,635,894.85     | 2.12         | ₹82,592.00       | 722          |
| 2024 | 24.49%           | ₹1,980,193.10     | 1.91         | ₹22,075.45       | 756          |


## 📌 Pattern Detection Used:
The strategy incorporates multiple candlestick and volume breakout patterns:

* ✅ Bullish Engulfing

* ✅ Bearish Engulfing

* ✅ Morning Star

* ✅ Evening Star

* ✅ Hammer

* ✅ Inverted Hammer

* ✅ Doji with Volume Breakout

* ✅ Inside Bars


## 📈 Future Enhancements & Roadmap
This section outlines potential upgrades to improve signal quality, robustness, and overall strategy performance.

### 🔧 1. Signal Quality & Filtering Enhancements
*** ✅ Technical Filters (Momentum, Volatility, Trend) ***
EMA Filter: Only execute long trades above 50/200 EMA to align with trend.

RSI / MACD Confirmation: Add logic to validate reversal signals when RSI < 30 or during bullish MACD crossover.

ATR Volatility Filter: Avoid trades when ATR is below threshold (low-volatility zones).

*** ✅ Multi-Timeframe Confirmation ***
Validate signal on base timeframe (e.g., 15 min) only if trend confirms on higher timeframes like 1H or 1D.

### 📊 2. Position Sizing & Risk Management
*** ✅ ATR-Based Dynamic SL/TP ***
Implement stop loss and take profit using:

```

SL = Entry - (1.5 * ATR)
TP = Entry + (2 * ATR)

```
*** ✅ Kelly Criterion / Volatility-Based Sizing *** 
Adjust trade size based on:

* Signal confidence

* Historical win rate

* Market volatility

*** ✅ Circuit Breaker Logic *** 
If cumulative drawdown > X%, reduce position size or halt trading temporarily.

### 🧠 3. Machine Learning / AI Integration
*** ✅ ML Classifier for Signal Validation *** 
Train models like RandomForest, XGBoost, or LSTM using features:

* OHLCV data

* Pattern type

* Preceding trend characteristics

* Predict profitability of a trade before execution.

*** ✅ Clustering Candlestick Sequences *** 
* Use unsupervised learning (KMeans, DBSCAN, TSLearn) to:

* Discover profitable pattern clusters

* Explore hidden relationships between candles

### 📦 4. Data & Execution Improvements
*** ✅ Options & Futures Data *** 
Incorporate derivative data to:

* Identify strong sentiment

* Hedge directional trades

* Implement straddle/strangle setups

*** ✅ Broker API Integration *** 
Add real-time data feed and live execution support via APIs like:

* Zerodha Kite Connect

* Interactive Brokers

* Enable paper trading mode for live forward testing

### 💹 5. Strategy Diversification
*** ✅ Additional Strategy Modules *** 
Breakout Strategies: Identify range breakouts using price & volume

* Mean Reversion: Use Bollinger Bands or RSI divergence

* Gap Trading: Detect and trade opening gaps with volume confirmation

* News/Volume Spike: Leverage sudden changes in volume or news sentiment



### Current improvement plans

✅ RSI < 30 / MACD Bullish Cross (Signal Quality filter)

✅ ATR filter (Avoid trades during low volatility)

✅ Higher Timeframe (5m) confirmation using 1m data

✅ Only trade long signals above 50 EMA

✅ Add SuperTrend signal

✅ Print logs when Buy/Sell patterns trigger
