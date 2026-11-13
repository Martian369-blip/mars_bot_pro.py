import streamlit as st
import numpy as np
import plotly.graph_objects as go
from config import INSTRUMENTS
from design import XM_THEME_CSS
from engine import fetch_all_frames, add_indicators, generate_signal

st.set_page_config(page_title="MARS_BOT PRO 👽", page_icon="👽", layout="wide", initial_sidebar_state="collapsed")
st.markdown(XM_THEME_CSS, unsafe_allow_html=True)

# Direct one-tap switcher to your separate Trading Journal panel
st.page_link("pages/1_Trading_Journal.py", label="📓 Open Trading Journal & Balance Recon", use_container_width=True)

with st.sidebar:
    st.markdown("### 👽 MARS_BOT PRO Settings")
    account_balance = st.number_input("Actual XM Live Balance (ZAR)", value=430.00, step=10.0)
    daily_floor = st.number_input("Hard Daily Floor (ZAR)", value=400.00, step=10.0)
    max_risk_zar = st.number_input("Max Risk Per Trade (ZAR)", value=65.00, step=5.0)
    lot_size = st.selectbox("Fixed Position Size (Lots)", [0.01, 0.02], index=0)
    st.markdown("---")
    price_offset = st.number_input("Gold Broker Offset (+/-)", value=-7.80, step=0.10)
    custom_spread = st.number_input("Override Spread (0 = auto)", value=0.00, step=0.01, format="%.5f")
    enforce_session_gate = st.checkbox("Enforce London/NY Gate (SAST)", value=True)

selected_pair = st.selectbox("Instrument", list(INSTRUMENTS.keys()), index=0, label_visibility="collapsed")
selected_tf = st.radio("TF", ["15m", "1H", "4H", "1D"], index=0, horizontal=True, label_visibility="collapsed")

spec = INSTRUMENTS[selected_pair]
dec = spec["decimals"]
spread = custom_spread if custom_spread > 0 else spec["spread"]
active_offset = price_offset if selected_pair == "GOLD (XAU/USD)" else 0.0

df_raw, df_1h_raw, df_1d_raw, usdzar = fetch_all_frames(selected_pair, selected_tf)
if df_raw.empty or df_1h_raw.empty:
    st.warning("Market feed refreshing. Tap Rerun in top-right menu.")
    st.stop()

df = add_indicators(df_raw)
df_1h = add_indicators(df_1h_raw)
df_1d = add_indicators(df_1d_raw) if not df_1d_raw.empty else df_1h

for col in ["Open", "High", "Low", "Close", "EMA9", "EMA20", "EMA50"]:
    df[col] = df[col] + active_offset
    df_1h[col] = df_1h[col] + active_offset
    if col in df_1d.columns:
        df_1d[col] = df_1d[col] + active_offset

live_bid = float(df["Close"].tail(1).item())
live_ask = live_bid + spread

day_slice = df.tail(24)
day_open = float(day_slice["Open"].head(1).item())
day_low = float(day_slice["Low"].min())
day_high = float(day_slice["High"].max())
day_diff = live_bid - day_open
day_pct = (day_diff / day_open) * 100 if day_open != 0 else 0.0
range_pos = int(np.clip(((live_bid - day_low) / max(day_high - day_low, 1e-6)) * 100, 2, 98))

support_lvl = float(df_1h["Low"].tail(48).min())
resist_lvl = float(df_1h["High"].tail(48).max())

change_class = "price-up" if day_diff >= 0 else "price-down"
arrow = "↗" if day_diff >= 0 else "↘"
st.markdown(f"<div class='ticker-title'>👽 {selected_pair} <span class='{change_class}'>{day_diff:+.{dec}f} {arrow} {day_pct:+.2f}% · {selected_tf}</span></div>", unsafe_allow_html=True)

plot_df = df.tail(55)
fig = go.Figure()
fig.add_trace(go.Candlestick(x=plot_df.index, open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], increasing_line_color="#39FF14", decreasing_line_color="#FF5722", increasing_fillcolor="#39FF14", decreasing_fillcolor="#FF5722"))
fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["EMA9"], line=dict(color="#39FF14", width=1.2, dash="dot")))
fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["EMA20"], line=dict(color="#FF8A65", width=1.4)))
fig.update_layout(height=270, margin=dict(l=5, r=45, t=8, b=8), paper_bgcolor="#0B0E14", plot_bgcolor="#0B0E14", xaxis_rangeslider_visible=False, showlegend=False, xaxis=dict(gridcolor="#181E2B", showgrid=True, color="#8B98B0"), yaxis=dict(side="right", gridcolor="#181E2B", showgrid=True, color="#8B98B0", tickformat=f".{dec}f"))
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

spread_display = f"{spread:.{dec}f}" if selected_pair == "GOLD (XAU/USD)" else f"{spread / spec['pip_size']:.1f} pips"
st.markdown(f"<div class='quote-grid'><div class='sell-box'><div class='quote-label'>SELL (MARS)</div><div class='quote-val'>{live_bid:.{dec}f}</div></div><div class='spread-pill'>{spread_display}</div><div class='buy-box'><div class='quote-label'>BUY (ALIEN)</div><div class='quote-val'>{live_ask:.{dec}f}</div></div></div>", unsafe_allow_html=True)

sig = generate_signal(selected_pair, selected_tf, df, df_1h, df_1d, usdzar, account_balance, daily_floor, max_risk_zar, lot_size, spread, enforce_session_gate)
card_css = "signal-card-sell" if sig["type"] == "SELL" else ("signal-card-buy" if sig["type"] == "BUY" else "signal-card-wait")
st.markdown(f"<div class='{card_css}'><div style='font-size:1.05rem;font-weight:800;margin-bottom:4px;'>{sig['title']}</div><div style='font-size:0.86rem;color:#CBD5E1;margin-bottom:8px;'>{sig['reason']}</div><div style='font-size:0.78rem;color:#94A3B8;'>{sig['session_msg']} · USD/ZAR: <b>R{usdzar:.2f}</b> · Lot: <b>{lot_size}</b></div></div>", unsafe_allow_html=True)

if sig["type"] in ["SELL", "BUY"]:
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Entry</div><div class='metric-mini-val'>{sig['entry']:.{dec}f}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Stop Loss (-R{sig['risk_zar']:.0f})</div><div class='metric-mini-val' style='color:#FF5722;'>{sig['sl']:.{dec}f}</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Breakeven</div><div class='metric-mini-val' style='color:#38BDF8;'>{sig['be']:.{dec}f}</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Take Profit (+R{sig['reward_zar']:.0f})</div><div class='metric-mini-val' style='color:#39FF14;'>{sig['tp']:.{dec}f}</div></div>", unsafe_allow_html=True)

bias_badge = "<span class='badge-bearish'>Bearish ↘</span>" if sig["it_bear"] else "<span class='badge-bullish'>Bullish ↗</span>"
ai_text = f"{selected_pair} remains under 1H selling pressure below its 20 & 50 EMAs (RSI {sig['rsi']:.1f}). Sell pullbacks into EMA9/EMA20 during active sessions." if sig["it_bear"] else f"{selected_pair} holds bullish 1H momentum above its moving averages (RSI {sig['rsi']:.1f}). Look for pullback entries on closed {selected_tf} candles."
st.markdown(f"<div class='xm-card'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'><span style='font-weight:800;font-size:0.98rem;'>👽 MARS AI Overview</span>{bias_badge}</div><div style='font-size:0.88rem;color:#CBD5E1;line-height:1.45;'>{ai_text}</div></div>", unsafe_allow_html=True)

ema_score = 50 + np.clip(((sig["close"] - sig["ema20"]) / max(sig["atr"], 1e-6)) * 12, -25, 25)
buy_pct = int(round((ema_score * 0.5) + (np.clip(sig["rsi"], 15, 85) * 0.5)))
sell_pct = 100 - buy_pct
st.markdown(f"<div class='xm-card'><div style='font-weight:800;font-size:1.0rem;'>Market Sentiment</div><div style='display:flex;justify-content:space-between;font-size:0.86rem;font-weight:700;margin-top:6px;'><span style='color:#39FF14;'>{buy_pct}% Buy</span><span style='color:#FF5722;'>Sell {sell_pct}%</span></div><div class='sentiment-bar-container'><div class='sentiment-bar-buy' style='width:{buy_pct}%;'></div></div></div>", unsafe_allow_html=True)

st.markdown(f"<div class='xm-card'><div style='font-weight:800;font-size:1.0rem;margin-bottom:4px;'>Daily Price Change</div><div class='{change_class}' style='font-size:0.9rem;'>{arrow} {day_pct:+.2f}%</div><div class='range-track'><div class='range-fill' style='width:{range_pos}%;'></div><div class='range-dot' style='left:{range_pos}%;'></div></div><div style='display:flex;justify-content:space-between;font-size:0.82rem;color:#94A3B8;'><span><b>{day_low:.{dec}f}</b> Low</span><span>High <b>{day_high:.{dec}f}</b></span></div></div>", unsafe_allow_html=True)

st_lbl = "<span style='color:#FF5722;'>Bearish</span>" if sig["st_bear"] else "<span style='color:#39FF14;'>Bullish</span>"
it_lbl = "<span style='color:#FF5722;'>Bearish</span>" if sig["it_bear"] else "<span style='color:#39FF14;'>Bullish</span>"
lt_lbl = "<span style='color:#FF5722;'>Bearish</span>" if sig["lt_bear"] else "<span style='color:#39FF14;'>Bullish</span>"
st_bar = "<div style='width:55%;height:100%;background:#FF5722;'></div>" if sig["st_bear"] else "<div style='width:55%;height:100%;background:#39FF14;margin-left:45%;'></div>"
it_bar = "<div style='width:55%;height:100%;background:#FF5722;'></div>" if sig["it_bear"] else "<div style='width:55%;height:100%;background:#39FF14;margin-left:45%;'></div>"
lt_bar = "<div style='width:55%;height:100%;background:#FF5722;'></div>" if sig["lt_bear"] else "<div style='width:55%;height:100%;background:#39FF14;margin-left:45%;'></div>"
st.markdown(f"<div class='xm-card'><div style='font-weight:800;font-size:1.0rem;margin-bottom:6px;'>Technical Score</div><div class='tech-row'><span style='color:#CBD5E1;'>Short-Term</span><span>{st_lbl}<span class='tech-pill-bg'>{st_bar}</span></span></div><div class='tech-row'><span style='color:#CBD5E1;'>Intermediate</span><span>{it_lbl}<span class='tech-pill-bg'>{it_bar}</span></span></div><div class='tech-row' style='border-bottom:none;'><span style='color:#CBD5E1;'>Long-Term</span><span>{lt_lbl}<span class='tech-pill-bg'>{lt_bar}</span></span></div><div style='display:flex;justify-content:space-between;margin-top:12px;padding-top:10px;border-top:1px solid #1E2533;font-size:0.88rem;'><span><span style='color:#8B98B0;'>Support</span> &nbsp;<b>{support_lvl:.{dec}f}</b></span><span><span style='color:#8B98B0;'>Resistance</span> &nbsp;<b>{resist_lvl:.{dec}f}</b></span></div></div>", unsafe_allow_html=True)
