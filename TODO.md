# Weighted Trading System - TODO

## 1. Foundation

* [ ] Setup Python project structure
* [ ] Create configuration loader
* [ ] Create logger utility
* [ ] Add environment support (.env)
* [ ] Create common helper functions

---

## 2. Data Layer

* [ ] Implement OHLCV data loader
* [ ] Add CSV datasource
* [ ] Add TradingView export parser
* [ ] Add Binance datasource
* [ ] Add MT5 datasource
* [ ] Add data validation
* [ ] Add missing candle handler
* [ ] Add resampling utility
* [ ] Support multi-timeframe datasets

---

## 3. Indicator Migration

### Moving Average

* [x] EMA
* [ ] SMA
* [ ] WMA
* [ ] VWMA

### Momentum

* [ ] RSI
* [ ] Stochastic
* [ ] Stochastic RSI
* [ ] MACD
* [ ] CCI
* [ ] Momentum
* [ ] ROC

### Trend

* [ ] Supertrend
* [ ] ADX
* [ ] DMI
* [ ] Choppiness Index
* [ ] Parabolic SAR
* [ ] Ichimoku

### Volatility

* [ ] ATR
* [ ] Bollinger Bands
* [ ] Keltner Channel
* [ ] Donchian Channel

### Volume

* [ ] OBV
* [ ] CMF
* [ ] MFI
* [ ] VWAP

---

## 4. Scoring Engine

* [ ] Create generic score object
* [ ] Add positive weights
* [ ] Add negative weights
* [ ] Add persistence scoring
* [ ] Add decay scoring
* [ ] Add confidence normalization
* [ ] Add score history tracking
* [ ] Add net confidence calculation
* [ ] Add bullish confidence
* [ ] Add bearish confidence

Example:

bullish = 145

bearish = 35

net_score = bullish - bearish

net_score = 110

---

## 5. Current Strategy Migration

### Supertrend

* [ ] ST Flip
* [ ] Triple ST alignment
* [ ] Green count
* [ ] Persistence

### EMA

* [ ] Distance scoring
* [ ] EMA slope
* [ ] Fast EMA slope
* [ ] EMA crossover

### Stochastic RSI

* [ ] K>D
* [ ] K cross D
* [ ] Oversold recovery
* [ ] Momentum persistence

### ADX

* [ ] ADX threshold
* [ ] ADX acceleration
* [ ] DI crossover
* [ ] DI dominance

### Choppiness

* [ ] Trending condition
* [ ] Falling CI scoring

---

## 6. Entry Engine

* [ ] Single entry
* [ ] Pyramid entry
* [ ] Grid entry
* [ ] Dynamic pyramid thresholds
* [ ] Cooldown between entries
* [ ] Maximum exposure control
* [ ] Position sizing

---

## 7. Exit Engine

* [ ] Supertrend 1 exit
* [ ] Supertrend 2 exit
* [ ] Supertrend 3 exit
* [ ] Score exit
* [ ] Score + EMA exit
* [ ] BarsSince confidence exit
* [ ] ATR trailing stop
* [ ] Partial TP
* [ ] Break even
* [ ] Time based exit

---

## 8. Backtesting Engine

* [ ] Single symbol backtest
* [ ] Multi symbol backtest
* [ ] Walk-forward testing
* [ ] Monte Carlo simulation
* [ ] Slippage simulation
* [ ] Commission support
* [ ] Position statistics

Metrics:

* [ ] Net Profit
* [ ] CAGR
* [ ] Sharpe Ratio
* [ ] Sortino Ratio
* [ ] Profit Factor
* [ ] Winrate
* [ ] Expectancy
* [ ] Max Drawdown

---

## 9. Auto Weight Optimization

### Simple

* [ ] Winrate based weighting
* [ ] Expectancy weighting
* [ ] Profit factor weighting

### Statistical

* [ ] Correlation filtering
* [ ] Mutual information
* [ ] Feature importance

### Machine Learning

* [ ] Random Forest
* [ ] XGBoost
* [ ] LightGBM
* [ ] CatBoost

### Reinforcement Learning

* [ ] PPO
* [ ] DQN

---

## 10. Adaptive Weighting

* [ ] Train using previous year
* [ ] Validate current year
* [ ] Monthly recalibration
* [ ] Quarterly recalibration
* [ ] Rolling window optimization
* [ ] Regime detection

---

## 11. Visualization

* [ ] Score distribution chart
* [ ] Equity curve
* [ ] Indicator contribution chart
* [ ] Feature importance chart
* [ ] Trade heatmap
* [ ] Monthly returns table

---

## 12. Testing

* [ ] Unit tests indicators
* [ ] Unit tests scoring
* [ ] Unit tests entry engine
* [ ] Unit tests exits
* [ ] Integration tests
* [ ] Benchmark against TradingView

---

## 13. Research Ideas

* [ ] Add every TradingView default indicator
* [ ] Introduce negative confidence scoring
* [ ] Regime classifier
* [ ] Ensemble models
* [ ] Bayesian optimization
* [ ] Genetic Algorithm optimizer
* [ ] Explainable AI scoring
* [ ] Meta strategy selector

---

## 14. Production

* [ ] CLI runner
* [ ] Configuration profiles
* [ ] Docker support
* [ ] API endpoint
* [ ] Live paper trading
* [ ] MT5 execution bridge
* [ ] Exchange execution bridge
* [ ] Monitoring dashboard
