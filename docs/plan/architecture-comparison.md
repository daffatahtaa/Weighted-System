# Architecture Comparison & Proposed Design

> **Context:** Evaluating the current PineScript Weighted System vs. ChatGPT's proposed 3-layer architecture, and proposing a Hybrid 4-Layer Adaptive System for Python migration.

---

## 1. Current Architecture (PineScript Weighted System)

```
┌──────────────────────────────────────────────────────────┐
│                   WEIGHTED SYSTEM                        │
│                                                          │
│  [Filters: CI + ADX] ───▶ [Scoring Engine: ~375 max]     │
│                                │                         │
│                   [Direction: EMA200]                    │
│                                │                         │
│                        [Score ≥ 100?]                    │
│                                │                         │
│                       ┌────────┴────────┐                │
│                       │   ENTRY/EXIT    │                │
│                       └─────────────────┘                │
└──────────────────────────────────────────────────────────┘
```

### Characteristics

| Aspek | Detail |
|-------|--------|
| **Struktur** | Monolitik — semua logic dalam satu file PineScript |
| **Scoring** | Akumulasi poin positif dari 6 kategori (max ~375) |
| **Filter** | Choppiness Index + ADX (optional) |
| **Direction** | EMA200 sebagai filter arah (embedded di scoring) |
| **Exit** | 7 metode (ST1/2/3, Scoring, Bars Since, dll) |
| **Entry** | Single / Pyramid / Grid |
| **Regime** | Tidak ada pemisahan regime |

### Kelebihan
- ✅ Sistem scoring sudah teruji di TradingView
- ✅ 7 exit methods — fleksibel
- ✅ Pyramid entry yang terstruktur
- ✅ Multi-indicator consensus

### Kekurangan
- ❌ Semua logic campur aduk — sulit di-maintain
- ❌ Tidak ada regime-adaptive parameters
- ❌ Threshold scoring statis (selalu ≥ 100)
- ❌ Skor tidak ternormalisasi — tidak meaningful secara statistik
- ❌ Tidak ada higher timeframe context

---

## 2. ChatGPT 3-Layer Proposal

```
Layer 1 ──▶ Market Regime  ──▶ TRENDING / RANGING / VOLATILE / LOW VOLATILE
               ↓ (kalau not trending, STOP)
Layer 2 ──▶ Direction Filter ──▶ LONG / SHORT / NONE
               ↓ (kalau opposite direction, STOP)
Layer 3 ──▶ Entry Confidence ──▶ P(win)=84% → Trade
```

### Komponen per Layer

| Layer | Indikator | Output |
|-------|-----------|--------|
| **1 — Market Regime** | ADX, ATR, Choppiness Index, Hurst Exponent | TRENDING / RANGING / VOLATILE / LOW VOLATILE |
| **2 — Direction Filter** | EMA50, EMA200, Supertrend, Higher TF bias | LONG / SHORT / NONE |
| **3 — Entry Confidence** | RSI, MACD, Volume, Pullback, Breakout, Candle Pattern | P(win) disertai rekomendasi Trade/Skip |

### Analisis

#### ✅ Yang Lebih Baik dari Sistem Saat Ini

| Aspek | Rating | Alasan |
|-------|--------|--------|
| **Separation of concerns** | ✅✅ | 3 layer jelas, tiap layer punya tanggung jawab sendiri |
| **Regime detection** | ✅ | Menambahkan Hurst Exponent yang tidak ada di sistem saat ini |
| **Direction filter explicit** | ✅ | Layer terpisah, plus higher timeframe bias |
| **Gated architecture** | ✅ | Tiap layer bisa menghentikan eksekusi — tidak seperti scoring yang tetap jalan |
| **Probability output** | ⚠️ | Konsepnya bagus, implementasinya bermasalah (lihat di bawah) |

#### ❌ Kekurangan

| Masalah | Detail |
|---------|--------|
| **Layer 1 terlalu sempit** | Output kategorikal (TRENDING/RANGING/VOLATILE) — padahal regime itu spektrum. Lebih baik output berupa skala kontinu + klasifikasi. |
| **P(win) palsu tanpa data** | Tidak mungkin menentukan `P(win)=84%` tanpa backtest historis. Probability harus di-calculate dari data, bukan hardcoded. |
| **Scoring engine dibuang** | Sistem scoring ~375 poin sebenarnya bagus — tinggal di-normalize, bukan dibuang total. |
| **Tidak ada exit strategy** | Fokus cuma entry. Exit strategy adalah salah satu keunggulan sistem saat ini. |
| **Tidak regime-adaptive** | Threshold entry tetap sama di semua kondisi pasar. |
| **MACD + Volume** | Ini bagus sebagai tambahan, tapi tidak dijelaskan bobotnya. |

---

## 3. Proposed: Hybrid 4-Layer Adaptive System

### Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ADAPTIVE WEIGHTED SYSTEM                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  LAYER 1: MARKET REGIME                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ • ADX              → Trend Strength (0-100)                  │   │
│  │ • Choppiness Index → Trending vs Ranging                     │   │
│  │ • Hurst Exponent   → Mean-reversion vs Trending              │   │
│  │ • ATR %Rank        → Volatility Regime                       │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  Output: {regime: "trending"|"ranging"|"volatile",           │   │
│  │           trend_strength: 0-100,                             │   │
│  │           volatility: "low"|"normal"|"high"}                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                           │                                         │
│                           ▼ (parameter adaptif berdasarkan regime)  │
│  LAYER 2: DIRECTION FILTER                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ • EMA 50/200      → Trend alignment                          │   │
│  │ • 3× Supertrend   → Multi-level confirmation                 │   │
│  │ • Higher TF bias  → Context dari timeframe lebih besar       │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  Output: {direction: "long"|"short"|"neutral",               │   │
│  │           conviction: 0-100}                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                           │                                         │
│                           ▼ (kalau neutral → skip)                  │
│  LAYER 3: ENTRY CONFIDENCE                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ • Scoring Engine (existing ~375 system) → normalize 0-100    │   │
│  │ • Dynamic threshold: trending→60, ranging→80, volatile→70    │   │
│  │ • Probabilistic calibration via historical backtest          │   │
│  │ • Entry method: Single / Pyramid / Grid                      │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  Output: {should_enter: bool,                                │   │
│  │           confidence: 0-100,                                 │   │
│  │           prob_win: float (dari backtest)}                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                           │                                         │
│                           ▼                                         │
│  LAYER 4: EXIT MANAGEMENT                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ • 7 exit methods (existing)                                  │   │
│  │ • ATR trailing stop                                          │   │
│  │ • Time-based exit                                            │   │
│  │ • Partial TP / Breakeven                                     │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Layer 1 — Market Regime

**Tujuan:** Menentukan jenis pasar saat ini untuk mengadaptasi parameter di layer berikutnya.

#### Sub-layer 1a: Trend Regime

| Indikator | Fungsi |
|-----------|--------|
| **ADX** | Trend strength (0-100). ADX > 25 → trending |
| **Choppiness Index** | CI < 38.2 → trending. CI ≥ 38.2 → ranging |
| **Hurst Exponent** | H > 0.5 → trending. H ≈ 0.5 → random walk. H < 0.5 → mean-reversion |

#### Sub-layer 1b: Volatility Regime

| Indikator | Fungsi |
|-----------|--------|
| **ATR %Rank** | Posisi ATR saat ini dalam historical range. > 70% → high volatility. < 30% → low volatility |

#### Output

```python
{
    "regime": "trending" | "ranging" | "volatile",
    "trend_strength": float,  # 0-100
    "volatility": "low" | "normal" | "high",
    "hurst": float,
    "adx": float,
    "ci": float,
    "atr_percentile": float
}
```

#### Adaptive Parameters (ditentukan oleh Layer 1)

| Parameter | Trending | Ranging | Volatile |
|-----------|----------|---------|----------|
| Entry threshold | 60 | 80 | 70 |
| Pyramid multiplier | 5 | 8 | 10 |
| Max pyramid | 5 | 3 | 2 |
| Exit method | ST3 | Scoring | ST1/ATR |
| ADX filter | aktif | nonaktif | aktif |
| CI filter | nonaktif | aktif | nonaktif |

---

### Layer 2 — Direction Filter

**Tujuan:** Menentukan arah trading yang sesuai.

| Komponen | Bobot | Logika |
|----------|-------|--------|
| **EMA 50/200** | 30% | Close > EMA50 > EMA200 → bullish. Sebaliknya → bearish |
| **3× Supertrend** | 40% | Majority vote dari 3 ST. greenCount vs redCount |
| **Higher TF bias** | 30% | Trend dari timeframe lebih besar (misal: H1 untuk entry di M15) |

#### Output

```python
{
    "direction": "long" | "short" | "neutral",
    "conviction": float,  # 0-100
    "ema_alignment": float,
    "st_alignment": int,  # greenCount - redCount
    "htf_bias": "long" | "short" | "neutral"
}
```

#### Gating Logic

```python
if direction == "neutral":
    SKIP — no trade
elif conviction < 40:
    SKIP — not confident enough
else:
    PROCEED to Layer 3
```

---

### Layer 3 — Entry Confidence

**Tujuan:** Menghitung confidence score dan memutuskan entry.

#### Scoring Engine (dari sistem existing, di-adaptasi)

Kategori scoring yang sudah ada (dari PineScript):

| Kategori | Maks Skor | Normalized |
|----------|-----------|------------|
| Supertrend | 55 | 14.7 |
| Stochastic RSI | 90 | 24.0 |
| EMA | 80 | 21.3 |
| ADX/DMI | 105 | 28.0 |
| Choppiness Index | 15 | 4.0 |
| Persistence | 30 | 8.0 |
| **Total** | **~375** | **100.0** |

Normalization: `normalized_score = raw_score / 375 * 100`

#### Dynamic Threshold

```python
thresholds = {
    "trending": 60,
    "ranging": 80,
    "volatile": 70
}

should_enter = normalized_score >= thresholds[regime]
```

#### Probabilistic Calibration

Setelah backtest, hitung:
```python
prob_win = winning_trades_in_score_range / total_trades_in_score_range
```

Binning score:
| Score Range | Winrate (contoh) |
|-------------|-----------------|
| 60-70 | 52% |
| 70-80 | 58% |
| 80-90 | 67% |
| 90-100 | 78% |

#### Output

```python
{
    "should_enter": bool,
    "confidence": float,  # 0-100
    "prob_win": float,    # dari historical calibration, 0-1
    "entry_method": "single" | "pyramid" | "grid",
    "position_size": float
}
```

---

### Layer 4 — Exit Management

**Tujuan:** Mengelola exit berdasarkan metode yang dipilih.

#### Exit Methods (dari existing + tambahan)

| Metode | Logika | Adaptif Regime |
|--------|--------|----------------|
| **Supertrend 1** | Close crossunder/crossover ST1 | Trending |
| **Supertrend 2** | Close crossunder/crossover ST2 | Trending |
| **Supertrend 3** | Close crossunder/crossover ST3 | Trending |
| **Scoring** | Score turun di bawah threshold | Ranging |
| **Scoring + EMA** | Score lemah ATAU close melewati EMA | Ranging/Volatile |
| **Bars Since** | Score lemah > 2 bar | Semua |
| **Bars Since + EMA** | Score lemah > 2 bar DAN close melewati EMA | Semua |
| **ATR Trailing** | Trail stop based on ATR multiplier | Volatile |
| **Partial TP** | Take profit sebagian di level tertentu | Semua |
| **Breakeven** | Pindah SL ke breakeven setelah harga bergerak X ATR | Semua |
| **Time-based** | Exit setelah N bar jika belum profit | Ranging |

#### Output

```python
{
    "should_exit": bool,
    "exit_method": str,
    "exit_reason": str,
    "exit_price": float
}
```

---

## 4. Perbandingan Lengkap

| Kriteria | Current System | ChatGPT 3-Layer | Hybrid 4-Layer |
|----------|---------------|-----------------|----------------|
| **Separation of concerns** | ❌ Monolitik | ✅ 3 layer | ✅✅ 4 layer + sub-layer |
| **Regime detection** | ⚠️ CI + ADX (embedded) | ✅ CI + ADX + Hurst + ATR | ✅✅ CI + ADX + Hurst + ATR %Rank |
| **Regime-adaptive params** | ❌ Threshold tetap 100 | ❌ Threshold tetap | ✅ Threshold adaptif per regime |
| **Direction filter** | ⚠️ EMA200 (embedded) | ✅ EMA50/200 + ST + HTF | ✅✅ EMA50/200 + 3ST + HTF + conviction |
| **Scoring system** | ✅ ~375 max | ❌ Dibuang | ✅ Dipertahankan + dinormalisasi |
| **Probability** | ❌ Tidak ada | ⚠️ Angka palsu | ✅ Dari historical calibration |
| **Exit strategy** | ✅ 7 methods | ❌ Tidak ada | ✅✅ 11 methods |
| **Higher TF bias** | ❌ Tidak ada | ✅ Ada | ✅ Ada |
| **Backtest compatibility** | ✅ | ❌ | ✅ |
| **Extensibility** | ❌ Susah | ✅ Mudah | ✅✅ Mudah + adaptif |

---

## 5. Prioritas Migrasi

### Phase 1 — Foundation
```
[ ] Setup Python project structure (jika belum)
[ ] Configuration loader
[ ] Data pipeline (OHLCV loader, multi-TF support)
[ ] Indicator library → ADX, ATR, EMA, Supertrend, StochRSI, CI, Hurst
```

### Phase 2 — Layer 1: Market Regime
```
[ ] ADX trend strength
[ ] Choppiness Index
[ ] Hurst Exponent
[ ] ATR %Rank
[ ] Regime classifier
[ ] Adaptive parameter mapping
```

### Phase 3 — Layer 2: Direction Filter
```
[ ] EMA 50/200 alignment
[ ] 3× Supertrend consensus
[ ] Higher timeframe bias
[ ] Conviction scoring
```

### Phase 4 — Layer 3: Entry Confidence
```
[ ] Scoring engine migration (6 kategori)
[ ] Score normalization (0-100)
[ ] Dynamic threshold per regime
[ ] Probabilistic calibration
[ ] Entry methods: Single, Pyramid, Grid
```

### Phase 5 — Layer 4: Exit Management
```
[ ] 7 exit methods dari PineScript
[ ] ATR trailing stop
[ ] Partial TP / Breakeven
[ ] Time-based exit
```

### Phase 6 — Backtesting & Optimization
```
[ ] Backtesting engine
[ ] Walk-forward testing
[ ] Monte Carlo simulation
[ ] Auto weight optimization
[ ] ML integration (Random Forest / XGBoost)
```

---

## 6. Catatan Tambahan

### Hurst Exponent
Hurst Exponent adalah metrik yang mengukur *long-term memory* dari time series:

| Nilai H | Interpretasi |
|---------|-------------|
| H > 0.5 | Trending — seri memiliki memori jangka panjang |
| H ≈ 0.5 | Random walk — tidak dapat diprediksi |
| H < 0.5 | Mean-reversion — cenderung kembali ke rata-rata |

Implementasi: `numpy` + `polyfit` pada log-log plot R/S statistic.

### ATR %Rank
Bukan ATR mentah, tapi persentil posisi ATR dalam X periode terakhir:

```
ATR %Rank = (jumlah bar dengan ATR < current ATR) / total bar * 100
```

- ATR %Rank > 70 → High volatility → kurangi ukuran posisi
- ATR %Rank < 30 → Low volatility → bisa pakai tighter stops

### Probability Calibration
Jangan hardcode P(win). Cara yang benar:

1. Backtest strategy di historical data
2. Group hasil trade berdasarkan score range (60-70, 70-80, dll)
3. Hitung winrate per group
4. Simpan sebagai lookup table
5. Update secara periodik dengan data baru

```
P(win) = trades_menang_di_score_range_X / total_trades_di_score_range_X
```

---

## 7. Logistic Regression sebagai Entry Confidence (Layer 3)

### 7.1 Konsep Dasar

**Logistic Regression** adalah model klasifikasi probabilistik yang menggantikan *manual scoring* dengan bobot yang **dipelajari dari data historis**.

| Aspek | Manual Scoring | Logistic Regression |
|-------|---------------|-------------------|
| **Bobot** | Tebakan/eksperimen manual | Optimal dari data historis |
| **Output** | Skor 0-375 (arbitrer) | **P(win) 0-1** (probabilistik) |
| **Adaptif** | Threshold tetap 100 | Threshold dari ROC curve |
| **Interpretability** | ✅ Mudah | ✅ Koefisien bisa diinspeksi |
| **Data kebutuhan** | 0 (expert knowledge) | Butuh ~500-1000+ trades |
| **Regime change** | Manual adjust | Model bisa stale → perlu retrain |
| **Non-linear patterns** | Bisa dikoding manual | ❌ Linear decision boundary |

### 7.2 Cara Kerja

```
Manual Scoring:
    score = w1·f1 + w2·f2 + w3·f3 + ...   # w = fixed (10, 5, 15, dll)
    entry = score ≥ 100

Logistic Regression:
    log_odds = w0 + w1·f1 + w2·f2 + w3·f3 + ...   # w = learned from data
    P(win) = sigmoid(log_odds) = 1 / (1 + e^(-log_odds))
    entry = P(win) ≥ threshold
```

Perbedaan fundamental: bobot `w` tidak lagi tebakan manusia, tapi hasil optimasi dari data.

### 7.3 Feature Engineering

Features untuk Logistic Regression = semua kondisi yang sekarang di-scoring:

```python
features = {
    # ===== SUPERTREND FEATURES =====
    "st1_flip":         direction[1] > 0 and direction < 0,        # binary
    "st2_flip":         direction2[1] > 0 and direction2 < 0,      # binary
    "st3_flip":         direction3[1] > 0 and direction3 < 0,      # binary
    "green_count":      greenCount,                                 # int 0-3
    "st1_green":        direction < 0,                              # binary
    "st2_green":        direction2 < 0,                             # binary
    "st3_green":        direction3 < 0,                             # binary

    # ===== STOCHASTIC RSI FEATURES =====
    "stoch_k":          stochK,                                     # continuous 0-100
    "stoch_d":          stochD,                                     # continuous 0-100
    "stoch_k_cross_d":  crossover(stochK, stochD),                  # binary
    "stoch_k_above_50": stochK > 50,                                # binary
    "stoch_k_above_20": stochK > 20,                                # binary
    "stoch_k_rising":   stochK - stochK[1],                         # continuous
    "stoch_d_rising":   stochD - stochD[1],                         # continuous

    # ===== EMA FEATURES =====
    "ema_distance":     abs(close - ema200) / ema200 * 100,        # continuous %
    "ema_slope_1":      ema200 - ema200[1],                         # continuous
    "ema_slope_5":      ema200 - ema200[5],                         # continuous
    "ema_slope_10":     ema200 - ema200[10],                        # continuous
    "close_above_ema":  close > ema200,                             # binary
    "close_above_fast": close > fastEma,                            # binary
    "fast_ema_slope":   fastEma - fastEma[1],                       # continuous

    # ===== ADX/DMI FEATURES =====
    "adx":              adx,                                        # continuous
    "adx_above_25":     adx > 25,                                   # binary
    "adx_above_30":     adx > 30,                                   # binary
    "adx_accel":        (adx - adx[1]) - (adx[1] - adx[2]),        # continuous
    "di_plus":          diplus,                                     # continuous
    "di_minus":         diminus,                                    # continuous
    "di_dominance":     diplus - diminus,                           # continuous
    "di_cross_up":      crossover(diplus, diminus),                 # binary

    # ===== CHOPPINESS INDEX FEATURES =====
    "ci":               ci,                                         # continuous
    "ci_below_30":      ci < 30,                                    # binary
    "ci_falling":       ci - ci[1],                                 # continuous

    # ===== PERSISTENCE FEATURES =====
    "st_persistence":   direction < 0 and direction[1] < 0,         # binary
    "stoch_persistence": all(stochK[i] > stochK[i+1] for i in 3),  # binary
    "adx_persistence":  adx > adx[1] > adx[2],                     # binary
}
```

Total: **~30 features** — kombinasi binary dan continuous.

### 7.4 Implementasi

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import roc_auc_score, classification_report

class LogisticEntryModel:
    def __init__(self, C=0.1, penalty="l1", threshold=0.65):
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                penalty=penalty,     # L1 → feature selection otomatis
                C=C,                 # Regularization strength
                solver="saga",
                max_iter=1000,
                random_state=42
            ))
        ])
        self.threshold = threshold
        self.feature_names = None

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Konversi OHLCV + indikator ke feature matrix."""
        features = pd.DataFrame(index=df.index)

        # Supertrend
        features["st1_flip"] = (df["direction1"].shift(1) > 0) & (df["direction1"] < 0)
        features["st2_flip"] = (df["direction2"].shift(1) > 0) & (df["direction2"] < 0)
        features["st3_flip"] = (df["direction3"].shift(1) > 0) & (df["direction3"] < 0)
        features["green_count"] = (
            (df["direction1"] < 0).astype(int) +
            (df["direction2"] < 0).astype(int) +
            (df["direction3"] < 0).astype(int)
        )

        # Stochastic
        features["stoch_k"] = df["stoch_k"]
        features["stoch_k_cross_d"] = (
            (df["stoch_k"] > df["stoch_d"]) &
            (df["stoch_k"].shift(1) <= df["stoch_d"].shift(1))
        )
        features["stoch_k_above_50"] = df["stoch_k"] > 50

        # EMA
        features["ema_distance"] = abs(df["close"] - df["ema200"]) / df["ema200"] * 100
        features["close_above_ema"] = df["close"] > df["ema200"]
        features["ema_slope"] = df["ema200"] - df["ema200"].shift(1)

        # ADX
        features["adx"] = df["adx"]
        features["adx_above_25"] = df["adx"] > 25
        features["di_dominance"] = df["diplus"] - df["diminus"]
        features["di_cross_up"] = (
            (df["diplus"] > df["diminus"]) &
            (df["diplus"].shift(1) <= df["diminus"].shift(1))
        )

        # CI
        features["ci"] = df["ci"]
        features["ci_below_30"] = df["ci"] < 30

        self.feature_names = features.columns.tolist()
        return features

    def train(self, df: pd.DataFrame, target_col: str = "trade_win"):
        """
        Train model.
        target_col = 1 (win), 0 (loss).
        Hanya bar yang ada trade.
        """
        trade_mask = df["trade_signal"] != 0
        X = self.build_features(df[trade_mask])
        y = df.loc[trade_mask, target_col]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        self.pipeline.fit(X_train, y_train)

        # Evaluasi
        y_prob = self.pipeline.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_prob)
        print(f"Test AUC: {auc:.3f}")

        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Prediksi P(win) untuk bar terbaru."""
        X = self.build_features(df)
        return self.pipeline.predict_proba(X)[:, 1]

    def should_enter(self, df: pd.DataFrame) -> tuple:
        """Decision: entry or not."""
        prob = self.predict_proba(df.iloc[[-1]])[0]
        return prob >= self.threshold, prob

    def get_feature_importance(self) -> pd.DataFrame:
        """Lihat kontribusi tiap feature."""
        coef = self.pipeline.named_steps["classifier"].coef_[0]
        return pd.DataFrame({
            "feature": self.feature_names,
            "coef": coef,
            "abs_coef": abs(coef)
        }).sort_values("abs_coef", ascending=False)
```

### 7.5 Interpretasi Koefisien

Setelah training, Logistic Regression memberikan koefisien yang **langsung bisa dibaca**:

```python
model.get_feature_importance()
```

| Feature | Coefficient | Arti |
|---------|-------------|------|
| `di_dominance` | +2.1 | +DI > -DI → sangat bullish |
| `st1_flip` | +1.5 | ST1 flip → bullish |
| `stoch_k_cross_d` | +0.8 | K cross D → cukup bullish |
| `ema_distance` | -0.3 | Semakin jauh dari EMA → kurang bagus |
| `ci_below_30` | +0.2 | CI rendah → trending → positif |
| `stoch_k` | -0.1 | (L1 bisa nol-kan ini kalau tidak berguna) |

Dengan **L1 regularization**, feature yang tidak prediktif akan memiliki koefisien **0** — otomatis ter-drop.

Ini bisa jadi **validasi** apakah asumsi scoring manual kamu benar. Misalnya:

- Kalau kamu kasi `st1_flip = 10` poin tapi model kasi koefisien mendekati 0 → berarti ST1 flip sebenarnya tidak prediktif
- Kalau model kasi koefisien besar ke feature yang kamu kasi poin kecil → berarti kamu underestimate feature itu

### 7.6 Regime-Specific Models

Satu model untuk semua kondisi pasar kurang optimal. Solusi: **satu model per regime**.

```python
class RegimeAwareLogisticModel:
    def __init__(self):
        self.models = {
            "trending": LogisticEntryModel(C=0.1),
            "ranging":  LogisticEntryModel(C=0.5),   # lebih regularisasi di ranging
            "volatile": LogisticEntryModel(C=0.05),   # lebih konservatif di volatile
        }
        self.regime_history = []

    def train(self, df: pd.DataFrame, regimes: pd.Series):
        """Train satu model per regime."""
        for regime in self.models:
            mask = regimes == regime
            if mask.sum() < 100:
                print(f"Warning: {regime} only has {mask.sum()} samples")
                continue
            self.models[regime].train(df[mask])

    def predict(self, df: pd.DataFrame, regime: str) -> float:
        """P(win) berdasarkan regime saat ini."""
        return self.models[regime].predict_proba(df)[0]
```

### 7.7 Threshold Optimization

Threshold optimal tidak harus 0.5 — bisa dipilih dari **ROC curve**:

```python
from sklearn.metrics import roc_curve

def find_optimal_threshold(y_true, y_prob):
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)

    # Youden's J statistic
    j_scores = tpr - fpr
    best_idx = np.argmax(j_scores)

    # Atau: maximize profit
    # profit = tpr * win_gain - fpr * loss_cost

    return thresholds[best_idx]
```

Atau buat threshold **adaptif per regime** via backtest:

```python
thresholds = {
    "trending": optimize_threshold(X_trend, y_trend),   # misal: 0.60
    "ranging":  optimize_threshold(X_range, y_range),   # misal: 0.75
    "volatile": optimize_threshold(X_vol, y_vol),       # misal: 0.70
}
```

### 7.8 Integrasi dengan 4-Layer Architecture

Ada 2 opsi integrasi:

#### Option A: Replace Layer 3 Sepenuhnya

```
Layer 1 → Regime → adaptive params
Layer 2 → Direction → filter
Layer 3 → Logistic Regression → P(win)
Layer 4 → Exit
```

#### Option B: Hybrid — Manual Scoring + Logistic Regression

```
Layer 3a → Manual Scoring     → raw_score (0-100)
Layer 3b → Logistic Regression → P(win)

Entry if: raw_score ≥ regime_threshold AND P(win) ≥ 0.6
```

**Rekomendasi: Option B** — lebih aman. Sistem manual sudah terbukti di TradingView. Logistic Regression sebagai *confirmation overlay* mengurangi false positive.

### 7.9 Tradeoff & Peringatan

| Skenario | Risiko | Mitigasi |
|----------|--------|----------|
| **Data sedikit** (< 200 trades) | Koefisien tidak stabil, overfit | Gunakan L2 regularization kuat (C=0.01), atau stick ke manual scoring |
| **Market regime shift** | Model trained di trending gagal di ranging | Model per regime + periodic retrain (bulanan) |
| **Feature multicollinearity** | Koefisien tidak reliable | L1 regularization otomatis drop feature redundant |
| **Look-ahead bias** | Feature pakai data masa depan | Pastikan feature hanya dari data yang tersedia saat entry |
| **Class imbalance** (banyak loss) | Model bias predict "no trade" | Gunakan class_weight="balanced" atau threshold tuning |

### 7.10 Kapan Logistic Regression TIDAK Cocok

| Skenario | Masalah |
|----------|---------|
| **Feature non-linear murni** | Misal: "K cross D + oversold = 30 poin" — ini interaksi non-linear. Solusi: tambahkan interaction terms atau polynomial features |
| **Regime sangat dinamis** | Model perlu retrain setiap minggu — repot |
| **Belum punya data** | Jangan paksa. Mulai dengan manual scoring dulu, kumpulkan data, baru train model |
| **Black-box requirement** | Logistic Regression sebenarnya interpretable, tapi beberapa stakeholder mungkin tetap ingin scoring manual yang transparan |

### 7.11 Kesimpulan

| Kriteria | Manual Scoring | Logistic Regression | Hybrid (Recommended) |
|----------|---------------|-------------------|---------------------|
| **Mulai cepat** | ✅✅ Langsung | ❌ Butuh data | ✅ Manual dulu |
| **Bobot optimal** | ❌ Tebakan | ✅✅ Dari data | ✅✅ |
| **P(win) valid** | ❌ Tidak ada | ✅✅ | ✅✅ |
| **Interpretable** | ✅✅ | ✅ | ✅✅ |
| **Robust** | ✅ | ⚠️ Tergantung data | ✅✅ |
| **Feature selection** | ❌ Manual | ✅✅ Otomatis (L1) | ✅✅ |
| **Total** | **Mulai** | **Scale** | **Best of both** |
