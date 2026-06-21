import numpy as np
import pandas as pd

def rsi(close: pd.Series, rsi_length: int = 14) -> pd.Series:
    """Calculate Relative Strength Index (RSI) using Wilder's smoothing EMA.

    Parameters
    ----------
    close : pd.Series
        Closing price series.
    rsi_length : int, optional
        Period for RSI calculation (default 14).

    Returns
    -------
    pd.Series
        RSI values ranging from 0 to 100.
    """
    delta = close.diff()
    
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.ewm(alpha = 1 / rsi_length, adjust = False).mean()
    avg_loss = loss.ewm(alpha = 1 / rsi_length, adjust = False).mean()
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
    
def stochastic(series: pd.Series, stochastic_length: int = 14) -> pd.Series:
    """Calculate Stochastic Oscillator of a given series.

    Parameters
    ----------
    series : pd.Series
        Input series (e.g. RSI values).
    stochastic_length : int, optional
        Lookback period for lowest/highest calculation (default 14).

    Returns
    -------
    pd.Series
        Stochastic values ranging from 0 to 100.
    """
    lowest = series.rolling(window = stochastic_length).min()
    highest = series.rolling(window = stochastic_length).max()
    
    denominator = highest - lowest
    
    return ((series - lowest) / denominator.replace(0, np.nan) * 100)

def calculate_stochastic_rsi(close: pd.Series, rsi_length: int = 14, stochastic_length: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> pd.DataFrame:
    """Calculate Stochastic RSI (StochRSI) indicator.

    StochRSI applies the stochastic oscillator formula to RSI values
    instead of price, then smooths the result with moving averages.

    Parameters
    ----------
    close : pd.Series
        Closing price series.
    rsi_length : int, optional
        Period for RSI calculation (default 14).
    stochastic_length : int, optional
        Lookback period for stochastic calculation (default 14).
    smooth_k : int, optional
        Smoothing period for %K line (default 3).
    smooth_d : int, optional
        Smoothing period for %D line (default 3).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - 'rsi': RSI values
        - 'stochastic': Raw StochRSI values
        - 'stoch_k': Smoothed %K line
        - 'stoch_d': Signal %D line
    """
    rsi_values = rsi(close = close, rsi_length = rsi_length)
    
    stoch = stochastic(series = rsi_values, stochastic_length = stochastic_length)
    
    k = stoch.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()
    
    return pd.DataFrame({
        'rsi': rsi_values,
        'stochastic': stoch,
        'stoch_k': k,
        'stoch_d': d,
    })