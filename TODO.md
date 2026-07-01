# Weighted Trading System - TODO

## 1. Foundation

* [x] Setup Python project structure (pyproject.toml, Pipfile)
* [ ] Create configuration loader
* [ ] Create logger utility
* [ ] Add environment support (.env)
* [ ] Create common helper functions
* [ ] Isi pyproject.toml dengan dependencies (pandas, numpy, scikit-learn, ta)

---

## 1b. Market Regime (Layer 1)

* [ ] Hurst Exponent implementation
* [ ] ATR %Rank (percentile-based volatility)
* [ ] Regime classifier (ADX + CI + Hurst + ATR %Rank)
* [ ] Regime output: trending / ranging / volatile
* [ ] Adaptive parameter mapping per regime
* [ ] Regime-aware threshold selection

---

## 1c. Direction Filter (Layer 2)

* [ ] EMA 50/200 alignment scoring
* [ ] 3x Supertrend consensus (majority vote)
* [ ] Higher timeframe bias detection
* [ ] Conviction score (0-100)
* [ ] Neutral direction gating logic (skip trade)

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

## 2b. Dataset Pipeline for ML

* [ ] OHLCV → Indicators → Features pipeline
* [ ] Label creation (forward-looking return, N bar)
* [ ] Entry bar masking (hanya bar entry untuk training)
* [ ] Train/validation/test split (chronological, no look-ahead)
* [ ] Export dataset ke CSV untuk analisis manual

---

## 2c. Feature Engineering

* [ ] Distance-based features (% from EMA, ATR)
* [ ] Slope-based features (sudut kemiringan EMA dalam derajat)
* [ ] Volatility-adjusted features (price-to-ST in ATR units)
* [ ] Momentum features (RSI distance from 50)
* [ ] ADX quality features (normalized 0-1, momentum)
* [ ] Persistence features (bars since last flip)
* [ ] Interaction features (EMA + ST + ADX combo)
* [ ] Polynomial features (non-linear patterns: ADX squared)

---

## 3. Indicator Migration

### Moving Average

* [x] EMA
* [ ] SMA
* [ ] WMA
* [ ] VWMA

### Momentum

* [x] RSI (di stochastic_rsi.py)
* [x] Stochastic (di stochastic_rsi.py)
* [x] Stochastic RSI
* [ ] MACD
* [ ] CCI
* [ ] Momentum
* [ ] ROC

### Trend

* [x] Supertrend (src/indicators/supertrend.py)
* [x] ADX + DMI (src/indicators/adx.py — includes +DI, -DI, DX)
* [ ] Choppiness Index
* [ ] Parabolic SAR
* [ ] Ichimoku

### Volatility

* [x] ATR (src/indicators/atr.py — includes Wilder's smoothing option)
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
* [ ] Regime-adaptive exit method selection
* [ ] Exit method auto-switch based on Layer 1 regime

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

### Logistic Regression (Baseline)

* [ ] Dataset preparation (features + labels)
* [ ] L1 regularization (automatic feature selection)
* [ ] Regime-specific models (1 model per regime)
* [ ] Threshold optimization via ROC curve
* [ ] Probability calibration (Platt scaling)
* [ ] Coefficient analysis (feature importance)

### Tree-Based (Advanced)

* [ ] Random Forest
* [ ] XGBoost
* [ ] LightGBM
* [ ] CatBoost
* [ ] Model comparison: Logistic Regression vs Tree-based

### Reinforcement Learning

* [ ] PPO
* [ ] DQN

### Hybrid Decision Engine

* [ ] Manual scoring → normalized score (0-100)
* [ ] Logistic Regression → P(win)
* [ ] AND logic: score ≥ threshold AND P(win) ≥ threshold
* [ ] Conflict resolution (scoring bilang entry, LR bilang skip)
* [ ] Mode switching: manual-only / LR-only / hybrid

### Model Evaluation

* [ ] AUC-ROC score
* [ ] Precision / Recall / F1
* [ ] Confusion matrix
* [ ] Profit curve (threshold vs expectancy)
* [ ] Walk-forward validation
* [ ] Time series cross-validation

---

## 10. Adaptive Weighting

* [ ] Train using previous year
* [ ] Validate current year
* [ ] Monthly recalibration
* [ ] Quarterly recalibration
* [ ] Rolling window optimization
* [ ] Regime-aware threshold calibration
* [ ] Adaptive pyramid per regime (size, multiplier)
* [ ] Adaptive exit method per regime
* [ ] Periodic retrain schedule (monthly / quarterly)

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

## 12b. Src Structure

* [ ] `src/core/` — masih kosong
* [ ] `src/features/` — masih kosong
* [ ] `src/datasource/` — masih kosong
* [ ] `src/backtest/` — masih kosong
* [ ] `src/ml/` — masih kosong
* [ ] `src/optimizer/` — masih kosong
* [ ] `config/` — masih kosong
* [ ] `data/` — masih kosong
* [ ] `tests/` — masih kosong

---

## 13. Research Ideas

* [ ] Add every TradingView default indicator
* [ ] Introduce negative confidence scoring
* [ ] Ensemble models (stacking LR + XGBoost)
* [ ] Bayesian optimization for hyperparams
* [ ] Genetic Algorithm optimizer
* [ ] Explainable AI (SHAP / LIME untuk koefisien LR)
* [ ] Meta strategy selector
* [ ] Attention-based feature weighting
* [ ] Online learning (model update real-time)
* [ ] Multi-timeframe feature fusion

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
