# Pendekatan Baru — Weighted System V2

> Ringkasan lengkap setelah diskusi: dari Weighted Matrix menuju Adaptive 4-Layer System dengan Logistic Regression.

---

## 1. Filosofi

```
Sistem lama:    "Kumpulkan poin sebanyak-banyaknya, entry kalau ≥ 100"
Sistem baru:    "Pahami market dulu → tentukan arah → hitung confidence → keluar dengan benar"
```

No single indicator is perfect. Tapi juga tidak semua indikator perlu di-scoring — setiap indikator harus punya **peran jelas** di salah satu layer.

---

## 2. Arsitektur 4-Layer

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     ADAPTIVE WEIGHTED SYSTEM V2                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  REGIME ───▶ DIRECTION ───▶ CONFIDENCE ───▶ EXIT                        │
│  (Layer 1)     (Layer 2)      (Layer 3)       (Layer 4)                 │
│                                                                          │
│  Apa market    Ke mana        Seberapa       Kapan keluar?               │
│  sedang apa?   arahnya?       yakin?                                     │
└──────────────────────────────────────────────────────────────────────────┘
```

### Layer 1 — Market Regime (Apa kondisi pasar?)

**Tujuan:** Menentukan tipe pasar saat ini, lalu mengadaptasi parameter layer di bawahnya.

| Input | Output |
|-------|--------|
| ADX, Choppiness Index, Hurst Exponent, ATR %Rank | `trending`, `ranging`, atau `volatile` |

**Komponen:**

| Indikator | Peran |
|-----------|-------|
| **ADX** | Trend strength (0-100). > 25 = trending |
| **Choppiness Index** | CI < 38.2 = trending, ≥ 38.2 = ranging |
| **Hurst Exponent** | H > 0.5 = trending, H < 0.5 = mean-reversion |
| **ATR %Rank** | Volatility percentile. > 70% = high vol, < 30% = low vol |

**Adaptive Parameters (ditentukan oleh Layer 1):**

| Parameter | Trending | Ranging | Volatile |
|-----------|----------|---------|----------|
| Entry threshold | 60 | 80 | 70 |
| Pyramid multiplier | 5 | 8 | 10 |
| Max pyramid | 5 | 3 | 2 |
| Exit method | ST3 | Scoring | ST1/ATR |
| ADX filter | aktif | nonaktif | aktif |
| CI filter | nonaktif | aktif | nonaktif |

---

### Layer 2 — Direction Filter (Ke mana arahnya?)

**Tujuan:** Menentukan arah trading — LONG, SHORT, atau SKIP.

| Komponen | Bobot | Cara Kerja |
|----------|-------|------------|
| **EMA 50/200** | 30% | Close > EMA50 > EMA200 → bullish. Kebalikannya → bearish |
| **3× Supertrend** | 40% | Majority vote dari 3 ST. greenCount vs redCount |
| **Higher TF bias** | 30% | Trend dari timeframe lebih besar (misal: H1 untuk entry M15) |
| **Price Action** | konfirmasi | HH/HL count, swing distance (tambahan) |

**Gating Logic:**

```python
if direction == "neutral":        # ST split 2-1, EMA mixed
    SKIP — no trade
elif conviction < 40:              # Meskipun ada arah, tapi lemah
    SKIP — not confident enough
else:
    PROCEED to Layer 3
```

---

### Layer 3 — Entry Confidence (Seberapa yakin?)

**Tujuan:** Menghitung confidence score dan memutuskan entry — pakai **Mode Hybrid**.

```
Layer 3a: Manual Scoring       → normalized score (0-100)
Layer 3b: Logistic Regression  → P(win)

Entry if: score ≥ regime_threshold AND P(win) ≥ 0.60
```

#### Manual Scoring — 6 Kategori (dari sistem existing, dinormalisasi)

| Kategori | Maks Raw | Normalized | Sumber Indikator |
|----------|----------|------------|------------------|
| Supertrend | 55 | 14.7 | ST1/2/3 flip, alignment, persistence |
| Stochastic RSI | 90 | 24.0 | K cross D, oversold, K > 50 |
| EMA | 80 | 21.3 | Distance, slope, crossover |
| ADX/DMI | 105 | 28.0 | Threshold, DI cross, dominance |
| Choppiness Index | 15 | 4.0 | CI < 30, CI turun |
| Persistence | 30 | 8.0 | ST, Stoch, ADX, EMA berkelanjutan |
| **Total** | **~375** | **100.0** | |

**Tambahan Baru:**

| Kategori | Maks | Sumber |
|----------|------|--------|
| Candlestick Patterns | 15 | Engulfing, Hammer, Pin Bar, Doji, 3 Soldiers |
| Price Action | 15 | Inside bar, range contraction, HH/HL |
| MFI | 10 | Volume confirmation |
| MACD | 15 | Histogram slope, divergence |

**Normalization:** `confidence = raw_score / max_possible * 100`

#### Logistic Regression

**Kenapa Logistic Regression?**

| Manual Scoring | Logistic Regression |
|---------------|-------------------|
| Bobot: tebakan manusia (10, 5, 15, dll) | Bobot: dipelajari dari data historis |
| Output: skor 0-375 (arbitrer) | Output: P(win) 0-1 (probabilistik) |
| Tidak bisa deteksi feature tidak berguna | L1 regularization → feature selection otomatis |
| Threshold tetap 100 | Threshold dari ROC curve |

**Cara kerja:**

```
log_odds = β₀ + β₁·st_flip + β₂·ema_dist + β₃·adx + ...
P(win) = sigmoid(log_odds) = 1 / (1 + e^(-log_odds))
```

**Feature engineering — jangan kasi data mentah:**

| Lebih Baik | Daripada |
|-----------|----------|
| `ema_distance_pct = 1.8%` | `close > ema = True` |
| `rsi_dist_from_50 = +13` | `rsi = 63` |
| `price_to_st_atr = 0.35` | `st_green = True` |
| `atr_percentile_100 = 82%` | `atr = 1.5` |
| `ema_slope_angle = 24°` | `ema_slope = 2.4` |

**Roadmap ML:**

```
Phase 1: Logistic Regression (baseline)
    ↓ evaluasi: AUC, precision, profit curve
Phase 2: Regime-specific models (3 model terpisah)
    ↓ kalau masih kurang
Phase 3: XGBoost / LightGBM (hanya jika terbukti perlu)
```

Jangan lompat ke XGBoost sebelum Logistic Regression terbukti mentok.

---

### Layer 4 — Exit Management (Kapan keluar?)

**Tujuan:** Mengelola exit dengan 11 metode.

| Metode | Cocok untuk Regime |
|--------|-------------------|
| Supertrend 1/2/3 | Trending |
| Score turun | Ranging |
| Score + EMA lewat | Ranging / Volatile |
| Bars Since Threshold | Semua |
| **ATR Trailing Stop** | **Volatile** |
| Partial TP | Semua |
| Breakeven | Semua |
| Time-based | Ranging |

**Baru:** Exit method auto-switch berdasarkan Layer 1.

---

## 3. Indicator Set — Final

### Core Indicators (15 indikator)

| # | Indikator | Layer | Kategori | Status |
|---|-----------|-------|----------|--------|
| 1 | EMA | 2, 3 | Moving Average | ✅ Selesai |
| 2 | RSI | 3 | Momentum | ✅ Selesai |
| 3 | Stochastic | 3 | Momentum | ✅ Selesai |
| 4 | Stochastic RSI | 3 | Momentum | ✅ Selesai |
| 5 | Supertrend (×3) | 2, 3 | Trend | ✅ Selesai |
| 6 | ADX + DMI | 1, 3 | Trend | ✅ Selesai |
| 7 | ATR | 1, 4 | Volatility | ✅ Selesai |
| 8 | Choppiness Index | 1 | Trend | ⬜ TODO |
| 9 | Hurst Exponent | 1 | Trend | ⬜ TODO |
| 10 | ATR %Rank | 1 | Volatility | ⬜ TODO |
| 11 | Bollinger Bands | 1, 3 | Volatility | ⬜ TODO |
| 12 | MACD | 3 | Momentum | ⬜ TODO |
| 13 | MFI | 3 | Volume | ⬜ TODO |
| 14 | Candlestick Patterns | 3 | Price Action | ⬜ TODO |
| 15 | Price Action Features | 2, 3 | Price Action | ⬜ TODO |

### Dihapus (redundan / tidak diperlukan)

| Indikator | Alasan |
|-----------|--------|
| WMA, VWMA | EMA sudah cukup |
| Parabolic SAR | Sama fungsi dengan Supertrend |
| Ichimoku | Terlalu kompleks, redundan dengan EMA + ST |
| Keltner Channel | Identik dengan Bollinger Bands |
| Donchian Channel | Informasi minimal untuk scoring |
| CMF | MFI lebih standard (bounded 0-100) |

### Deprioritized (low priority — dikerjakan jika nanti perlu)

SMA, CCI, ROC, Momentum, OBV

---

## 4. Dataset Pipeline

Setiap trade disimpan sebagai satu baris untuk training Logistic Regression:

```
| EMA_dist | RSI_50 | ADX | DI_dom | ST_flip | CI | ATR_pct | BB_W | MFI | Candl | Win |
|----------|--------|-----|--------|---------|-----|---------|------|------|-------|-----|
|   1.8    |  +13   | 34  |  +12   |    1    | 28  |   82    | 0.4  |  65  |   1   |  1  |
|  -0.5    |   -7   | 18  |   -5   |    0    | 45  |   45    | 1.2  |  42  |   0   |  0  |
```

**Pipeline lengkap:**

```
OHLCV → Indicators → Feature Engineering → Label Creation → Train/Val/Test Split
                                                                    ↓
                                                            Logistic Regression
                                                                    ↓
                                                            Evaluasi + Threshold
```

---

## 5. Evolution Path

```
Weighted Matrix (PineScript — current)
        ↓
Adaptive 4-Layer + Manual Scoring (Python — Phase 1)
        ↓
+ Logistic Regression hybrid (Phase 2)
        ↓
+ Regime-specific models (Phase 3)
        ↓
+ XGBoost (Phase 4 — hanya jika terbukti perlu)
```

Setiap phase adalah **foundation** untuk phase berikutnya. Jangan lompat.

---

## 6. Prioritas Implementasi

### Sekarang — Foundation
```
[ ] Isi pyproject.toml dengan dependencies (pandas, numpy, scikit-learn, ta)
[ ] Choppiness Index
[ ] Hurst Exponent
[ ] ATR %Rank
```

### Phase 1 — Layer 1 & 2
```
[ ] Regime classifier (ADX + CI + Hurst + ATR %Rank)
[ ] Adaptive parameter mapping per regime
[ ] Direction filter (EMA 50/200 + 3×ST + HTF bias)
[ ] Conviction scoring + gating logic
```

### Phase 2 — Layer 3 (Manual Scoring)
```
[ ] Scoring engine migration (6 kategori dari PineScript)
[ ] Normalisasi 0-100
[ ] Dynamic threshold per regime
[ ] Candlestick patterns (Engulfing, Hammer, Pin Bar, Doji, 3 Soldiers)
[ ] Price action features (HH/HL, inside bar, range contraction)
[ ] Entry methods: Single, Pyramid, Grid
```

### Phase 3 — Layer 3 (Machine Learning)
```
[ ] Dataset pipeline (OHLCV → Features → Labels)
[ ] Feature engineering (distance, slope, percentile, interaction)
[ ] Logistic Regression baseline
[ ] Hybrid mode: manual scoring + LR confirmation
[ ] Evaluasi: LR vs Manual Scoring
```

### Phase 4 — Layer 4
```
[ ] 7 exit methods dari PineScript
[ ] ATR trailing stop
[ ] Regime-adaptive exit method selection
```

### Phase 5 — Backtesting & Optimization
```
[ ] Backtesting engine
[ ] Walk-forward testing
[ ] Regime-specific models (3 model)
[ ] Threshold optimization via ROC curve
```

---

## 7. Ringkasan Perubahan dari Sistem Lama

| Aspek | Sistem Lama (PineScript) | Sistem Baru (Python V2) |
|-------|-------------------------|------------------------|
| **Struktur** | Monolitik, 1 file | 4 layer terpisah |
| **Filter** | CI + ADX embedded di scoring | Layer 1: Regime classifier independen |
| **Direction** | EMA200 embedded di kondisi entry | Layer 2: Direction filter dengan gating |
| **Scoring** | 375 max, threshold tetap 100 | Normalized 0-100, threshold adaptif per regime |
| **ML** | Tidak ada | Logistic Regression hybrid |
| **Feature** | Boolean mentah (True/False) | Feature engineered (distance, slope, percentile) |
| **Exit** | 7 methods, manual pilih | 11 methods, auto-switch based on regime |
| **Indikator** | ~28 indikator campur aduk | ~15 indikator, masing-masing punya peran jelas |
| **Price Action** | Tidak ada | Candlestick patterns + HH/HL + inside bar |
| **Dataset** | Tidak ada | Pipeline OHLCV → Features → Labels |
