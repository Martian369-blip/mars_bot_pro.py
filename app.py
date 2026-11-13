import streamlit as st
import numpy as np
import plotly.graph_objects as go
from config import INSTRUMENTS, CUSTOM_CSS
from engine import fetch_all_frames, add_indicators, generate_signal

st.set_page_config(
    page_title="MARS_BOT PRO | Institutional Terminal",
    page_icon="👽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR: LIVE ACCOUNT & XM CALIBRATION
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 👽 MARS_BOT PRO Settings")
    account_balance = st.number_input("Live Account Balance (ZAR)", value=430.00, step=10.0)
    daily_floor = st.number_input("Hard Daily Floor (ZAR)", value=400.00, step=10.0)
    max_risk_zar = st.number_input("Max Risk Per Trade (ZAR)", value=65.00, step=5.0)
    lot_size = st.selectbox("Fixed Position Size (Lots)", [0.01, 0.02], index=0)
    st.markdown("---")
    st.markdown("#### 🔧 XM Broker Calibration")
    price_offset = st.number_input(
        "Gold Broker Offset (+/-)",
        value=-7.80,
        step=0.10,
        help="XM Spot Gold minus GC=F Futures (e.g., -7.80 aligns GC=F to XM Spot)."
    )
    custom_spread = st.number_input("Override Spread (0 = auto)", value=0.00, step=0.01, format="%.5f")
    enforce_session_gate = st.checkbox("Enforce London/NY Liquidity Gate (SAST)", value=True)

# ---------------------------------------------------------
# TOP CONTROLS (XM INSTRUMENT + TIMEFRAME SELECTOR)
# ---------------------------------------------------------
selected_pair = st.selectbox("Select Instrument", list(INSTRUMENTS.keys()), index=0, label_visibility="collapsed")
selected_tf = st.radio("Timeframe", ["15m", "1H", "4H", "1D"], index=0, horizontal=True, label_visibility="collapsed")

spec = INSTRUMENTS[selected_pair]
dec = spec["decimals"]
spread = custom_spread if custom_spread > 0 else spec["spread"]
active_offset = price_offset if selected_pair == "GOLD (XAU/USD)" else 0.0

df_raw, df_1h_raw, df_1d_raw, usdzar = fetch_all_frames(selected_pair, selected_tf)

if df_raw.empty or df_1h_raw.empty:
    st.warning("Market feed is refreshing. Tap 'Rerun' in the top-right menu.")
    st.stop()

df = add_indicators(df_raw)
df_1h = add_indicators(df_1h_raw)
df_1d = add_indicators(df_1d_raw) if not df_1d_raw.empty else df_1h

for col in ["Open", "High", "Low", "Close", "EMA9", "EMA20", "EMA50"]:
    df[col] = df[col] + active_offset
    df_1h[col] = df_1h[col] + active_offset
    if col in df_1d.columns:
        df_1d[col] = df_1d[col] + active_offset

live_bid = float(df["Close"].iloc[-1])
live_ask = live_bid + spread

# Daily Range & Change Stats (Matching XM Screenshot 2)
day_slice = df.tail(24)
day_open = float(day_slice["Open"].iloc[0])
day_low = float(day_slice["Low"].min())
day_high = float(day_slice["High"].max())
day_diff = live_bid - day_open
day_pct = (day_diff / day_open) * 100 if day_open != 0 else 0.0
range_pos = int(np.clip(((live_bid - day_low) / max(day_high - day_low, 1e-6)) * 100, 2, 98))

# Support & Resistance Levels (Matching XM Screenshot 2 Footer)
support_lvl = float(df_1h["Low"].tail(48).min())
resist_lvl = float(df_1h["High"].tail(48).max())

# ---------------------------------------------------------
# 1. HEADER TICKER (MATCHING SCREENSHOT 1)
# ---------------------------------------------------------
change_class = "price-up" if day_diff >= 0 else "price-down"
arrow = "↗" if day_diff >= 0 else "↘"
st.markdown(
    f"<div class='ticker-title'>{selected_pair} "
    f"<span class='{change_class}'>{day_diff:+.{dec}f} {arrow} {day_pct:+.2f}% · {selected_tf}</span>"
    f"</div>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 2. CANDLESTICK CHART (DARK XM / TRADINGVIEW STYLE)
# ---------------------------------------------------------
plot_df = df.tail(55)
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=plot_df.index,
    open=plot_df["Open"],
    high=plot_df["High"],
    low=plot_df["Low"],
    close=plot_df["Close"],
    increasing_line_color="#19B36B",
    decreasing_line_color="#E03E52",
    increasing_fillcolor="#19B36B",
    decreasing_fillcolor="#E03E52"
))
fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["EMA9"], line=dict(color="#38BDF8", width=1.3)))
fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["EMA20"], line=dict(color="#FBBF24", width=1.3)))

fig.update_layout(
    height=270,
    margin=dict(l=5, r=45, t=8, b=8),
    paper_bgcolor="#111622",
    plot_bgcolor="#111622",
    xaxis_rangeslider_visible=False,
    showlegend=False,
    xaxis=dict(gridcolor="#1E2638", showgrid=True, color="#8B98B0"),
    yaxis=dict(side="right", gridcolor="#1E2638", showgrid=True, color="#8B98B0", tickformat=f".{dec}f")
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ---------------------------------------------------------
# 3. SELL | SPREAD | BUY QUOTE BAR
# ---------------------------------------------------------
spread_display = f"{spread:.{dec}f}" if selected_pair == "GOLD (XAU/USD)" else f"{spread / spec['pip_size']:.1f} pips"

st.markdown(f"""
<div class="quote-grid">
    <div class="sell-box">
        <div class="quote-label">SELL</div>
        <div class="quote-val">{live_bid:.{dec}f}</div>
    </div>
    <div class="spread-pill">{spread_display}</div>
    <div class="buy-box">
        <div class="quote-label">BUY</div>
        <div class="quote-val">{live_ask:.{dec}f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. ACCURATE SIGNALS (DIRECTLY UNDERNEATH SPREAD)
# ---------------------------------------------------------
sig = generate_signal(
    selected_pair, selected_tf, df, df_1h, df_1d, usdzar,
    account_balance, daily_floor, max_risk_zar, lot_size, spread, enforce_session_gate
)

card_css = "signal-card-sell" if sig["type"] == "SELL" else ("signal-card-buy" if sig["type"] == "BUY" else "signal-card-wait")

st.markdown(f"""
<div class="{card_css}">
    <div style="font-size:1.05rem; font-weight:800; margin-bottom:4px;">{sig['title']}</div>
    <div style="font-size:0.86rem; color:#CBD5E1; margin-bottom:8px;">{sig['reason']}</div>
    <div style="font-size:0.78rem; color:#94A3B8;">{sig['session_msg']} · USD/ZAR: <b>R{usdzar:.2f}</b> · Lot: <b>{lot_size}</b></div>
</div>
""", unsafe_allow_html=True)

if sig["type"] in ["SELL", "BUY"]:
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Entry</div><div class='metric-mini-val'>{sig['entry']:.{dec}f}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Stop Loss (-R{sig['risk_zar']:.0f})</div><div class='metric-mini-val' style='color:#FF5C70;'>{sig['sl']:.{dec}f}</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Breakeven</div><div class='metric-mini-val' style='color:#38BDF8;'>{sig['be']:.{dec}f}</div></div>", unsafe_allow_html=True)
    with m4:
        st.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Take Profit (+R{sig['reward_zar']:.0f})</div><div class='metric-mini-val' style='color:#2EE58F;'>{sig['tp']:.{dec}f}</div></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. AI OVERVIEW CARD (MATCHING SCREENSHOT 1)
# ---------------------------------------------------------
if sig["it_bear"]:
    bias_badge = "<span class='badge-bearish'>Bearish ↘</span>"
    ai_text = f"{selected_pair} remains under higher-timeframe selling pressure below its 1H 20 & 50 EMAs (RSI {sig['rsi']:.1f}). Prioritize selling pullbacks into EMA9/EMA20 resistance during active London or NY liquidity."
else:
    bias_badge = "<span class='badge-bullish'>Bullish ↗</span>"
    ai_text = f"{selected_pair} holds bullish 1H momentum above its key moving averages (RSI {sig['rsi']:.1f}). Look for pullback continuation entries on closed {selected_tf} candles."

st.markdown(f"""
<div class="xm-card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <span style="font-weight:800; font-size:0.98rem;">✨ AI Overview</span>
        {bias_badge}
    </div>
    <div style="font-size:0.88rem; color:#CBD5E1; line-height:1.45;">{ai_text}</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. MARKET SENTIMENT, DAILY RANGE & TECHNICAL SCORE (SCREENSHOT 2)
# ---------------------------------------------------------
ema_score = 50 + np.clip(((sig["close"] - sig["ema20"]) / max(sig["atr"], 1e-6)) * 12, -25, 25)
buy_pct = int(round((ema_score * 0.5) + (np.clip(sig["rsi"], 15, 85) * 0.5)))
sell_pct = 100 - buy_pct

st_label = "<span style='color:#E03E52;'>Bearish</span>" if sig["st_bear"] else "<span style='color:#19B36B;'>Bullish</span>"
it_label = "<span style='color:#E03E52;'>Bearish</span>" if sig["it_bear"] else "<span style='color:#19B36B;'>Bullish</span>"
lt_label = "<span style='color:#E03E52;'>Bearish</span>" if sig["lt_bear"] else "<span style='color:#19B36B;'>Bullish</span>"

st_bar = "<div style='width:55%; height:100%; background:#E03E52;'></div>" if sig["st_bear"] else "<div style='width:55%; height:100%; background:#19B36B; margin-left:45%;'></div>"
it_bar = "<div style='width:55%; height:100%; background:#E03E52;'></div>" if sig["it_bear"] else "<div style='width:55%; height:100%; background:#19B36B; margin-left:45%;'></div>"
lt_bar = "<div style='width:55%; height:100%; background:#E03E52;'></div>" if sig["lt_bear"] else "<div style='width:55%; height:100%; background:#19B36B; margin-left:45%;'></div>"

st.markdown(f"""
<div class="xm-card">
    <div style="font-weight:800; font-size:1.0rem;">Market Sentiment</div>
