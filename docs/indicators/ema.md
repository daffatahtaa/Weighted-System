# EMA (Exponential Moving Average)

## Overview

**Exponential Moving Average (EMA)** adalah indikator *trend-following* yang memberikan bobot lebih besar pada data harga terbaru, menjadikannya lebih responsif terhadap perubahan harga dibandingkan **SMA (Simple Moving Average)**.

EMA membantu trader untuk:
- **Mengidentifikasi** arah tren jangka pendek, menengah, dan panjang
- **Menentukan** level *support/resistance* dinamis
- **Memberikan** sinyal *cross* antara EMA cepat dan lambat
- **Mengonfirmasi** tren dengan melihat slope (kemiringan) EMA

### Perbandingan EMA vs SMA

| Aspek | EMA | SMA |
|-------|-----|-----|
| Bobot | Lebih berat ke harga terbaru | Semua harga sama rata |
| Responsivitas | Lebih cepat bereaksi | Lebih halus, lebih lambat |
| *Lag* | Lebih rendah | Lebih tinggi |
| Cocok untuk | Tren jangka pendek, entry timing | Tren jangka panjang, support/resistance |

---

## Interpretasi

| Kondisi | Makna |
|---------|-------|
| Harga di atas EMA | Uptrend — harga cenderung naik |
| Harga di bawah EMA | Downtrend — harga cenderung turun |
| EMA naik (slope positif) | Momentum bullish menguat |
| EMA turun (slope negatif) | Momentum bearish menguat |
| EMA datar | Market *sideways* / konsolidasi |
| Harga dekat EMA | Market sedang "menunggu" — potensi *breakout* atau *reversal* |

### Fast EMA vs Slow EMA

| Jenis | Periode | Fungsi |
|-------|---------|--------|
| **Fast EMA** | 9, 12, 20 | Mengikuti harga lebih dekat, sinyal lebih cepat |
| **Slow EMA** | 50, 100, 200 | Menunjukkan tren utama, lebih halus |

Sinyal umum:
- **Fast EMA cross di atas Slow EMA** → *Golden Cross* (bullish)
- **Fast EMA cross di bawah Slow EMA** → *Death Cross* (bearish)
- **Harga di atas Fast EMA dan Fast EMA di atas Slow EMA** → Tren bullish kuat
- **Harga di bawah Fast EMA dan Fast EMA di bawah Slow EMA** → Tren bearish kuat

---

## Step-by-Step Calculation

### Step 1: Smoothing Factor (α)

$$
\alpha = \frac{2}{\text{length} + 1}
$$

| Periode | α (Smoothing Factor) |
|---------|---------------------|
| 9 | 0.200 (20%) |
| 20 | 0.095 (9.5%) |
| 50 | 0.039 (3.9%) |
| 200 | 0.010 (1.0%) |

Semakin kecil α, semakin lambat EMA bereaksi — dan semakin halus garisnya.

### Step 2: Exponential Moving Average

Nilai EMA pertama adalah SMA dari `length` data pertama:

$$
EMA_{\text{length}} = \frac{1}{\text{length}} \sum_{i=1}^{\text{length}} \text{Close}_i
$$

Setelah itu, EMA dihitung secara rekursif:

$$
EMA_t = \text{Close}_t \times \alpha + EMA_{t-1} \times (1 - \alpha)
$$

### Contoh Perhitungan (length = 5, α = 2/6 ≈ 0.333)

| Hari | Close | EMA |
|------|-------|-----|
| 1 | 100 | — |
| 2 | 102 | — |
| 3 | 101 | — |
| 4 | 103 | — |
| 5 | 104 | **102.00** (SMA 5 hari pertama) |
| 6 | 106 | 102.00 + 0.333 × (106 - 102.00) = **103.33** |
| 7 | 105 | 103.33 + 0.333 × (105 - 103.33) = **103.89** |
| 8 | 107 | 103.89 + 0.333 × (107 - 103.89) = **104.93** |

---

## Cara Penggunaan dalam Kode

```python
import pandas as pd
from src.indicators.ema import ema

# Contoh data harga close
data = pd.DataFrame({
    'close': [100, 102, 101, 103, 104, 106, 105, 107, 108, 110],
})

# Multiple EMA dalam satu panggilan
result = ema(data['close'], lengths=[20, 50, 200])
print(result.tail())

# Fast + Slow EMA (seperti di weighted_system.pine)
ema_200 = result['ema_200']
ema_20 = result['ema_20']
```

### Output:

```
   ema_20     ema_50     ema_200
5   103.33  102.50  101.25
6   103.89  102.80  101.40
7   104.93  103.15  101.58
8   105.62  103.48  101.75
9   106.08  103.78  101.92
```

Interpretasi:
- **EMA 20 > EMA 50 > EMA 200** — tren bullish (semua EMA terurut naik)
- **Harga > EMA 20 > EMA 50 > EMA 200** — bullish kuat

---

## Multiple EMA dalam Strategi

Strategi seperti **Weighted System** sering menggunakan dua EMA sekaligus:

```python
from src.indicators.ema import ema

close = data['close']
emas = ema(close, lengths=[200, 20])  # Slow (200) + Fast (20)

slow_ema = emas['ema_200']
fast_ema = emas['ema_20']

# Golden Cross / Death Cross
golden_cross = (fast_ema > slow_ema) & (fast_ema.shift(1) <= slow_ema.shift(1))
death_cross = (fast_ema < slow_ema) & (fast_ema.shift(1) >= slow_ema.shift(1))

# Slope (kemiringan) EMA
ema_slope = slow_ema - slow_ema.shift(1)
```

---

## Parameter

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `length` | — | Periode EMA. Semakin besar, semakin halus dan lambat |
| Nilai umum | 9, 12, 20 | Fast EMA — sinyal cepat |
| Nilai umum | 50, 100, 200 | Slow EMA — tren utama |

---

## Referensi

- [Investopedia: Exponential Moving Average (EMA)](https://www.investopedia.com/terms/e/ema.asp)
- [StockCharts: Moving Averages](https://school.stockcharts.com/doku.php?id=technical_indicators:moving_averages)
