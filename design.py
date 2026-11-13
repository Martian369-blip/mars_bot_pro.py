XM_THEME_CSS = """
<style>
    .stApp {
        background-color: #0B0E14;
        color: #E6EDF3;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .block-container {
        padding-top: 1.1rem;
        padding-bottom: 2rem;
        max-width: 1050px;
    }
    .ticker-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 6px;
    }
    .price-up { color: #39FF14; font-weight: 700; font-size: 0.95rem; }
    .price-down { color: #FF5722; font-weight: 700; font-size: 0.95rem; }

    .quote-grid {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 10px;
        align-items: center;
        margin: 12px 0 16px 0;
    }
    .sell-box {
        background: linear-gradient(135deg, #FF5722, #D84315);
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
        color: #FFFFFF;
        box-shadow: 0 4px 14px rgba(255, 87, 34, 0.30);
    }
    .buy-box {
        background: linear-gradient(135deg, #2ECC40, #1FAA2E);
        border: 1px solid #39FF14;
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
        color: #081208;
        box-shadow: 0 4px 14px rgba(57, 255, 20, 0.25);
    }
    .spread-pill {
        background-color: #141923;
        border: 1px solid #FF5722;
        color: #39FF14;
        font-weight: 800;
        font-size: 0.85rem;
        padding: 6px 12px;
        border-radius: 6px;
        text-align: center;
    }
    .quote-label { font-size: 0.72rem; font-weight: 800; letter-spacing: 1px; opacity: 0.92; }
    .quote-val { font-size: 1.25rem; font-weight: 900; margin-top: 2px; }

    .signal-card-sell {
        background-color: #141821;
        border: 1.5px solid #FF5722;
        border-left: 6px solid #FF5722;
        border-radius: 12px;
        padding: 15px 18px;
        margin-bottom: 14px;
    }
    .signal-card-buy {
        background-color: #141821;
        border: 1.5px solid #39FF14;
        border-left: 6px solid #39FF14;
        border-radius: 12px;
        padding: 15px 18px;
        margin-bottom: 14px;
    }
    .signal-card-wait {
        background-color: #141821;
        border: 1.5px solid #FF8A65;
        border-left: 6px solid #FF8A65;
        border-radius: 12px;
        padding: 15px 18px;
        margin-bottom: 14px;
    }

    .xm-card {
        background-color: #12161F;
        border: 1px solid #232B3A;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }
    .badge-bearish {
        background-color: rgba(255, 87, 34, 0.18);
        color: #FF7043;
        border: 1px solid rgba(255, 87, 34, 0.4);
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .badge-bullish {
        background-color: rgba(57, 255, 20, 0.14);
        color: #39FF14;
        border: 1px solid rgba(57, 255, 20, 0.4);
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .sentiment-bar-container {
        width: 100%;
        height: 8px;
        background-color: #FF5722;
        border-radius: 4px;
        overflow: hidden;
        margin: 8px 0 4px 0;
    }
    .sentiment-bar-buy { height: 100%; background-color: #39FF14; }

    .range-track {
        position: relative;
        width: 100%;
        height: 6px;
        background-color: #232B3A;
        border-radius: 4px;
        margin: 12px 0 8px 0;
    }
    .range-fill { height: 100%; background-color: #39FF14; border-radius: 4px; }
    .range-dot {
        position: absolute;
        top: -4px;
        width: 14px;
        height: 14px;
        background-color: #FF5722;
        border: 2px solid #FFFFFF;
        border-radius: 50%;
        transform: translateX(-50%);
    }

    .tech-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #1E2533;
        font-size: 0.9rem;
    }
    .tech-pill-bg {
        width: 65px;
        height: 8px;
        background-color: #1E2533;
        border-radius: 4px;
        overflow: hidden;
        display: inline-block;
        margin-left: 10px;
    }

    .metric-mini {
        background-color: #0E121A;
        border: 1px solid #232B3A;
        border-radius: 8px;
        padding: 10px 12px;
        text-align: center;
        margin-bottom: 8px;
    }
    .metric-mini-label { font-size: 0.72rem; color: #8B98B0; text-transform: uppercase; }
    .metric-mini-val { font-size: 1.05rem; font-weight: 800; color: #FFFFFF; margin-top: 2px; }
</style>
"""
