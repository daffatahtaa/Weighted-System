import numpy as np
import pandas as pd


def adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Calculate Average Directional Index (ADX) indicator.

    ADX measures trend strength using +DI and -DI lines.
    Values above 25 indicate a strong trend, below 20 a weak/range-bound market.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns 'high', 'low', 'close'.
    period : int, optional
        Smoothing period for TR, DM, and ADX (default 14).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - 'adx': Average Directional Index (trend strength)
        - 'plus_di': Positive Directional Indicator (+DI)
        - 'minus_di': Negative Directional Indicator (-DI)
        - 'dx': Raw Directional Index before smoothing
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

    # ── Directional Movements ─────────────────────────────────────
    prev_high = high.shift(1)
    prev_low = low.shift(1)

    up_move = high - prev_high
    down_move = prev_low - low

    plus_dm = pd.Series(np.where(
        (up_move > down_move) & (up_move > 0), up_move, 0.0
    ), index=df.index)

    minus_dm = pd.Series(np.where(
        (down_move > up_move) & (down_move > 0), down_move, 0.0
    ), index=df.index)

    # ── Wilder's Smoothing ────────────────────────────────────────
    # First value is simple average, followed by exponential:
    #   smoothed = prev_smoothed - (prev_smoothed / period) + current
    def wilder_smooth(series: pd.Series, period: int) -> pd.Series:
        smoothed = series.copy().astype(float)
        smoothed.iloc[:period] = np.nan
        first_val = series.iloc[1:period + 1].mean()
        if pd.notna(first_val):
            smoothed.iloc[period] = first_val
            for i in range(period + 1, len(series)):
                smoothed.iloc[i] = smoothed.iloc[i - 1] - (smoothed.iloc[i - 1] / period) + series.iloc[i]
        return smoothed

    smoothed_tr = wilder_smooth(tr, period)
    smoothed_plus_dm = wilder_smooth(plus_dm, period)
    smoothed_minus_dm = wilder_smooth(minus_dm, period)

    # ── +DI and -DI ───────────────────────────────────────────────
    plus_di = 100 * smoothed_plus_dm / smoothed_tr.replace(0, np.nan)
    minus_di = 100 * smoothed_minus_dm / smoothed_tr.replace(0, np.nan)

    # ── Directional Index (DX) ────────────────────────────────────
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)

    # ── ADX (smoothed DX) ────────────────────────────────────────
    adx_values = wilder_smooth(dx, period)

    return pd.DataFrame({
        'adx': adx_values,
        'plus_di': plus_di,
        'minus_di': minus_di,
        'dx': dx,
    })
