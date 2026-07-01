# Weighted Trading System

Weighted Trading System is a modular quantitative trading framework designed to combine multiple technical indicators into a unified confidence score.

The main philosophy is:

> No single indicator is perfect.
> Indicators should contribute weighted evidence toward a trading decision.

The system aims to provide:

* Flexible indicator scoring
* Confidence-based entries
* Multiple exit methodologies
* Automatic weight optimization
* Machine Learning integration
* Long historical backtesting support
* Migration compatibility from TradingView Pine Script

---

# Features

## Indicator Scoring

Every indicator contributes positive or negative confidence.

Example:

EMA200 Above Price
+20

Triple Supertrend Green
+35

ADX > 25
+20

Stoch RSI Bullish
+30

MACD Cross Up
+25

Bearish Divergence
-15

Weak Momentum
-10

Final confidence:

Bullish Score = 145

Bearish Score = 35

Net Confidence = 110

Trade decision:

Net Confidence >= Entry Threshold

→ Open Position

---

# Supported Indicators

## Trend

* EMA
* SMA
* WMA
* VWMA
* Supertrend
* ADX
* DMI
* Ichimoku
* Parabolic SAR

---

## Momentum

* RSI
* Stochastic
* Stochastic RSI
* MACD
* CCI
* ROC
* Momentum

---

## Volatility

* ATR
* Bollinger Bands
* Keltner Channel
* Donchian Channel

---

## Volume

* OBV
* CMF
* MFI
* VWAP

---

# Documentation

Dokumentasi lengkap tersedia di folder `docs/`:

## Indicators

| Dokumen | Deskripsi |
|---------|-----------|
| [EMA](docs/indicators/ema.md) | Exponential Moving Average — fast & slow EMA |
| [Stochastic RSI](docs/indicators/stochastic_rsi.md) | StochRSI — RSI-based stochastic oscillator |
| [ADX](docs/indicators/adx.md) | Average Directional Index — trend strength |
| [ATR](docs/indicators/atr.md) | Average True Range — volatility measurement |
| [Supertrend](docs/indicators/supertrend.md) | Trend-following indicator with ATR bands |

## Strategy — Weighted System

| Dokumen | Deskripsi |
|---------|-----------|
| [Overview](docs/strategy/overview.md) | Arsitektur sistem, diagram alur, komponen utama |
| [Scoring Engine](docs/strategy/scoring-engine.md) | Detail scoring: Supertrend, StochRSI, EMA, ADX, CI, Persistence |
| [Entry Methods](docs/strategy/entry-methods.md) | Single entry, Pyramid entry, Grid entry |
| [Exit Methods](docs/strategy/exit-methods.md) | 7 metode exit: ST1/2/3, Scoring, Bars Since, dll |

---

# Architecture

```text
Weighted System

│
├── config/
│
├── data/
│
├── docs/
│   ├── indicators/
│   │   ├── adx.md
│   │   ├── atr.md
│   │   ├── ema.md
│   │   ├── stochastic_rsi.md
│   │   └── supertrend.md
│   └── strategy/
│       ├── overview.md
│       ├── scoring-engine.md
│       ├── entry-methods.md
│       └── exit-methods.md
│
├── src/
│   │
│   ├── datasource/
│   │
│   ├── indicators/
│   │
│   ├── features/
│   │
│   ├── core/
│   │
│   ├── backtest/
│   │
│   ├── optimizer/
│   │
│   └── ml/
│
└── tests/
```

---

# Scoring Engine

Indicators do not directly generate entries.

Instead they contribute confidence.

Example:

```python
score = 0

score += 20 if close > ema200 else 0

score += 15 if supertrend_green else 0

score += 10 if adx > 25 else 0

score += 25 if macd_cross else 0

score -= 15 if bearish_divergence else 0
```

Result:

```python
net_score = bullish_score - bearish_score
```

Example:

```python
Bullish = 135

Bearish = 25


Net = 110
```

---

# Entry Engine

Several entry models are supported.

## Single Entry

Single position only.

```text
Position = 0

Open Buy
```

---

## Pyramid

Increase exposure when confidence rises.

Example

```text
Threshold = 100


Trade 1

score >=100


Trade 2

score >=110


Trade 3

score >=120


Trade 4

score >=130
```

---

## Grid

Price based additions.

Example

```text
Trade 1

Trade 2 at -1 ATR


Trade 3 at -2 ATR


Trade 4 at -3 ATR
```

---

# Exit Engine

Supported methods

### Supertrend Exit

ST1

ST2

ST3

---

### Score Exit

```python
score < 50
```

---

### Score + EMA

```python
score < 50

or


close < ema200
```

---

### Persistence Exit

Example

```python
score < 50


for 3 bars
```

---

### ATR Exit

ATR Stop

ATR Trailing

---

### Break Even

Supported

---

### Partial Take Profit

Supported

---

# Backtesting

Metrics

Supported

Net Profit

CAGR

Profit Factor

Sharpe Ratio

Sortino Ratio

Winrate

Expectancy

Max Drawdown

Recovery Factor

Ulcer Index

Calmar Ratio

---

# Weight Optimization

## Static

Manual weights.

---

## Statistical

Feature Importance

Correlation Analysis

Mutual Information

Permutation Importance

---

## Machine Learning

Random Forest

LightGBM

CatBoost

XGBoost

---

## Reinforcement Learning

PPO

DQN

---

# Adaptive Weights

The system can retrain periodically.

Examples

Train:

2020-2024

Validate:

2025

Trade:

2026

Or

Rolling Window

```text
Train

Last 2 years


Trade

Current month


Retrain

Every Month
```

---

# Development Roadmap

Phase 1

Indicator migration

Phase 2

Scoring engine

Phase 3

Entry system

Phase 4

Exit engine

Phase 5

Backtester

Phase 6

Weight optimization

Phase 7

Machine learning

Phase 8

Adaptive retraining

Phase 9

Live execution

---

# Goal

The objective of this project is not to discover a perfect indicator.

The objective is to create a confidence aggregation framework capable of combining many weak signals into a robust decision-making process.

This project is inspired by concepts from:

* Ensemble Learning
* Factor Investing
* Quantitative Momentum
* Smart Money Concepts
* Adaptive Trading Systems
* Machine Learning Feature Engineering
