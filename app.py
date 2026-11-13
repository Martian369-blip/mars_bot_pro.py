import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import pytz

# ---------------------------------------------------------
# 1. PAGE CONFIG & XM DARK INSTITUTIONAL STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="MARS_BOT PRO | Institutional Terminal",
    page_icon="👽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Main Dark Background matching XM Markets UI */
    .stApp {
        background-color: #111622;
        color: #E6EDF3;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }
    /* Top Header Ticker Styling */
    .ticker-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: 0.5px;
    }
    .price-up { color: #19B36B; font-weight: 700; font-size: 0.95rem; }
    .price-down { color: #E03E52; font-weight: 700; font-size: 0.95rem; }

    /* SELL | SPREAD | BUY Action Bar */
    .quote-grid {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 10px;
        align-items: center;
        margin: 12px 0 18px 0;
    }
    .sell-box {
        background: linear-gradient(135deg, #D93848, #B82837);
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 12px rgba(217, 56, 72, 0.25);
    }
    .buy-box {
        background: linear-gradient(135deg, #1E9E63, #15804E);
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 12px rgba(30, 158, 99, 0.25);
    }
    .spread-pill {
        background-color: #FFFFFF;
        color: #111622;
        font-weight: 800;
        font-size: 0.85rem;
        padding: 6px 12px;
        border-radius: 6px;
        text-align: center;
    }
    .quote-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1px;
        opacity: 0.9;
    }
    .quote-val {
        font-size: 1.25rem;
        font-weight: 800;
        margin-top: 2px;
    }

    /* Precision Signal Card (Directly Underneath Spread) */
    .signal-card-sell {
        background-color: #191F2E;
        border: 1.5px solid #E03E52;
        border-left: 6px solid #E03E52;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    .signal-card-buy {
        background-color: #191F2E;
        border: 1.5px solid #19B36B;
        border-left: 6px solid #19B36B;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    .signal-card-wait {
        background-color: #191F2E;
        border: 1.5px solid #F59E0B;
        border-left: 6px solid #F59E0B;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }

    /* AI Overview Card */
    .ai-card {
        background-color: #181E2C;
        border: 1px solid #2A344A;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 16px;
    }
    .ai-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .badge-bearish {
        background-color: rgba(224, 62, 82, 0.18);
        color: #FF5C70;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .badge-bullish {
        background-color: rgba(25, 179, 107, 0.18);
        color: #2EE58F;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .badge-neutral {
        background-color: rgba(245, 158, 11, 0.18);
        color: #FBBF24;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }

    /* Market Sentiment Bar */
    .sentiment-bar-container {
        width: 100%;
        height: 8px;
        background-color: #E03E52;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 6px;
        margin-bottom: 14px;
    }
    .sentiment-bar-buy {
        height: 100%;
        background-color: #19B36B;
    }

    /* Metric Boxes */
    .metric-mini {
        background-color: #141926;
        border: 1px solid #263045;
        border-radius: 8px;
        padding: 10px 12px;
        text-align: center;
    }
    .metric-mini-label {
        font-size: 0.72rem;
        color: #8B98B0;
        text-transform: uppercase;
    }
    .metric-mini-val {
        font-size: 1.05rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INSTRUMENT & BROKER SPECIFICATIONS (XM STANDARD ZAR)
# ---------------------------------------------------------
INSTRUMENTS = {
    "GOLD (XAU/USD)": {
        "ticker": "XAUUSD=X",
        "fallback": "GC=F",
        "spread": 0.55,
        "decimals": 2,
        "pip_size": 0.10,
        "usd_per_unit_001": 1.00,  # $1 move on 0.01 lot (1 oz) = $1.00
        "max_sl_points": 3.80,
        "usd_correlated": "INVERSE_USD"
    },
    "EUR/USD": {
        "ticker": "EURUSD=X",
        "fallback": "EURUSD=X",
        "spread": 0.00012,
        "decimals": 5,
        "pip_size": 0.0001,
        "usd_per_unit_001": 1000.0,  # 0.0001 move on 0.01 lot (1,000) = $0.10
        "max_sl_points": 0.0022,
        "usd_correlated": "INVERSE_USD"
    },
    "GBP/USD": {
        "ticker": "GBPUSD=X",
        "fallback": "GBPUSD=X",
        "spread": 0.00015,
        "decimals": 5,
        "pip_size": 0.0001,
        "usd_per_unit_001": 1000.0,
        "max_sl_points": 0.0025,
        "usd_correlated": "INVERSE_USD"
    },
    "USD/JPY": {
        "ticker": "USDJPY=X",
        "fallback": "USDJPY=X",
        "spread": 0.016,
        "decimals": 3,
        "pip_size": 0.01,
        "usd_per_unit_001": 6.26,
        "max_sl_points": 0.25,
        "usd_correlated": "DIRECT_USD"
    },
    "AUD/USD": {
        "ticker": "AUDUSD=X",
        "fallback": "AUDUSD=X",
        "spread": 0.00014,
        "decimals": 5,
        "pip_size": 0.0001,
        "usd_per_unit_001": 1000.0,
        "max_sl_points": 0.0020,
        "usd_correlated": "INVERSE_USD"
    },
    "USD/CAD": {
        "ticker": "USDCAD=X",
        "fallback": "USDCAD=X",
        "spread": 0.00018,
        "decimals": 5,
        "pip_size": 0.0001,
        "usd_per_unit_001": 720.0,
        "max_sl_points": 0.0022,
        "usd_correlated": "DIRECT_USD"
    },
    "USD/CHF": {
        "ticker": "USDCHF=X",
        "fallback": "USDCHF=X",
        "spread": 0.00016,
        "decimals": 5,
        "pip_size": 0.0001,
        "usd_per_unit_001": 1130.0,
        "max_sl_points": 0.0022,
        "usd_correlated": "DIRECT_USD"
    },
    "NZD/USD": {
        "ticker": "NZDUSD=X",
        "fallback": "NZDUSD=X",
        "spread": 0.00018,
        "decimals": 5,
        "pip_size": 0.0001,
        "usd_per_unit_001": 1000.0,
        "max_sl_points": 0.0020,
        "usd_correlated": "INVERSE_USD"
    }
}

TIMEFRAMES = {
    "15m": ("15m", "5d"),
    "1H": ("1h", "1mo"),
    "4H": ("1h", "3mo"),
    "1D": ("1d", "6mo")
}

# ---------------------------------------------------------
# 3. SIDEBAR: LIVE ACCOUNT & BROKER CALIBRATION
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
        "Broker Price Offset (+/-)",
        value=0.00,
        step=0.10,
        help="If XM quote differs slightly from feed, enter XM Price minus Feed Price here."
    )
    custom_spread = st.number_input(
        "Override Broker Spread (0 = auto)",
        value=0.00,
        step=0.01,
        format="%.5f"
    )
    enforce_session_gate = st.checkbox("Enforce London/NY Liquidity Gate (SAST)", value=True)

# ---------------------------------------------------------
# 4. DATA FETCHING & TECHNICAL ENGINE
# ---------------------------------------------------------
@st.cache_data(ttl=30)
def get_market_data(symbol_key, tf_label):
    spec = INSTRUMENTS[symbol_key]
    interval, period = TIMEFRAMES[tf_label]

    df = yf.download(spec["ticker"], interval=interval, period=period, progress=False)
    if df is None or df.empty or len(df) < 55:
        df = yf.download(spec["fallback"], interval=interval, period=period, progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.dropna().copy()

    # Fetch 1H data for higher-timeframe trend filter
    df_1h = yf.download(spec["ticker"], interval="1h", period="1mo", progress=False)
    if df_1h is None or df_1h.empty or len(df_1h) < 55:
        df_1h = yf.download(spec["fallback"], interval="1h", period="1mo", progress=False)
    if isinstance(df_1h.columns, pd.MultiIndex):
        df_1h.columns = df_1h.columns.get_level_values(0)
    df_1h = df_1h.dropna().copy()

    # Fetch USD/ZAR for exact Rand risk conversion
    zar_df = yf.download("ZAR=X", interval="1h", period="5d", progress=False)
    if isinstance(zar_df.columns, pd.MultiIndex):
        zar_df.columns = zar_df.columns.get_level_values(0)
    usdzar = float(zar_df["Close"].iloc[-1]) if not zar_df.empty else 16.76

    return df, df_1h, usdzar

