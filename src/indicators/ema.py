def ema (df, period):
    return df["close"].ewm(span = period, adjust = False).mean()