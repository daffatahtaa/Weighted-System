# Supertrend

## Overview

**Supertrend** adalah indikator *trend-following* yang dikembangkan oleh **Olivier Seban**. Indikator ini menggabungkan **Average True Range (ATR)** dengan harga *middle point* (HL/2) untuk menghasilkan garis yang mengikuti arah tren sekaligus memberikan sinyal *buy/sell*.

Supertrend membantu trader untuk:
- **Mengidentifikasi** arah tren saat ini (uptrend / downtrend)
- **Memberikan** sinyal entry/exit yang jelas
- **Beradaptasi** dengan volatilitas pasar melalui ATR

---

## Components (Komponen)

| Komponen | Deskripsi |
|----------|-----------|
| **Supertrend Line** | Garis yang mengikuti harga — posisinya di atas atau di bawah harga tergantung arah tren |
| **Trend Direction** | 1 = uptrend (garis di bawah harga), -1 = downtrend (garis di atas harga) |
| **Upper Band** | Batas atas: HL/2 + (multiplier × ATR) |
| **Lower Band** | Batas bawah: HL/2 - (multiplier × ATR) |

### Interpretasi Dasar:
- **Harga di atas Supertrend** → Uptrend (bullish)
- **Harga di bawah Supertrend** → Downtrend (bearish)
- **Sinyal buy** → Saat harga *close* menembus ke atas garis Supertrend
- **Sinyal sell** → Saat harga *close* menembus ke bawah garis Supertrend

---

## Step-by-Step Calculation

### Step 1: Average True Range (ATR)

Menghitung rata-rata True Range selama `atr_length` periode.

$$
\begin{aligned}
TR_t &= \max(
    \text{High}_t - \text{Low}_t,\;
    |\text{High}_t - \text{Close}_{t-1}|,\;
    |\text{Low}_t - \text{Close}_{t-1}|
) \\[4pt]
ATR_t &= \frac{1}{\text{atr\_length}} \sum_{i=1}^{\text{atr\_length}} TR_{t-i+1}
\end{aligned}
$$

### Step 2: Basic Bands

Menghitung *middle point* harga dan menambahkan/mengurangkan ATR:

$$
\begin{aligned}
HL2_t &= \frac{\text{High}_t + \text{Low}_t}{2} \\[4pt]
\text{UpperBand}_t &= HL2_t + (\text{multiplier} \times ATR_t) \\[4pt]
\text{LowerBand}_t &= HL2_t - (\text{multiplier} \times ATR_t)
\end{aligned}
$$

### Step 3: Trend Direction & Supertrend Line

Trend direction ditentukan berdasarkan posisi *close* terhadap garis Supertrend sebelumnya:

```
IF close[i] > supertrend[i-1] AND trend[i-1] == -1:
    → Reverse ke uptrend  (trend = 1)
ELIF close[i] < supertrend[i-1] AND trend[i-1] == 1:
    → Reverse ke downtrend (trend = -1)
ELSE:
    → Lanjutkan trend sebelumnya
```

Kemudian nilai supertrend ditentukan:

$$
\text{Supertrend}_t =
\begin{cases}
\max(\text{LowerBand}_t,\; \text{Supertrend}_{t-1}), & \text{if uptrend} \\[4pt]
\min(\text{UpperBand}_t,\; \text{Supertrend}_{t-1}), & \text{if downtrend}
\end{cases}
$$

> **Catatan:** Selama uptrend, garis Supertrend hanya bergerak naik (mengikuti lower band). Selama downtrend, garis hanya bergerak turun (mengikuti upper band). Ini yang membuat garis terlihat "halus".

---

## Parameter

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `atr_multiplier` | 3.0 | Semakin besar → garis semakin jauh dari harga (lebih jarang reversal) |
| `atr_length` | 10 | Periode untuk kalkulasi ATR |

### Tips Memilih Parameter:
- **Multiplier lebih kecil** (1.5–2.0) → lebih sensitif, lebih sering sinyal
- **Multiplier lebih besar** (3.0–5.0) → lebih selektif, lebih sedikit false signal
- **atr_length lebih kecil** → ATR lebih responsif terhadap volatilitas terbaru
- **atr_length lebih besar** → ATR lebih halus

---

## Cara Penggunaan dalam Kode

```python
import pandas as pd
from src.indicators.supertrend import supertrend

# Contoh data OHLC
data = pd.DataFrame({
    'high':  [...],
    'low':   [...],
    'close': [...],
})

result = supertrend(data, atr_multiplier=3.0, atr_length=10)
print(result.tail())
```

### Output:
| supertrend | trend | upper_band | lower_band |
|------------|-------|------------|------------|
| 152.50 | 1 | 155.20 | 152.50 |
| 153.10 | 1 | 156.00 | 153.10 |
| 154.80 | -1 | 157.30 | 154.80 |
| 156.20 | -1 | 156.20 | 153.90 |

Interpretasi:
- Baris 1–2: **trend = 1** → harga di atas supertrend (uptrend), supertrend = lower_band
- Baris 3–4: **trend = -1** → harga di bawah supertrend (downtrend), supertrend = upper_band

---

## Strategi Sederhana

| Kondisi | Aksi |
|---------|------|
| Harga *close* > Supertrend (trend berubah dari -1 ke 1) | **Buy** / Long entry |
| Harga *close* < Supertrend (trend berubah dari 1 ke -1) | **Sell** / Short entry |
| Trend = 1 | Hold long position / tidak sell |
| Trend = -1 | Hold short position / tidak buy |

### Tips:
- Gunakan timeframe lebih tinggi (H4/Daily) untuk sinyal yang lebih akurat
- Kombinasikan dengan ADX untuk konfirmasi kekuatan tren
- Hindari sinyal saat ADX < 20 (market sideways)
- Gunakan `atr_multiplier = 2.0` untuk scalping, `3.0` untuk swing trading

---

## Referensi

- Seban, Olivier. *Supertrend Indicator*.
- [Investopedia: Average True Range (ATR)](https://www.investopedia.com/terms/a/atr.asp)
- [TradingView: Supertrend](https://www.tradingview.com/support/solutions/43000590582-supertrend/)
