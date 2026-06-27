# ADX (Average Directional Index)

## Overview

**Average Directional Index (ADX)** adalah indikator teknikal yang digunakan untuk mengukur **kekuatan (strength)** suatu tren, bukan arah tren. Dikembangkan oleh **J. Welles Wilder** pada tahun 1978.

ADX membantu trader untuk:
- **Mengidentifikasi** apakah market sedang *trending* atau *range-bound* (sideways)
- **Menyaring** sinyal trading hanya pada tren terkuat
- **Menghindari** false signal saat market sedang datar

Nilai ADX berkisar dari **0 hingga 100**, di mana:
| Nilai ADX | Interpretasi |
|-----------|-------------|
| 0 – 20 | Tidak ada tren / *range-bound* (sideways) |
| 20 – 25 | Tren lemah mulai terbentuk |
| 25 – 50 | Tren kuat |
| 50 – 75 | Tren sangat kuat |
| 75 – 100 | Tren ekstrem (seringkali reversal sudah dekat) |

> ⚠️ ADX **tidak menunjukkan arah** tren (naik atau turun). Ia hanya mengukur **kekuatan**. Untuk arah tren, lihat posisi +DI vs -DI.

---

## Components (Komponen)

ADX terdiri dari **3 garis**:

| Komponen | Deskripsi |
|----------|-----------|
| **+DI** (Positive Directional Indicator) | Mengukur kekuatan pergerakan *naik* |
| **-DI** (Negative Directional Indicator) | Mengukur kekuatan pergerakan *turun* |
| **ADX** (Average Directional Index) | Rata-rata smoothed dari DX — mengukur kekuatan tren secara keseluruhan |

### Interpretasi +DI dan -DI:
- **+DI > -DI** → Pergerakan naik lebih dominan (bullish)
- **-DI > +DI** → Pergerakan turun lebih dominan (bearish)
- **Cross +DI dan -DI** → Potensi sinyal entry (tapi perlu dikonfirmasi ADX > 25)

---

## Step-by-Step Calculation

### Step 1: True Range (TR)

True Range adalah ukuran volatilitas harian yang memperhitungkan *gap* harga.

$$
\begin{aligned}
TR_t = \max(& \\ 
&\quad \text{High}_t - \text{Low}_t, \\
&\quad |\text{High}_t - \text{Close}_{t-1}|, \\
&\quad |\text{Low}_t - \text{Close}_{t-1}| \\
&)
\end{aligned}
$$

Dalam kode:
```python
tr = pd.concat([
    (high - low).abs(),
    (high - prev_close).abs(),
    (low - prev_close).abs(),
], axis=1).max(axis=1)
```

### Step 2: Directional Movement (+DM dan -DM)

Mengukur pergerakan harga ke atas dan ke bawah.

$$
\begin{aligned}
\text{UpMove} &= \text{High}_t - \text{High}_{t-1} \\
\text{DownMove} &= \text{Low}_{t-1} - \text{Low}_t \\[4pt]
+DM_t &=
\begin{cases}
\text{UpMove}, & \text{if UpMove > DownMove and UpMove > 0} \\
0, & \text{otherwise}
\end{cases} \\[4pt]
-DM_t &=
\begin{cases}
\text{DownMove}, & \text{if DownMove > UpMove and DownMove > 0} \\
0, & \text{otherwise}
\end{cases}
\end{aligned}
$$

> **Catatan:** +DM dan -DM tidak bisa bernilai positif bersamaan. Hanya satu yang dihitung, atau keduanya 0.

Dalam kode:
```python
plus_dm = pd.Series(np.where(
    (up_move > down_move) & (up_move > 0), up_move, 0.0
), index=df.index)

minus_dm = pd.Series(np.where(
    (down_move > up_move) & (down_move > 0), down_move, 0.0
), index=df.index)
```

### Step 3: Wilder's Smoothing

Wilder menggunakan metode smoothing khusus (bukan EMA biasa):

$$
\text{Smoothed}_t = \text{Smoothed}_{t-1} - \frac{\text{Smoothed}_{t-1}}{\text{period}} + \text{Value}_t
$$

Nilai pertama adalah **simple average** dari `period` data pertama:

$$
\text{Smoothed}_{\text{period}} = \frac{1}{\text{period}} \sum_{i=1}^{\text{period}} \text{Value}_i
$$

Proses ini diterapkan pada **TR**, **+DM**, dan **-DM** secara terpisah.

### Step 4: Hitung +DI dan -DI

$$
\begin{aligned}
+DI_t &= 100 \times \frac{\text{Smoothed } +DM_t}{\text{Smoothed } TR_t} \\[4pt]
-DI_t &= 100 \times \frac{\text{Smoothed } -DM_t}{\text{Smoothed } TR_t}
\end{aligned}
$$

+DI dan -DI dinyatakan dalam persentase (0–100).

### Step 5: Hitung Directional Index (DX)

DX mengukur selisih relatif antara +DI dan -DI:

$$
DX_t = 100 \times \frac{|+DI_t - -DI_t|}{+DI_t + -DI_t}
$$

- Jika +DI = -DI → DX = 0 (tidak ada directional movement)
- Jika salah satu dominan → DX mendekati 100

### Step 6: Hitung ADX

ADX adalah **Wilder's smoothed average dari DX** selama `period` hari:

$$
ADX_t = \text{WilderSmooth}(DX_t, \text{period})
$$

Inilah garis utama yang menunjukkan kekuatan tren.

---

## Cara Penggunaan dalam Kode

```python
import pandas as pd
from src.indicators.adx import adx

# Contoh data OHLC
data = pd.DataFrame({
    'high':  [...],
    'low':   [...],
    'close': [...],
})

result = adx(data, period=14)
print(result[['adx', 'plus_di', 'minus_di']].tail())
```

### Output:
| adx | plus_di | minus_di |
|-----|---------|----------|
| 22.5 | 28.3 | 18.7 |
| 24.1 | 30.2 | 17.5 |
| 26.8 | 32.1 | 16.2 |

Interpretasi pada baris terakhir:
- **ADX = 26.8** → Tren kuat terbentuk (>25)
- **+DI > -DI** → Tren naik (bullish)

---

## Strategi Sederhana

| Kondisi | Sinyal |
|---------|--------|
| ADX > 25 **dan** +DI > -DI | Long / Buy |
| ADX > 25 **dan** -DI > +DI | Short / Sell |
| ADX < 20 | Hindari entry — market sideways |
| +DI cross ke atas -DI + ADX > 25 | Bullish cross (buy signal) |
| -DI cross ke atas +DI + ADX > 25 | Bearish cross (sell signal) |

---

## Referensi

- Wilder, J. Welles. *New Concepts in Technical Trading Systems*. Trend Research, 1978.
- [Investopedia: Average Directional Index (ADX)](https://www.investopedia.com/terms/a/adx.asp)
- [StockCharts: ADX and DMI](https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx)