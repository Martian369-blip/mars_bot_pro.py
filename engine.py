import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from config import INSTRUMENTS, TIMEFRAMES

def safe_download(ticker, fallback, interval, period):
    try:
        df = yf.download(ticker, interval=interval, period=period, progress=False)
        if df is None or df.empty or len(df) < 30:
            df = yf.download(fallback, interval=interval, period=period, progress=False)
        if df is not None and not df.empty and isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna().copy() if df is not None and not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def fetch_all_frames(symbol_key, tf_label):
    spec = INSTRUMENTS[symbol_key]
    interval, period = TIMEFRAMES[tf_label]

    df = safe_download(spec["ticker"], spec["fallback"], interval, period)
    df_1h = safe_download(spec["ticker"], spec["fallback"], "1h", "1mo")
    df_1d = safe_download(spec["ticker"], spec["fallback"], "1d", "6mo")

    zar_df = safe_download("ZAR=X", "ZAR=X", "1h", "5d")
    usdzar = float(zar_df["Close"].iloc[-1]) if not zar_df.empty else 16.77

    return df, df_1h, df_1d, usdzar

def add_indicators(df):
    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    df["EMA9"] = close.ewm(span=9, adjust=False).mean()
    df["EMA20"] = close.ewm(span=20, adjust=False).mean()
    df["EMA50"] = close.ewm(span=50, adjust=False).mean()

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI"] = (100 - (100 / (1 + rs))).fillna(50.0)

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR"] = tr.ewm(alpha=1/14, min_periods=14, adjust=False).mean().bfill()
    return df

def check_sast_session():
    sast = pytz.timezone("Africa/Johannesburg")
    now_sast = datetime.now(sast)
    mins = now_sast.hour * 60 + now_sast.minute

    in_london = (10 * 60 + 15) <= mins <= (11 * 60 + 55)
    in_ny = (15 * 60 + 40) <= mins <= (18 * 60 + 0)
    in_news_lockout = (15 * 60 + 25) <= mins < (15 * 60 + 40)

    if in_london:
        return True, f"🟢 LONDON LIQUIDITY ACTIVE ({now_sast.strftime('%H:%M')} SAST)"
    elif in_ny:
        return True, f"🟢 NEW YORK LIQUIDITY ACTIVE ({now_sast.strftime('%H:%M')} SAST)"
    elif in_news_lockout:
        return False, f"🛑 U.S. PPI LOCKOUT ({now_sast.strftime('%H:%M')} SAST — Wait until 15:40)"
    else:
        return False, f"🟡 OFF-PEAK ({now_sast.strftime('%H:%M')} SAST — Trade 10:15–11:55 & 15:40–18:00)"

def generate_signal(symbol_key, tf_label, df, df_1h, df_1d, usdzar, balance, floor, max_risk_zar, lot_size, spread, enforce_gate):
    spec = INSTRUMENTS[symbol_key]
    live_bid = float(df["Close"].iloc[-1])
    live_ask = live_bid + spread

    closed = df.iloc[-2]
    htf_1h = df_1h.iloc[-2]
    htf_1d = df_1d.iloc[-2] if not df_1d.empty else htf_1h

    # Technical Scores (Short-Term, Intermediate, Long-Term) matching XM UI
    st_bear = closed["Close"] < closed["EMA20"]
    it_bear = htf_1h["Close"] < htf_1h["EMA20"] and htf_1h["EMA20"] < htf_1h["EMA50"]
    lt_bear = htf_1d["Close"] < htf_1d["EMA20"]

    c_close = float(closed["Close"])
    c_open = float(closed["Open"])
    c_ema9 = float(closed["EMA9"])
    c_ema20 = float(closed["EMA20"])
    c_rsi = float(closed["RSI"])
    c_atr = float(closed["ATR"])

    bearish_candle = (c_close < c_open) and (c_close < c_ema9) and (c_close < c_ema20)
    bullish_candle = (c_close > c_open) and (c_close > c_ema9) and (c_close > c_ema20)

    raw_sl = min(max(c_atr * 1.15, spread * 3.5), spec["max_sl_points"])
    max_move = (max_risk_zar / (usdzar * spec["usd_per_unit_001"] * (lot_size / 0.01))) - spread
    sl_dist = max(min(raw_sl, max_move), spread * 2.2)
    tp_dist = sl_dist * 2.2

    risk_zar = (sl_dist + spread) * spec["usd_per_unit_001"] * (lot_size / 0.01) * usdzar
    reward_zar = (tp_dist - spread) * spec["usd_per_unit_001"] * (lot_size / 0.01) * usdzar

    session_ok, session_msg = check_sast_session()

    sig = {
        "type": "WAIT",
        "title": "⏳ WAIT / NO ENTRY — PROTECT CAPITAL",
        "reason": "",
        "session_msg": session_msg,
        "entry": live_bid,
        "sl": 0.0,
        "be": 0.0,
        "tp": 0.0,
        "risk_zar": risk_zar,
        "reward_zar": reward_zar,
        "st_bear": st_bear,
        "it_bear": it_bear,
        "lt_bear": lt_bear,
        "rsi": c_rsi,
        "atr": c_atr,
        "ema20": c_ema20,
        "close": c_close
    }

    if enforce_gate and not session_ok:
        sig["title"] = "🛑 WAIT — SESSION LIQUIDITY GATE LOCKED"
        sig["reason"] = f"{session_msg}. Avoiding midday/pre-open chop. Next window: 15:40 SAST."
    elif balance <= floor:
        sig["title"] = "🛑 HARD DAILY FLOOR REACHED — LOCKED"
        sig["reason"] = f"Balance (R{balance:.2f}) is at or below your R{floor:.2f} floor."
    elif it_bear and bearish_candle and (34.0 <= c_rsi <= 62.0):
        sig["type"] = "SELL"
        sig["title"] = f"💥 ACCURATE SELL / SHORT SIGNAL — {symbol_key}"
        sig["entry"] = live_bid
        sig["sl"] = live_bid + sl_dist
        sig["tp"] = live_bid - tp_dist
        sig["be"] = live_bid - (sl_dist * 1.2)
        sig["reason"] = f"1H downtrend + closed {tf_label} candle rejected below EMA9/EMA20 (RSI {c_rsi:.1f})."
    elif (not it_bear) and bullish_candle and (38.0 <= c_rsi <= 66.0):
        sig["type"] = "BUY"
        sig["title"] = f"🚀 ACCURATE BUY / LONG SIGNAL — {symbol_key}"
        sig["entry"] = live_ask
        sig["sl"] = live_ask - sl_dist
        sig["tp"] = live_ask + tp_dist
        sig["be"] = live_ask + (sl_dist * 1.2)
        sig["reason"] = f"1H uptrend + closed {tf_label} candle closed bullish above EMA9/EMA20 (RSI {c_rsi:.1f})."
    else:
        if c_rsi < 34.0:
            sig["reason"] = f"RSI oversold ({c_rsi:.1f}). Do NOT chase shorts at support—wait for EMA pullback."
        elif c_rsi > 66.0:
            sig["reason"] = f"RSI overbought ({c_rsi:.1f}). Do NOT chase longs at resistance—wait for pullback."
        else:
            sig["reason"] = f"Waiting for closed {tf_label} candle to align with 1H trend (RSI {c_rsi:.1f})."

    return sig
