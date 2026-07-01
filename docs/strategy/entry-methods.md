# Entry Methods

## Gambaran Umum

Weighted System mendukung **tiga metode entry** yang dapat dipilih melalui parameter `entryMethod`. Setiap metode memiliki profil risiko yang berbeda:

| Metode | Risiko | Jumlah Posisi | Kapan Cocok |
|--------|--------|---------------|-------------|
| **Single** | Rendah | 1 | Trader konservatif, modal terbatas |
| **Pyramid** | Sedang | 2–5 | Trader agresif, yakin tren kuat |
| **Grid** | Tinggi | Banyak | Belum diimplementasikan |

---

## 1. Single Entry

### Logika

Buka **satu posisi** saat kondisi entry terpenuhi dan belum ada posisi terbuka.

```
IF longCondition == true AND strategy.position_size == 0:
    → strategy.entry("Long", strategy.long)
```

### Kode (Pine Script)

```python
if (entryMethod == EXT_ENTRY1 and longCondition and allowLong and strategy.position_size == 0):
    strategy.entry("Long", strategy.long, comment=str.tostring(longScore))
```

### Karakteristik

| Aspek | Detail |
|-------|--------|
| Label entry | `"Long"` / `"Short"` |
| Comment | Nilai skor saat entry |
| Exit | Satu `strategy.close()` untuk semua |
| Cocok untuk | Backtest awal, akun kecil, risk-adverse |

### Flowchart

```
                    ┌──────────────────┐
                    │  longCondition?  │
                    │  score ≥ 100     │
                    │  close > ema200  │
                    │  chopFilter?     │
                    │  adxFilter?      │
                    └────────┬─────────┘
                             ▼ YES
                    ┌──────────────────┐
                    │  position == 0?  │
                    └────────┬─────────┘
                             ▼ YES
                    ┌──────────────────┐
                    │  ENTRY "Long"    │
                    │  (1 position)    │
                    └──────────────────┘
```

---

## 2. Pyramid Entry

### Logika

Buka **multiple positions** secara bertahap. Setiap level pyramid membutuhkan skor yang lebih tinggi dari level sebelumnya. Ini memastikan entry tambahan hanya terjadi jika keyakinan semakin kuat.

### Formula Threshold

```
requiredScore(level) = weightedEntryValue + (pyramidMultiplier × level)
```

| Level | Rumus | Threshold (default) |
|-------|-------|---------------------|
| 1 (posisi 0) | 100 + (5 × 0) | **100** |
| 2 (posisi 1) | 100 + (5 × 1) | **105** |
| 3 (posisi 2) | 100 + (5 × 2) | **110** |
| 4 (posisi 3) | 100 + (5 × 3) | **115** |
| 5 (posisi 4) | 100 + (5 × 4) | **120** |
| 6 (posisi 5) | 100 + (5 × 5) | **125** |

### Kode (Pine Script)

```python
if (entryMethod == EXT_ENTRY2 and longCondition and allowLong):
    for i = 0 to maxPyramid by +1:
        requiredScore = weightedEntryValue + (pyramidMultiplier * i)
        if strategy.opentrades == i and longScore >= requiredScore:
            strategy.entry(
                "Long_" + str.tostring(i + 1),
                strategy.long,
                comment="Long_" + str.tostring(i + 1) + "\n" + str.tostring(longScore)
            )
```

### Cara Kerja

1. **Bar 1**: Skor = 105, posisi = 0 → entry `Long_1` (threshold 100 ✅)
2. **Bar 2**: Skor = 112, posisi = 1 → entry `Long_2` (threshold 105 ✅)
3. **Bar 3**: Skor = 108, posisi = 2 → **tidak entry** (threshold 110 ❌)
4. **Bar 4**: Skor = 125, posisi = 2 → entry `Long_3` (threshold 110 ✅)

### Flowchart

```
                    ┌──────────────────┐
                    │  longCondition?  │
                    └────────┬─────────┘
                             ▼ YES
                    ┌──────────────────┐
                    │  Loop i=0..max   │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────────────────┐
                    │  strategy.opentrades == i    │
                    │  AND                         │
                    │  longScore ≥ requiredScore   │
                    └────────┬─────────────────────┘
                             ▼ YES
                    ┌──────────────────┐
                    │  ENTRY "Long_i"  │
                    │  (pyramid level) │
                    └──────────────────┘
```

### Parameter Pyramid

| Parameter | Default | Fungsi |
|-----------|---------|--------|
| `maxPyramid` | 5 | Maksimum level pyramid (posisi) |
| `pyramidMultiplier` | 5 | Kenaikan threshold per level |
| `weightedEntryValue` | 100 | Threshold level pertama |

### Contoh Skenario

```
weightedEntryValue = 100
pyramidMultiplier  = 5
maxPyramid         = 3

Level 1: butuh skor ≥ 100  → entry Long_1
Level 2: butuh skor ≥ 105  → entry Long_2
Level 3: butuh skor ≥ 110  → entry Long_3

Jika skor turun ke 95 → tidak ada entry baru
```

---

## 3. Grid Entry

### Status

> ⚠️ **Belum diimplementasikan.** Grid Entry adalah placeholder untuk ekspansi di masa depan.

### Rencana (Future)

Grid Entry akan membuka serangkaian posisi *buy limit / sell limit* pada level harga yang telah ditentukan. Cocok untuk strategi *mean reversion* dan *market making*.

---

## Perbandingan Entry Methods

| Aspek | Single | Pyramid | Grid |
|-------|--------|---------|------|
| Jumlah posisi | 1 | 2–maxPyramid | Banyak |
| Threshold entry | Tetap | Bertingkat | Level harga |
| Risiko per trade | Rendah | Sedang | Tinggi |
| Potensi profit | Sedang | Tinggi | Tinggi |
| Kompleksitas | Rendah | Sedang | Tinggi |
| Cocok untuk | Konservatif | Agresif | Algoritmik |
| Status | ✅ Aktif | ✅ Aktif | ❌ Belum |

---

## Exit Bersamaan dengan Entry

Penting: exit dilakukan per label entry.

### Single

```python
# Satu posisi — satu close
if exitLong:
    strategy.close("Long", ...)
```

### Pyramid

```python
# Multiple positions — close satu per satu
if exitLong:
    for i = 0 to maxPyramid by +1:
        strategy.close("Long_" + str.tostring(i + 1))
```

---

## Referensi

- Kode sumber: `src/pinescript/weighted_system.pine` — bagian ENTRY
- [Overview Strategi](overview.md)
- [Scoring Engine](scoring-engine.md)
- [Exit Methods](exit-methods.md)
