# Weighted System — Overview

## Philosophy

> No single indicator is perfect.
> Indicators should contribute weighted evidence toward a trading decision.

**Weighted System** adalah strategi trading berbasis *scoring* yang menggabungkan kontribusi dari berbagai indikator teknikal menjadi satu nilai kepercayaan (*confidence score*). Setiap indikator tidak langsung membuka posisi — ia hanya menyumbangkan poin (positif atau negatif) ke dalam sistem *scoring*.

Keputusan trading diambil ketika skor total mencapai ambang batas (*threshold*) yang telah ditentukan.

---

## Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WEIGHTED SYSTEM                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌────────────┐    ┌──────────┐    ┌─────────────┐  │
│  │   DATA   │ ──▶│ INDICATORS │ ──▶│ SCORING  │ ──▶│   FILTERS   │  │
│  │  OHLCV   │    │            │    │  ENGINE  │    │             │  │
│  └──────────┘    └────────────┘    └──────────┘    └─────────────┘  │
│       │                │                │                │          │
│       ▼                ▼                ▼                ▼          │
│  ┌────────┐    ┌────────────┐    ┌──────────┐    ┌─────────────┐  │
│  │ Close  │    │ • 3 ST     │    │ Long     │    │ • Chop      │  │
│  │ High   │    │ • 2 EMA    │    │ Score    │    │   Index     │  │
│  │ Low    │    │ • StochRSI │    │ • 6 cat  │    │ • ADX       │  │
│  └────────┘    │ • ADX/DMI  │    │ Short    │    │             │  │
│                │ • Chop Idx │    │ Score    │    └─────────────┘  │
│                └────────────┘    └──────────┘           │          │
│                                                         ▼          │
│                                          ┌──────────────────────┐  │
│                                   ┌─────│      ENTRY ENGINE    │  │
│                                   │     │ • Single / Pyramid   │  │
│                                   │     │ • Threshold: Score ≥ │  │
│                                   │     │   weightedEntryValue │  │
│                                   │     └──────────────────────┘  │
│                                   │              │                │
│                                   │              ▼                │
│                                   │     ┌──────────────────────┐  │
│                                   └─────│      EXIT ENGINE     │  │
│                                         │ • 7 methods          │  │
│                                         │ • ST, Score, EMA     │  │
│                                         └──────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Alur Eksekusi

1. **Data** → OHLCV harga (high, low, close)
2. **Indikator** → Semua indikator dihitung secara paralel
3. **Scoring Engine** → Setiap indikator menyumbang skor (Long & Short)
4. **Filter** → Choppiness Index dan/atau ADX memfilter tren
5. **Entry Engine** → Jika skor ≥ *threshold* dan filter lolos → buka posisi
6. **Exit Engine** → Pantau kondisi exit (ST, skor, EMA, dll)

---

## Komponen Utama

### Indicators

| Indikator | Parameter | Dokumen |
|-----------|-----------|---------|
| **Supertrend 1** | Period=10, Multiplier=1 | [docs/indicators/supertrend.md](../indicators/supertrend.md) |
| **Supertrend 2** | Period=11, Multiplier=2 | [docs/indicators/supertrend.md](../indicators/supertrend.md) |
| **Supertrend 3** | Period=12, Multiplier=3 | [docs/indicators/supertrend.md](../indicators/supertrend.md) |
| **EMA Slow** | Period=200 | [docs/indicators/ema.md](../indicators/ema.md) |
| **EMA Fast** | Period=20 | [docs/indicators/ema.md](../indicators/ema.md) |
| **Stochastic RSI** | RSI=14, Stoch=14, K=3, D=3 | [docs/indicators/stochastic_rsi.md](../indicators/stochastic_rsi.md) |
| **ADX / DMI** | DI Length=14, ADX Smooth=14 | [docs/indicators/adx.md](../indicators/adx.md) |
| **Choppiness Index** | Period=14, Threshold=38.2 | — |

### Scoring Categories

| Kategori | Komponen | Bobot Maks |
|----------|----------|-----------|
| **Supertrend** | ST flip, alignment, direction | 55 |
| **Stochastic RSI** | K cross D, oversold, K>50 | 90 |
| **EMA** | Cross, distance, slope | 80 |
| **ADX/DMI** | Threshold, DI cross, dominance | 105 |
| **Choppiness Index** | CI < 30, CI turun | 15 |
| **Persistence** | ST, Stoch, ADX, EMA berkelanjutan | 30 |

> Detail lengkap: [Scoring Engine](scoring-engine.md)

### Entry Methods

| Metode | Deskripsi |
|--------|-----------|
| **Single** | 1 posisi, entry saat skor ≥ threshold, position = 0 |
| **Pyramid** | Multiple posisi bertingkat, setiap level butuh skor lebih tinggi |
| **Grid** | Placeholder — belum diimplementasikan |

> Detail lengkap: [Entry Methods](entry-methods.md)

### Exit Methods

| Metode | Logika |
|--------|--------|
| **Supertrend 1** | Close crossunder ST1 (long) / crossover ST1 (short) |
| **Supertrend 2** | Close crossunder ST2 (long) / crossover ST2 (short) |
| **Supertrend 3** | Close crossunder ST3 (long) / crossover ST3 (short) |
| **Scoring** | Score turun di bawah exitScoring |
| **Scoring & Long EMA** | Score lemah ATAU close melewati EMA 200 |
| **Scoring Bars Since Threshold** | Score sudah lemah > 2 bar |
| **Scoring Bars Since + Slow EMA** | Score lemah > 2 bar DAN close melewati EMA 200 |

> Detail lengkap: [Exit Methods](exit-methods.md)

---

## Konfigurasi Global

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `allowLong` | true | Izinkan entry long |
| `allowShort` | true | Izinkan entry short |
| `entryMethod` | Single | Single / Pyramid / Grid |
| `maxPyramid` | 5 | Maksimum level pyramid |
| `pyramidMultiplier` | 5 | Kenaikan skor per level pyramid |
| `weightedEntryValue` | 100 | Skor minimum untuk entry |
| `exitPositionMethod` | Supertrend 3 | Metode exit |
| `exitScoring` | 50 | Ambang skor untuk exit (metode Scoring) |

---

## Trend Filters

Dua filter opsional untuk memastikan entry hanya terjadi saat market *trending*:

### 1. Choppiness Index Filter

```
isTrendingCI = CI < 38.2
chopFilter = useChoppinessIndex ? isTrendingCI : true
```

- CI < 38.2 → Market *trending* (filter lolos)
- CI ≥ 38.2 → Market *choppy* (filter tidak lolos)

### 2. ADX Filter

```
isTrendingADX = ADX > 25
adxFilter = useAdxFilter ? isTrendingADX : true
```

- ADX > 25 → Tren cukup kuat (filter lolos)
- ADX ≤ 25 → Tren lemah (filter tidak lolos)

### Entry Conditions

```
longCondition  = close > ema200 AND chopFilter AND adxFilter AND longScore ≥ weightedEntryValue
shortCondition = close < ema200 AND chopFilter AND adxFilter AND shortScore ≥ weightedEntryValue
```

---

## Diagram Alir Entry Long

```
                    ┌──────────────┐
                    │   OHLCV Data │
                    └──────┬───────┘
                           ▼
              ┌──────────────────────┐
              │  Hitung Indicators   │
              │  ST1, ST2, ST3, EMA  │
              │  StochRSI, ADX, CI   │
              └──────────┬───────────┘
                         ▼
              ┌──────────────────────┐
              │   Scoring Engine     │
              │  longScore = 0       │
              │  + ST scoring  (max55)│
              │  + Stoch scoring(max90)│
              │  + EMA scoring (max80)│
              │  + ADX scoring (max105)│
              │  + CI scoring  (max15)│
              │  + Persistence (max30)│
              └──────────┬───────────┘
                         ▼
              ┌──────────────────────┐
              │   Trend Filters      │
              │  chopFilter?         │
              │  adxFilter?          │
              └──────────┬───────────┘
                         ▼
              ┌──────────────────────┐
              │   Entry Decision     │
              │  close > ema200?     │
              │  longScore ≥ 100?    │
              │  position == 0?      │
              └──────────┬───────────┘
                         ▼
                    ┌──────────┐
                    │  ENTRY!  │
                    └──────────┘
```

---

## Referensi

- Kode sumber asli: `src/pinescript/weighted_system.pine`
- [Scoring Engine — Detail Lengkap](scoring-engine.md)
- [Entry Methods](entry-methods.md)
- [Exit Methods](exit-methods.md)
- [Dokumentasi Indikator](../indicators/)
