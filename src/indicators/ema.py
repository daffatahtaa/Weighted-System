import pandas as pd


def ema(df: pd.Series, lengths: list[int]) -> pd.DataFrame:
    """Calculate Exponential Moving Average (EMA) for multiple periods.

    Parameters
    ----------
    df : pd.Series
        Price series (typically 'close' prices).
    lengths : list[int]
        List of EMA periods to calculate, e.g. [9, 21, 50].

    Returns
    -------
    pd.DataFrame
        DataFrame with columns named 'ema_{length}' for each period.
    """
    data = {}

    for length in lengths:
        data[f'ema_{length}'] = df.ewm(span=length, adjust=False).mean()

    return pd.DataFrame(data)