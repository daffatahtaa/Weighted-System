import numpy as np
import pandas as pd

def rsi(close: pd.Series, rsi_length: int = 14) -> pd.Series:
    delta = close.diff()
    
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.ewm(alpha = 1 / rsi_length, adjust = False).mean()
    avg_loss = loss.ewm(alpha = 1 / rsi_length, adjust = False).mean()
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
    
def stochastic(series: pd.Series, stochastic_length: int = 14) -> pd.Series:
    lowest = series.rolling(window = stochastic_length).min()
    highest = series.rolling(window = stochastic_length).max()
    
    denominator = highest - lowest
    
    return ((series - lowest) / denominator.replace(0, np.nan) * 100)

def calculate_stochastic_rsi(close: pd.Series, rsi_length: int = 14, stochastic_length: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> pd.DataFrame:
    rsi_values = rsi(close = close, rsi_length = rsi_length)
    
    stoch = stochastic(rsi_values = rsi_values, stochastic_length = stochastic_length)
    
    k = stoch.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()
    
    return pd.DataFrame({
        'rsi': rsi_values,
        'stochastic': stoch,
        'stoch_k': k,
        'stoch_d': d,
    })