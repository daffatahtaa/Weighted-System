# Exit Methods

## Gambaran Umum

Weighted System menyediakan **7 metode exit** yang dapat dipilih melalui parameter `exitPositionMethod`. Tidak seperti entry yang menggunakan scoring, exit bisa menggunakan pendekatan berbeda — tergantung metode yang dipilih.

```
exitLong = switch exitPositionMethod:
    EXT_1  → ta.crossunder(close, st)          # Supertrend 1
    EXT_2  → ta.crossunder(close, st2)         # Supertrend 2
    EXT_3  → ta.crossunder(close, st3)         # Supertrend 3
    EXT_4  → longScore < exitScoring           # Scoring
    EXT_5  → longScore < exitScoring OR close < emaValue   # Scoring + EMA
    EXT_6  → barssince(longScore > exitScoring) > 2        # Bars Since
    EXT_7  → barssince(longScore > exitScoring) > 2 AND close < emaValue  # Bars Since + EMA
```

---

## Metode 1: Supertrend 1

### Logika

Exit saat harga **close** menembus ke bawah garis Supertrend 1 (untuk long).

```python
# LONG exit
exitLong = ta.crossunder(close, st)

# SHORT exit
exitShort = ta.crossover(close, st)
```

| Karakter | Nilai |
|----------|-------|
| ST Period | 10 |
| ST Multiplier | 1 |
| Sensitivitas | **Tertinggi** — exit paling cepat |
| Risiko | Sering exit premature |
| Cocok untuk | Scalping, tren jangka pendek |

### Visual

```
Harga
  │
  ├─── Long Entry
  │
  │    ┌───── Harga
  │    │      ══════ ST1 (paling dekat ke harga)
  │    │      │
  │    ▼      ▼ Crossunder → EXIT LONG
  │
  └──────────────────────────
```

---

## Metode 2: Supertrend 2

### Logika

Exit saat harga **close** menembus ke bawah garis Supertrend 2.

```python
exitLong = ta.crossunder(close, st2)
exitShort = ta.crossover(close, st2)
```

| Karakter | Nilai |
|----------|-------|
| ST Period | 11 |
| ST Multiplier | 2 |
| Sensitivitas | Sedang |
| Risiko | Seimbang |

---

## Metode 3: Supertrend 3

### Logika

Exit saat harga **close** menembus ke bawah garis Supertrend 3.

```python
exitLong = ta.crossunder(close, st3)
exitShort = ta.crossover(close, st3)
```

| Karakter | Nilai |
|----------|-------|
| ST Period | 12 |
| ST Multiplier | 3 |
| Sensitivitas | **Terendah** — exit paling lambat |
| Risiko | Lebih banyak drawdown sebelum exit |
| Cocok untuk | Tren kuat, swing trading |

> **Default:** Metode exit default di Weighted System adalah **Supertrend 3**.

---

## Metode 4: Scoring

### Logika

Exit saat **longScore** turun di bawah `exitScoring` (default: 50).

```python
exitLong = longScore < exitScoring
exitShort = shortScore < exitScoring
```

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `exitScoring` | 50 | Ambang batas skor untuk exit |

### Kelemahan

Scoring bisa fluktuatif dari bar ke bar. Skor 55 di bar ini bisa turun ke 45 di bar berikutnya, lalu naik lagi ke 60 — menyebabkan whipsaw.

Untuk mengurangi whipsaw, sistem menyediakan deteksi **persistensi skor lemah**:

```python
scoreWeakLong = longScore < exitScoring
scoreWeakLongPersist = scoreWeakLong and scoreWeakLong[1] and scoreWeakLong[2]
```

Variabel `scoreWeakLongPersist` ini saat ini tidak digunakan di kode entry/exit, tetapi tersedia untuk eksperimen.

---

## Metode 5: Scoring & Long EMA

### Logika

Exit saat **scoring lemah ATAU** harga **close** sudah melewati EMA 200 (slow EMA).

```python
exitLong = longScore < exitScoring or close < emaValue
exitShort = shortScore < exitScoring or close > emaValue
```

Metode ini menggabungkan dua kondisi:
1. **Scoring**: Skor kepercayaan sudah turun
2. **EMA 200**: Harga sudah menembus tren utama

Dengan logika OR, exit akan terjadi jika **salah satu** kondisi terpenuhi.

### Kapan Exit Terjadi

| Scoring | Harga vs EMA 200 | Hasil |
|---------|------------------|-------|
| Kuat (≥ 50) | Di atas EMA | ✅ Tahan |
| Kuat (≥ 50) | Di bawah EMA | ❌ Exit |
| Lemah (< 50) | Di atas EMA | ❌ Exit |
| Lemah (< 50) | Di bawah EMA | ❌ Exit |

---

## Metode 6: Scoring Bars Since Threshold

### Logika

Exit saat skor sudah berada di bawah threshold selama **lebih dari 2 bar**.

```python
exitLong = ta.barssince(longScore > exitScoring) > 2
exitShort = ta.barssince(shortScore > exitScoring) > 2
```

### Cara Kerja

`ta.barssince()` menghitung jumlah bar sejak kondisi `longScore > exitScoring` terakhir kali bernilai true.

| Bar | Skor | Skor > 50? | Barssince | Exit? |
|-----|------|------------|-----------|-------|
| 1 | 120 | ✅ True | 0 | ❌ |
| 2 | 60 | ✅ True | 0 | ❌ |
| 3 | 45 | ❌ False | 1 | ❌ |
| 4 | 40 | ❌ False | 2 | ❌ |
| 5 | 35 | ❌ False | 3 | ✅ **Exit** |

### Keuntungan

- **Mengurangi whipsaw** — tidak exit saat skor turun sebentar lalu naik lagi
- Memberi toleransi 2 bar sebelum menutup posisi

---

## Metode 7: Scoring Bars Since + Slow EMA

### Logika

Kombinasi Metode 6 ditambah konfirmasi dari EMA 200.

```python
exitLong = ta.barssince(longScore > exitScoring) > 2 and close < emaValue
exitShort = ta.barssince(shortScore > exitScoring) > 2 and close > emaValue
```

### Cara Kerja

Exit hanya terjadi jika **kedua kondisi** terpenuhi:
1. Skor sudah lemah > 2 bar
2. Harga sudah melewati EMA 200 (konfirmasi tren utama berubah)

| Bar | Skor | Skor > 50? | Barssince | Close > EMA? | Exit? |
|-----|------|------------|-----------|--------------|-------|
| 1 | 120 | ✅ | 0 | ✅ | ❌ |
| 2 | 60 | ✅ | 0 | ✅ | ❌ |
| 3 | 45 | ❌ | 1 | ✅ | ❌ |
| 4 | 40 | ❌ | 2 | ✅ | ❌ |
| 5 | 35 | ❌ | 3 | ✅ | ❌ (**masih di atas EMA**) |
| 6 | 30 | ❌ | 4 | ❌ | ✅ **Exit** |

### Keuntungan

- Paling selektif — membutuhkan konfirmasi tren utama
- Menghindari exit saat harga hanya terkoreksi tapi tren masih utuh

---

## Tabel Perbandingan Exit Methods

| Metode | Nama | Logika | Sensitivitas | Whipsaw | Drawdown | Cocok Untuk |
|--------|------|--------|-------------|---------|----------|-------------|
| 1 | **Supertrend 1** | Close crossunder ST1 | 🔴 Tinggi | Tinggi | Rendah | Scalping |
| 2 | **Supertrend 2** | Close crossunder ST2 | 🟡 Sedang | Sedang | Sedang | Day trading |
| 3 | **Supertrend 3** | Close crossunder ST3 | 🟢 Rendah | Rendah | Tinggi | Swing, tren kuat |
| 4 | **Scoring** | Skor < exitScoring | 🔴 Tinggi | Tinggi | Rendah | Konservatif |
| 5 | **Scoring + EMA** | Skor lemah ATAU close < EMA | 🔴 Tinggi | Sedang | Rendah | Konservatif |
| 6 | **Bars Since** | Skor lemah > 2 bar | 🟡 Sedang | Rendah | Sedang | Seimbang |
| 7 | **Bars Since + EMA** | Skor lemah > 2 bar DAN close < EMA | 🟢 Rendah | Sangat Rendah | Tinggi | Tren kuat |

### Visual Perbandingan Timeline Exit

```
Entry ────────────────────────────────────────────────────────►
                                                            │
Metode 1 (ST1)    ──── Exit (paling cepat)                  │
Metode 2 (ST2)    ────────── Exit                            │
Metode 3 (ST3)    ──────────────────── Exit (paling lambat)  │
Metode 4 (Score)  ──── Exit (fluktuatif)                     │
Metode 5 (S+EMA)  ──── Exit                                  │
Metode 6 (Bars)   ────────── Exit (toleransi 2 bar)         │
Metode 7 (B+EMA)  ──────────────────── Exit (paling selektif)│
                                                            ▼
                                                        Waktu
```

---

## Exit untuk Pyramid Entry

Saat menggunakan **Pyramid Entry**, exit menutup semua posisi satu per satu:

```python
# LONG EXIT — Pyramid
if entryMethod == EXT_ENTRY2 and strategy.position_size > 0 and exitLong:
    for i = 0 to maxPyramid by +1:
        strategy.close("Long_" + str.tostring(i + 1))

# SHORT EXIT — Pyramid
if entryMethod == EXT_ENTRY2 and strategy.position_size < 0 and exitShort:
    for i = 0 to maxPyramid by +1:
        strategy.close("Short_" + str.tostring(i + 1))
```

Untuk **Single Entry**, exit langsung menutup satu posisi:

```python
# LONG EXIT — Single
if entryMethod == EXT_ENTRY1 and strategy.position_size > 0 and exitLong:
    strategy.close("Long", str.tostring(longScore))
```

---

## Referensi

- Kode sumber: `src/pinescript/weighted_system.pine` — bagian EXIT LONG & EXIT SHORT
- [Overview Strategi](overview.md)
- [Scoring Engine](scoring-engine.md)
- [Entry Methods](entry-methods.md)
