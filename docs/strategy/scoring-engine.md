# Scoring Engine

## Konsep Dasar

**Scoring Engine** adalah jantung dari Weighted System. Alih-alih menggunakan satu indikator untuk entry, sistem mengumpulkan bukti dari berbagai indikator dan menjumlahkannya menjadi satu nilai kepercayaan (*confidence score*).

```
Setiap kondisi terpenuhi → +poin
Setiap kondisi tidak terpenuhi → +0 (bukan -poin)
Total skor = jumlah semua poin
Entry jika total skor ≥ weightedEntryValue (default: 100)
```

> **Catatan:** Sistem hanya memberikan poin positif. Tidak ada pengurangan skor. Jika skor tidak mencapai threshold, berarti bukti belum cukup kuat — dan posisi tidak dibuka.

---

## Long Score — Ringkasan

| Kategori | Sub-Komponen | Poin | Maks per Kategori |
|----------|-------------|------|-------------------|
| **Supertrend** | ST1 flip | 10 | |
| | ST2 flip | 5 | |
| | ST3 flip | 5 | |
| | 2 ST hijau | 10 | |
| | 3 ST hijau | 15 | |
| | ST1 hijau | 5 | |
| | ST2 hijau | 10 | |
| | ST3 hijau | 10 | |
| | | | **55** |
| **Stochastic** | K cross D | 10 | |
| | K > oversold (20) | 10 | |
| | K > D | 10 | |
| | K > K[1] | 5 | |
| | D > D[1] | 5 | |
| | K cross oversold | 10 | |
| | K > 50 | 10 | |
| | K cross D di oversold | 30 | |
| | | | **90** |
| **EMA** | Close cross fastEMA | 5 | |
| | fastEMA cross slowEMA | 5 | |
| | Close > fastEMA | 5 | |
| | fastEMA > fastEMA[1] | 10 | |
| | Distance < 1% | 15 | |
| | Distance < 2% | 10 | |
| | Distance < 3% | 5 | |
| | slowEMA > slowEMA[1] | 5 | |
| | slowEMA > slowEMA[5] | 5 | |
| | slowEMA > slowEMA[10] | 5 | |
| | Close > slowEMA | 5 | |
| | | | **80** |
| **ADX/DMI** | ADX > threshold | 10 | |
| | ADX > ADX[1] | 10 | |
| | +DI > -DI | 15 | |
| | +DI cross -DI | 20 | |
| | +DI > -DI & ADX > threshold | 20 | |
| | ADX > 30 | 10 | |
| | ADX acceleration | 10 | |
| | | | **105** |
| **Choppiness Index** | CI < 30 | 10 | |
| | CI < CI[1] | 5 | |
| | | | **15** |
| **Persistence** | ST1 hijau > 1 bar | 5 | |
| | ST2 hijau > 1 bar | 5 | |
| | ST3 hijau > 1 bar | 5 | |
| | Stoch K naik 3 bar | 5 | |
| | ADX naik 3 bar | 5 | |
| | slowEMA & fastEMA naik | 5 | |
| | | | **30** |
| **Total Maksimum** | | | **~375** |

---

## 1. Supertrend Scoring

### Logika Dasar

Tiga Supertrend dengan parameter berbeda memberikan pandangan multi-level tentang arah tren:

| ST | Period | Multiplier | Karakter |
|----|--------|------------|----------|
| ST1 | 10 | 1 | Paling sensitif, sering flip |
| ST2 | 11 | 2 | Sedang |
| ST3 | 12 | 3 | Paling selektif, jarang flip |

### Kode (Pine Script)

```python
# Flip detection — ST baru berubah jadi hijau
stFlip   = direction[1] > 0 and direction < 0    # ST1 flipped to green
stFlip2  = direction2[1] > 0 and direction2 < 0  # ST2 flipped to green
stFlip3  = direction3[1] > 0 and direction3 < 0  # ST3 flipped to green

longScore += stFlip  ? 10 : 0   # ST1 flip = sinyal kuat
longScore += stFlip2 ?  5 : 0   # ST2 flip = konfirmasi
longScore += stFlip3 ?  5 : 0   # ST3 flip = konfirmasi

# Green count — berapa ST yang sedang hijau
greenCount = (ST1 green?1:0) + (ST2 green?1:0) + (ST3 green?1:0)

if greenCount == 2: longScore += 10   # Mayoritas hijau
if greenCount == 3: longScore += 15   # Semua hijau — sinyal terkuat

# Direction bias — ST yang sedang hijau
longScore += direction  < 0 ? 5  : 0   # ST1 hijau
longScore += direction2 < 0 ? 10 : 0   # ST2 hijau (bobot lebih)
longScore += direction3 < 0 ? 10 : 0   # ST3 hijau (bobot lebih)
```

### Tabel Poin ST

| Kondisi | Poin | Catatan |
|---------|------|---------|
| ST1 flip (baru hijau) | 10 | Sinyal reversal terkuat dari ST1 |
| ST2 flip (baru hijau) | 5 | Konfirmasi dari ST yang lebih lambat |
| ST3 flip (baru hijau) | 5 | Konfirmasi dari ST paling lambat |
| 2 ST hijau | 10 | Mayoritas setuju uptrend |
| 3 ST hijau | 15 | Konsensus penuh — semua uptrend |
| ST1 hijau | 5 | ST1 sedang di uptrend |
| ST2 hijau | 10 | ST2 sedang di uptrend |
| ST3 hijau | 10 | ST3 sedang di uptrend |

---

## 2. Stochastic RSI Scoring

### Logika Dasar

Stochastic RSI mengukur momentum menggunakan posisi RSI dalam *range*-nya.

### Kode (Pine Script)

```python
# K cross D — moment changes
longScore += ta.crossover(stochK, stochD) ? 10 : 0

# K above oversold — momentum pulih dari jenuh jual
longScore += stochK > oversoldStoch ? 10 : 0

# K above D — momentum bullish
longScore += stochK > stochD ? 10 : 0

# K and D rising — momentum menguat
longScore += stochK > stochK[1] ? 5 : 0
longScore += stochD > stochD[1] ? 5 : 0

# K crossover oversold threshold (20) — breakout dari oversold
longScore += ta.crossover(stochK, oversoldStoch) ? 10 : 0

# K above 50 — momentum bullish dominan
longScore += stochK > 50 ? 10 : 0

# SPECIAL: K cross D while still in oversold — strong bullish signal
if (ta.crossover(stochK, stochD) and stochK < oversoldStoch):
    longScore += 30
```

### Tabel Poin Stochastic

| Kondisi | Poin | Catatan |
|---------|------|---------|
| K cross D (naik) | 10 | Perubahan momentum dari bearish ke bullish |
| K > 20 (oversold) | 10 | Momentum sudah pulih dari level ekstrem |
| K > D | 10 | Momentum bullish berkelanjutan |
| K > K[1] | 5 | K naik — momentum menguat |
| D > D[1] | 5 | D naik — konfirmasi |
| K cross 20 | 10 | *Breakout* dari zona oversold |
| K > 50 | 10 | Momentum bullish dominan |
| K cross D (saat < 20) | 30 | **Sinyal terkuat** — *oversold recovery* dengan konfirmasi |

---

## 3. EMA Scoring

### Logika Dasar

Dua EMA digunakan: **Fast EMA (20)** dan **Slow EMA (200)**. Semakin dekat harga ke slow EMA, semakin besar potensi *breakout*.

### Kode (Pine Script)

```python
if (useFastEma):
    # Harga menembus fast EMA
    longScore += ta.crossover(close, fastEmaValue) ? 5 : 0
    # Fast EMA menembus slow EMA (golden cross)
    longScore += ta.crossover(fastEmaValue, emaValue) ? 5 : 0
    # Harga di atas fast EMA
    longScore += close > fastEmaValue ? 5 : 0
    # Fast EMA naik (slope positif)
    longScore += fastEmaValue > fastEmaValue[1] ? 10 : 0

# Distance harga dari slow EMA (200)
emaDistance = abs(close - emaValue) / emaValue * 100

if emaDistance < 1: longScore += 15   # Sangat dekat — potensi breakout
if emaDistance < 2: longScore += 10   # Cukup dekat
if emaDistance < 3: longScore += 5    # Masih dalam range

# Slow EMA rising (multi-timeframe)
longScore += emaValue > emaValue[1]  ? 5 : 0   # 1 bar
longScore += emaValue > emaValue[5]  ? 5 : 0   # 5 bar
longScore += emaValue > emaValue[10] ? 5 : 0   # 10 bar

# Harga di atas slow EMA — tren utama bullish
longScore += close > emaValue ? 5 : 0
```

### Tabel Poin EMA

| Kondisi | Poin | Catatan |
|---------|------|---------|
| Close cross fastEMA | 5 | Entry timing — harga menembus EMA 20 |
| fastEMA cross slowEMA | 5 | Golden cross — EMA 20 naik di atas EMA 200 |
| Close > fastEMA | 5 | Harga di atas EMA 20 |
| fastEMA > fastEMA[1] | 10 | EMA 20 naik — slope positif |
| Distance < 1% | 15 | Harga sangat dekat ke EMA 200 |
| Distance < 2% | 10 | Harga cukup dekat ke EMA 200 |
| Distance < 3% | 5 | Harga dalam radius 3% dari EMA 200 |
| slowEMA > slowEMA[1] | 5 | EMA 200 naik 1 bar |
| slowEMA > slowEMA[5] | 5 | EMA 200 naik 5 bar |
| slowEMA > slowEMA[10] | 5 | EMA 200 naik 10 bar |
| Close > slowEMA | 5 | Harga di atas EMA 200 |

---

## 4. ADX / DMI Scoring

### Logika Dasar

ADX mengukur kekuatan tren. +DI dan -DI menunjukkan arah dominan. Kombinasi keduanya memberikan sinyal kuat.

### Kode (Pine Script)

```python
# Kekuatan tren
longScore += adx > adxTreshold ? 10 : 0   # ADX > 25
longScore += adx > adx[1] ? 10 : 0         # ADX menguat

# Arah dominan
longScore += diplus > diminus ? 15 : 0      # +DI > -DI (bullish)

# Perubahan arah
longScore += ta.crossover(diplus, diminus) ? 20 : 0   # +DI cross -DI

# Kombinasi: arah + kekuatan
longScore += diplus > diminus and adx > adxTreshold ? 20 : 0

# ADX ekstrem
longScore += adx > 30 ? 10 : 0

# ADX acceleration — percepatan tren
longScore += (adx - adx[1]) > (adx[1] - adx[2]) ? 10 : 0
```

### Tabel Poin ADX

| Kondisi | Poin | Catatan |
|---------|------|---------|
| ADX > 25 | 10 | Tren cukup kuat untuk entry |
| ADX > ADX[1] | 10 | Tren semakin kuat |
| +DI > -DI | 15 | Arah bullish dominan |
| +DI cross -DI | 20 | Perubahan arah ke bullish |
| +DI > -DI & ADX > 25 | 20 | Kombinasi — arah + kekuatan |
| ADX > 30 | 10 | Tren sangat kuat |
| ADX acceleration | 10 | Percepatan tren meningkat |

---

## 5. Choppiness Index Scoring

### Logika Dasar

Choppiness Index (CI) mengukur apakah market *trending* atau *choppy*. Selain sebagai filter, CI juga berkontribusi ke skor.

### Kode (Pine Script)

```python
# CI rendah = trending
longScore += ci < 30 ? 10 : 0    # Tren kuat
longScore += ci < ci[1] ? 5 : 0  # CI turun — tren mulai terbentuk
```

### Tabel Poin CI

| Kondisi | Poin | Catatan |
|---------|------|---------|
| CI < 30 | 10 | Market sedang *trending* kuat |
| CI < CI[1] | 5 | CI turun — transisi dari *choppy* ke *trending* |

---

## 6. Persistence Scoring

### Logika Dasar

Persistence (keberlanjutan) memberi poin tambahan jika kondisi indikator bertahan selama beberapa bar — menandakan tren yang stabil, bukan *false breakout*.

### Kode (Pine Script)

```python
# ST hijau bertahan
longScore += direction  < 0 and direction[1]  < 0 ? 5 : 0   # ST1 hijau 2+ bar
longScore += direction2 < 0 and direction2[1] < 0 ? 5 : 0   # ST2 hijau 2+ bar
longScore += direction3 < 0 and direction3[1] < 0 ? 5 : 0   # ST3 hijau 2+ bar

# Stoch K naik 3 bar berturut-turut
longScore += stochK > stochK[1] and stochK[1] > stochK[2] and stochK[2] > stochK[3] ? 5 : 0

# ADX menguat 3 bar berturut-turut
longScore += adx > adx[1] and adx[1] > adx[2] ? 5 : 0

# Slow & fast EMA naik bersamaan
longScore += emaValue > emaValue[1] and fastEmaValue > fastEmaValue[1] ? 5 : 0
```

### Tabel Poin Persistence

| Kondisi | Poin | Catatan |
|---------|------|---------|
| ST1 hijau 2+ bar | 5 | ST1 sudah hijau sejak bar lalu |
| ST2 hijau 2+ bar | 5 | ST2 sudah hijau sejak bar lalu |
| ST3 hijau 2+ bar | 5 | ST3 sudah hijau sejak bar lalu |
| Stoch K naik 3 bar | 5 | Momentum bullish berkelanjutan |
| ADX naik 3 bar | 5 | Kekuatan tren meningkat terus |
| slowEMA & fastEMA naik | 5 | Konfirmasi tren dari kedua EMA |

---

## Short Score — Mirror dari Long Score

Short Score menggunakan logika yang sama persis tetapi terbalik (mirror):

| Kategori | Long Condition | Short Condition |
|----------|---------------|-----------------|
| **ST Flip** | ST[1] merah → ST hijau | ST[1] hijau → ST merah |
| **ST Alignment** | greenCount | redCount |
| **ST Direction** | ST hijau | ST merah |
| **Stochastic** | K cross D (naik) | K cross D (turun) |
| | K > oversold (20) | K < overbought (80) |
| | K > D | K < D |
| | K > 50 | K < 50 |
| | Cross K > 20 | Cross K < 80 |
| **EMA** | close cross di atas fastEMA | close cross di bawah fastEMA |
| | close > fastEMA | close < fastEMA |
| | fastEMA > fastEMA[1] | fastEMA < fastEMA[1] |
| | close > slowEMA | close < slowEMA |
| **ADX** | +DI > -DI | -DI > +DI |
| | +DI cross -DI | -DI cross +DI |
| **Persistence** | ST hijau bertahan | ST merah bertahan |
| | K naik 3 bar | K turun 3 bar |
| | EMA naik semua | EMA turun semua |

---

## Trend Filters (Pre-Entry)

Sebelum entry, dua filter tambahan memeriksa apakah market benar-benar *trending*:

### Choppiness Index Filter

```
isTrendingCI = CI < chopTreshold    # chopTreshold = 38.2
chopFilter   = useChoppinessIndex ? isTrendingCI : true
```

### ADX Filter

```
isTrendingADX = ADX > adxTreshold    # adxTreshold = 25
adxFilter     = useAdxFilter ? isTrendingADX : true
```

### Final Entry Condition

```
longCondition = close > ema200 AND chopFilter AND adxFilter AND longScore ≥ weightedEntryValue
```

---

## Visualisasi Bobot Scoring

```
Kategori           Poin Max      Batang
──────────────────────────────────────────
Supertrend           55         ████████████▌
Stochastic RSI       90         █████████████████████▍
EMA                  80         ████████████████████
ADX/DMI             105         ██████████████████████████▏
Choppiness Index     15         ███▊
Persistence          30         ███████▌
──────────────────────────────────────────
Total              ~375
Threshold         ≥ 100  (≈ 27% dari max)
```

---

## Referensi

- Kode sumber: `src/pinescript/weighted_system.pine` — bagian SCORING LONG & SCORING SHORT
- [Overview Strategi](overview.md)
- [Entry Methods](entry-methods.md)
- [Exit Methods](exit-methods.md)
- [Dokumentasi Indikator](../indicators/)
