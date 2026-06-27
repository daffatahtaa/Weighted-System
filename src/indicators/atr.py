import numpy as np
import pandas as pd


def atr(df: pd.DataFrame, length: int = 14, use_wilder: bool = False) -> pd.Series:
    """Calculate Average True Range (ATR).

    ATR mengukur volatilitas pasar dengan merata-ratakan True Range
    selama N periode. Semakin tinggi ATR, semakin volatil market.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns 'high', 'low', 'close'.
    length : int, optional
        Period for ATR calculation (default 14).
    use_wilder : bool, optional
        If True, uses Wilder's smoothing (EMA-style, alpha=1/length).
        If False, uses simple moving average (default False).

    Returns
    -------
    pd.Series
        ATR values.
    """
    high = df['high']
    low = df['low']
    close = df['close']

    # ── True Range ────────────────────────────────────────────────
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)

    # ── Average True Range ────────────────────────────────────────
    if use_wilder:
        # Wilder's smoothing: first SMA, then:
        #   atr[i] = (atr[i-1] * (length - 1) + tr[i]) / length
        atr_values = tr.copy().astype(float)
        atr_values.iloc[:length] = np.nan
        first_val = tr.iloc[1:length + 1].mean()
        if pd.notna(first_val):
            atr_values.iloc[length] = first_val
            for i in range(length + 1, len(tr)):
                atr_values.iloc[i] = (
                    atr_values.iloc[i - 1] * (length - 1) + tr.iloc[i]
                ) / length
        return atr_values

    return tr.rolling(window=length).mean()
