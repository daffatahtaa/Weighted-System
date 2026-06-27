import numpy as np
import pandas as pd


def supertrend(df: pd.DataFrame, atr_multiplier: float = 3.0, atr_length: int = 10) -> pd.DataFrame:
    """Calculate Supertrend indicator.

    Supertrend adalah trend-following indicator yang menggabungkan volatilitas (ATR)
    dengan harga untuk menghasilkan sinyal arah tren yang halus.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns 'high', 'low', 'close'.
    atr_multiplier : float, optional
        Multiplier for ATR to determine band width (default 3.0).
    atr_length : int, optional
        Period for ATR calculation (default 10).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - 'supertrend': Supertrend line values
        - 'trend': Trend direction (1 = uptrend, -1 = downtrend)
        - 'upper_band': Upper ATR band (hl2 + multiplier * ATR)
        - 'lower_band': Lower ATR band (hl2 - multiplier * ATR)
    """
    high = df['high']
    low = df['low']
    close = df['close']

    # ── Average True Range ────────────────────────────────────────
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)

    atr = tr.rolling(window=atr_length).mean()

    # ── Basic Bands ───────────────────────────────────────────────
    hl2 = (high + low) / 2
    upper_band = hl2 + (atr_multiplier * atr)
    lower_band = hl2 - (atr_multiplier * atr)

    # ── Determine Trend Direction & Supertrend Line ───────────────
    supertrend = pd.Series(np.nan, index=df.index)
    trend = pd.Series(0, index=df.index, dtype=int)

    for i in range(1, len(df)):
        if i == 1:
            # Initialize: uptrend if close >= lower_band
            if close.iloc[i] >= lower_band.iloc[i]:
                trend.iloc[i] = 1
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                trend.iloc[i] = -1
                supertrend.iloc[i] = upper_band.iloc[i]
        else:
            # ── Check trend reversal ──────────────────────────
            if close.iloc[i] > supertrend.iloc[i - 1] and trend.iloc[i - 1] == -1:
                # Reverse to uptrend
                trend.iloc[i] = 1
            elif close.iloc[i] < supertrend.iloc[i - 1] and trend.iloc[i - 1] == 1:
                # Reverse to downtrend
                trend.iloc[i] = -1
            else:
                # Continue previous trend
                trend.iloc[i] = trend.iloc[i - 1]

            # ── Set supertrend line ───────────────────────────
            if trend.iloc[i] == 1:
                supertrend.iloc[i] = max(lower_band.iloc[i], supertrend.iloc[i - 1])
            else:
                supertrend.iloc[i] = min(upper_band.iloc[i], supertrend.iloc[i - 1])

    return pd.DataFrame({
        'supertrend': supertrend,
        'trend': trend,
        'upper_band': upper_band,
        'lower_band': lower_band,
    })