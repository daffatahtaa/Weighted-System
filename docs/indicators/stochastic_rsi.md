# Stochastic RSI (StochRSI)

## Overview

**Stochastic RSI (StochRSI)** adalah indikator momentum yang dikembangkan oleh **Tushar S. Chande** dan **Stanley Kroll** pada tahun 1994. StochRSI menerapkan formula *stochastic oscillator* pada nilai **RSI**, bukan pada harga — menjadikannya indikator dari indikator (*indicator of an indicator*).

Tujuan utama StochRSI adalah untuk meningkatkan sensitivitas RSI dengan mengukur posisi RSI saat ini relatif terhadap *range* RSI selama periode tertentu.

StochRSI membantu trader untuk:
- **Mengidentifikasi** kondisi *overbought* dan *oversold* dengan lebih sensitif
- **Menangkap** momentum lebih awal dibandingkan RSI biasa
- **Memberikan** sinyal *cross* antara garis %K dan %D
- **Mendeteksi** *divergence* antara StochRSI dan harga

### Perbandingan RSI vs Stochastic RSI

| Aspek | RSI | StochRSI |
|-------|-----|----------|
| Input | Harga | Nilai RSI |
| Range nilai | 0 – 100 | 0 – 100 |
| Sensitivitas | Standar | Lebih sensitif — lebih sering menyentuh 0 dan 100 |
| Osilasi | Lebih halus | Lebih ekstrem |

---

## Components (Komponen)

| Komponen | Deskripsi |
|----------|-----------|
| **RSI** | Relative Strength Index — mengukur kecepatan dan besaran perubahan harga |
| **Stochastic** | Posisi RSI saat ini dalam rentang RSI N periode terakhir |
| **%K** | Smoothed Stochastic (rata-rata bergerak dari Stochastic) |
| **%D** | Signal line — rata-rata bergerak dari %K (lebih halus) |

### Interpretasi Dasar

| Kondisi | Makna |
|---------|-------|
| %K > %D | Momentum bullish — %K naik di atas %D |
| %K < %D | Momentum bearish — %K turun di bawah %D |
| %K < 20 | Oversold — potensi *bounce* (kombinasikan dengan %K > %D) |
| %K > 80 | Overbought — potensi *reversal* (kombinasikan dengan %K < %D) |
| %K > 50 | Momentum bullish sedang |
| %K < 50 | Momentum bearish sedang |
| %K cross di atas %D (di bawah 20) | Sinyal bullish kuat — *oversold recovery* |
| %K cross di bawah %D (di atas 80) | Sinyal bearish kuat — *overbought rejection* |

---

## Step-by-Step Calculation

### Step 1: RSI (Relative Strength Index)

RSI dihitung menggunakan Wilder's smoothing EMA:

**Perubahan harga:**

$$
\Delta_t = \text{Close}_t - \text{Close}_{t-1}
$$

**Gain dan Loss:**

$$
\text{Gain}_t =
\begin{cases}
\Delta_t, & \text{if } \Delta_t > 0 \\
0, & \text{otherwise}
\end{cases}
\quad
\text{Loss}_t =
\begin{cases}
-\Delta_t, & \text{if } \Delta_t < 0 \\
0, & \text{otherwise}
\end{cases}
$$

**Rata-rata Gain/Loss (Wilder's smoothing):**

$$
\begin{aligned}
\text{AvgGain}_t &= \text{AvgGain}_{t-1} + \frac{\text{Gain}_t - \text{AvgGain}_{t-1}}{\text{rsi\_length}} \\
\text{AvgLoss}_t &= \text{AvgLoss}_{t-1} + \frac{\text{Loss}_t - \text{AvgLoss}_{t-1}}{\text{rsi\_length}}
\end{aligned}
$$

**RSI:**

$$
RS_t = \frac{\text{AvgGain}_t}{\text{AvgLoss}_t}
\qquad
RSI_t = 100 - \frac{100}{1 + RS_t}
$$

### Step 2: Stochastic dari RSI

Menerapkan formula stochastic pada nilai RSI yang sudah dihitung:

$$
\text{Stochastic}_t = \frac{RSI_t - \text{Lowest}_{RSI}(n)}{\text{Highest}_{RSI}(n) - \text{Lowest}_{RSI}(n)} \times 100
$$

di mana $n =$ `stochastic_length`.

### Step 3: Smoothing %K dan %D

$$
\begin{aligned}
\%K_t &= \text{SMA}(\text{Stochastic}, \text{smooth\_k}) \\[4pt]
\%D_t &= \text{SMA}(\%K, \text{smooth\_d})
\end{aligned}
$$

---

## Cara Penggunaan dalam Kode

```python
import pandas as pd
from src.indicators.stochastic_rsi import calculate_stochastic_rsi

# Contoh data harga close
data = pd.DataFrame({
    'close': [100, 102, 101, 103, 104, 106, 105, 107, 108, 110],
})

result = calculate_stochastic_rsi(
    close=data['close'],
    rsi_length=14,
    stochastic_length=14,
    smooth_k=3,
    smooth_d=3
)

print(result.tail())
```

### Output:

```
   rsi  stochastic    stoch_k    stoch_d
5  62.5      45.83      42.15     40.50
6  58.3      38.20      40.88     40.63
7  65.0      55.00      46.08     42.45
8  67.5      60.00      51.03     46.51
9  71.4      68.75      57.92     50.29
```

Interpretasi:
- **%K > %D** (stoch_k > stoch_d) → momentum bullish
- **%K naik** → tekanan beli meningkat
- **%K > 50** → momentum bullish dominan

### Deteksi Sinyal

```python
# K cross above D (bullish)
cross_up = (result['stoch_k'] > result['stoch_d']) & (result['stoch_k'].shift(1) <= result['stoch_d'].shift(1))

# K cross below D (bearish)
cross_down = (result['stoch_k'] < result['stoch_d']) & (result['stoch_k'].shift(1) >= result['stoch_d'].shift(1))

# Oversold bounce (K cross D below 20)
oversold_bounce = cross_up & (result['stoch_k'] < 20)
```

---

## Parameter

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `rsi_length` | 14 | Periode untuk kalkulasi RSI |
| `stochastic_length` | 14 | Periode *lookback* untuk nilai tertinggi/terendah RSI |
| `smooth_k` | 3 | Smoothing untuk garis %K |
| `smooth_d` | 3 | Smoothing untuk garis %D (signal line) |

---

## Referensi

- Chande, Tushar S. dan Kroll, Stanley. *The New Technical Trader*. Wiley, 1994.
- [Investopedia: Stochastic RSI (StochRSI)](https://www.investopedia.com/terms/s/stochrsi.asp)
- [StockCharts: StochRSI](https://school.stockcharts.com/doku.php?id=technical_indicators:stochrsi)
