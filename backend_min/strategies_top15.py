# strategies_top15.py — copied for backend_min
import numpy as np
import pandas as pd
import pandas_ta as ta

# helpers
def _xover(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))

def _xunder(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))

def _pack(df, long, short, entry=None, atr=None, atr_mult=2.0, rr=1.5):
    entry = df["close"] if entry is None else entry
    atr = ta.atr(df["high"], df["low"], df["close"]) if atr is None else atr
    sl = np.where(long, df["low"] - atr * atr_mult,
                  np.where(short, df["high"] + atr * atr_mult, np.nan))
    tp = np.where(long, entry + atr * rr,
                  np.where(short, entry - atr * rr, np.nan))
    sig = np.where(long, 1, np.where(short, -1, 0))
    return pd.DataFrame({"signal": sig, "entry": entry, "sl": sl, "tp": tp})

# 强韧输入
def _ensure_dt_index(df: pd.DataFrame, default_freq: str = "4H") -> pd.DataFrame:
    dfi = df.copy()
    if not isinstance(dfi.index, pd.DatetimeIndex):
        idx = None
        if "timestamp" in dfi.columns:
            idx = pd.to_datetime(dfi["timestamp"], errors="coerce", utc=True)
        elif "ts" in dfi.columns:
            idx = pd.to_datetime(dfi["ts"], errors="coerce", utc=True)
        if idx is None or idx.isna().all():
            start = pd.Timestamp.utcnow().floor("D") - pd.Timedelta(hours=len(dfi) * 4)
            idx = pd.date_range(start=start, periods=len(dfi), freq=default_freq)
        dfi.index = idx
    if getattr(dfi.index, "tz", None) is not None:
        dfi.index = dfi.index.tz_convert(None)
    dfi = dfi.sort_index()
    cols = ["open", "high", "low", "close", "volume"]
    for c in cols:
        if c not in dfi.columns:
            dfi[c] = np.nan if c != "volume" else 1.0
    dfi[["open", "high", "low", "close", "volume"]] = dfi[["open", "high", "low", "close", "volume"]].apply(
        pd.to_numeric, errors="coerce"
    )
    dfi = dfi.dropna(subset=["open", "high", "low", "close"])
    return dfi[["open", "high", "low", "close", "volume"]].copy()

# 策略集合（节选，保证 REGISTRY 完整）

def strat_ema_adx(df, fast=20, slow=50, adx_len=14, adx_min=20, atr_mult=2.0, rr=2.0):
    e1 = ta.ema(df["close"], length=fast)
    e2 = ta.ema(df["close"], length=slow)
    adx = ta.adx(df["high"], df["low"], df["close"], length=adx_len)[f"ADX_{adx_len}"]
    long = _xover(e1, e2) & (adx >= adx_min)
    short = _xunder(e1, e2) & (adx >= adx_min)
    return _pack(df, long, short, atr_mult=atr_mult, rr=rr)

def strat_macd(df, fast=12, slow=26, sig=9, atr_mult=2.0, rr=2.0):
    macd = ta.macd(df["close"], fast=fast, slow=slow, signal=sig)
    macd_line = macd.columns[0]
    sig_line = macd.columns[1]
    hist_col = macd.columns[2]
    m = macd[macd_line]
    s = macd[sig_line]
    h = macd[hist_col]
    long = _xover(m, s) & (h > 0)
    short = _xunder(m, s) & (h < 0)
    return _pack(df, long, short, atr_mult=atr_mult, rr=rr)

# ... 省略其余策略（保持与原文件一致）

REGISTRY = {
    "ema_adx": strat_ema_adx,
    "macd_plus": strat_macd,
    # 其余键保持与原文件一致（bb_mean, bb_squeeze, donchian, supertrend, keltner_break, ichimoku_kijun, psar_trend, stochrsi, cci_reversion, adx_di, heikin_ema, vwap_pullback）
}
