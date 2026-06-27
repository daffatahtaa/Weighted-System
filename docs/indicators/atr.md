# ATR (Average True Range)

## Overview

**Average True Range (ATR)** adalah indikator volatilitas yang dikembangkan oleh **J. Welles Wilder** pada tahun 1978. Tidak seperti indikator tren, ATR **tidak menunjukkan arah** harga — ia hanya mengukur **seberapa besar** harga bergerak dalam suatu periode.

ATR membantu trader untuk:
- **Mengukur volatilitas** pasar secara objektif
- **Menentukan** level *stop-loss* yang adaptif
- **Mengidentifikasi** periode volatilitas tinggi/rendah
- **Menyesuaikan** ukuran posisi (*position sizing*) berdasarkan risiko

---

## Interpretasi

| Kondisi | Makna |
|---------|-------|
| ATR meningkat | Volatilitas membesar — potensi *breakout* atau *panic selling/buying* |
| ATR menurun | Volatilitas mengecil — pasar mulai *sideways* / konsolidasi |
| ATR tinggi | *Stop-loss* perlu lebih lebar dari biasanya |
| ATR rendah | *Stop-loss* bisa lebih ketat |

> ⚠️ ATR bersifat **relatif** — nilai 50 di saham A belum tentu sama artinya dengan nilai 50 di saham B. Bandingkan ATR dengan harga saat ini (ATR sebagai % harga) untuk perbandingan yang lebih adil.

---

## Step-by-Step Calculation

### Step 1: True Range (TR)

True Range adalah nilai terbesar dari tiga metode pengukuran pergerakan harga harian:

$$
\begin{aligned}
TR_t = \max(& \\
&\quad \text{High}_t - \text{Low}_t, \\
&\quad |\text{High}_t - \text{Close}_{t-1}|, \\
&\quad |\text{Low}_t - \text{Close}_{t-1}| \\
&)
\end{aligned}
$$

| Komponen | Deskripsi |
|----------|-----------|
| High - Low | Rentang harga intraday |
| \|High - prev Close\| | *Gap* naik dari close kemarin ke high hari ini |
| \|Low - prev Close\| | *Gap* turun dari close kemarin ke low hari ini |

Dalam kode:
```python
tr = pd.concat([
    (high - low).abs(),
    (high - prev_close).abs(),
    (low - prev_close).abs(),
], axis=1).max(axis=1)
```

### Step 2: Average True Range

ATR adalah rata-rata dari TR selama N periode. Ada dua metode:

#### Metode A: Simple Moving Average (SMA) — `use_wilder=False`

$$
ATR_t = \frac{1}{\text{length}} \sum_{i=1}^{\text{length}} TR_{t-i+1}
```

Implementasi:
```python
atr = tr.rolling(window=length).mean()
```

#### Metode B: Wilder's Smoothing — `use_wilder=True`

Mirip dengan metode yang digunakan di ADX. Nilai pertama adalah SMA, lalu:

$$
ATR_t = \frac{ATR_{t-1} \times (\text{length} - 1) + TR_t}{\text{length}}
```

Implementasi:
```python
# Wilder's smoothing
atr[i] = (atr[i-1] * (length - 1) + tr[i]) / length
```

---

## Cara Penggunaan dalam Kode

```python
import pandas as pd
from src.indicators.atr import atr

# Contoh data OHLC
data = pd.DataFrame({
    'high':  [...],
    'low':   [...],
    'close': [...],
})

# ATR dengan SMA (default)
atr_sma = atr(data, length=14, use_wilder=False)

# ATR dengan Wilder's smoothing
atr_wilder = atr(data, length=14, use_wilder=True)

print(atr_sma.tail())
```

### Output:
```
14    0.85
15    0.92
16    0.88
17    1.05
18    1.12
```

---

## ATR Sebagai Persentase Harga

Untuk membandingkan volatilitas antar aset, hitung ATR sebagai % harga:

```python
atr_pct = atr(data, length=14) / data['close'] * 100
print(f"ATR%: {atr_pct.iloc[-1]:.2f}%")
```

---

## Strategi & Penggunaan

### 1. Stop-Loss Adaptif

Gunakan ATR sebagai jarak stop-loss yang dinamis:

```python
entry_price = 100.0
current_atr = 2.5
atr_multiplier = 2.0

stop_loss = entry_price - (current_atr * atr_multiplier)
take_profit = entry_price + (current_atr * atr_multiplier * 2)  # 1:2 risk-reward
```

| Parameter | Arti |
|-----------|------|
| `atr_multiplier = 1.0` | Stop-loss ketat (scalping) |
| `atr_multiplier = 2.0` | Stop-loss standar (swing) |
| `atr_multiplier = 3.0` | Stop-loss longgar (trend) |

### 2. Position Sizing

Sesuaikan ukuran posisi berdasarkan ATR untuk menjaga risiko konsisten:

```python
risk_per_trade = 0.02  # 2% dari modal
account_balance = 10_000
current_atr = 2.5
atr_multiplier = 2.0

risk_amount = account_balance * risk_per_trade          # $200
stop_distance = current_atr * atr_multiplier             # $5
position_size = risk_amount / stop_distance              # 40 shares
```

### 3. Identifikasi Breakout

ATR yang menyempit diikuti pembesaran tiba-tiba sering menandakan *breakout*:

```python
atr_current = atr(data, length=14).iloc[-1]
atr_ma = atr(data, length=14).rolling(20).mean().iloc[-1]

if atr_current > atr_ma * 1.5:
    print("⚠️ Volatilitas melonjak — potensi breakout!")
```

---

## Perbandingan SMA vs Wilder's Smoothing

| Aspek | SMA | Wilder's Smoothing |
|-------|-----|-------------------|
| Bobot | Semua periode sama | Periode terbaru lebih berbobot |
| Responsivitas | Kurang responsif | Lebih responsif ke perubahan terbaru |
| Kompatibilitas | Banyak platform pakai ini | Sama dengan ADX, RSI Wilder |
| Cocok untuk | Analisis umum | Strategi yang menggunakan Wilder's smoothing (ADX, RSI) |

---

## Referensi

- Wilder, J. Welles. *New Concepts in Technical Trading Systems*. Trend Research, 1978.
- [Investopedia: Average True Range (ATR)](https://www.investopedia.com/terms/a/atr.asp)
- [StockCharts: ATR](https://school.stockcharts.com/doku.php?id=technical_indicators:average_true_range_atr)
