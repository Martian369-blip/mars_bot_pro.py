XM_THEME_CSS = """
<style>
    .stApp {
        background-color: #111622;
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
    .price-up { color: #19B36B; font-weight: 700; font-size: 0.95rem; }
    .price-down { color: #E03E52; font-weight: 700; font-size: 0.95rem; }

    .quote-grid {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 10px;
        align-items: center;
        margin: 12px 0 16px 0;
    }
    .sell-box {
        background: linear-gradient(135deg, #D93848, #B82837);
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
        color: white;
    }
    .buy-box {
        background: linear-gradient(135deg, #1E9E63, #15804E);
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
        color: white;
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
    .quote-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 1px; opacity: 0.9; }
    .quote-val { font-size: 1.25rem; font-weight: 800; margin-top: 2px; }

    .signal-card-sell {
        background-color: #191F2E;
        border: 1.5px solid #E03E52;
        border-left: 6px solid #E03E52;
        border-radius: 12px;
        padding: 15px 18px;
        margin-bottom: 14px;
    }
    .signal-card-buy {
        background-color: #191F2E;
        border: 1.5px solid #19B36B;
        border-left: 6px solid #19B36B;
        border-radius: 12px;
        padding: 15px 18px;
        margin-bottom: 14px;
    }
    .signal-card-wait {
        background-color: #191F2E;
        border: 1.5px solid #F59E0B;
        border-left: 6px solid #F59E0B;
        border-radius: 12px;
        padding: 15px 18px;
        margin-bottom: 14px;
    }

    .xm-card {
        background-color: #181E2C;
        border: 1px solid #2A344A;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
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

    .sentiment-bar-container {
        width: 100%;
        height: 8px;
        background-color: #E03E52;
        border-radius: 4px;
        overflow: hidden;
        margin: 8px 0 4px 0;
    }
    .sentiment-bar-buy { height: 100%; background-color: #19B36B; }

    .range-track {
        position: relative;
        width: 100%;
        height: 6px;
        background-color: #2A344A;
        border-radius: 4px;
        margin: 12px 0 8px 0;
    }
    .range-fill { height: 100%; background-color: #19B36B; border-radius: 4px; }
    .range-dot {
        position: absolute;
        top: -4px;
        width: 14px;
        height: 14px;
        background-color: #FFFFFF;
        border-radius: 50%;
        transform: translateX(-50%);
    }

    .tech-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #242E42;
        font-size: 0.9rem;
    }
    .tech-pill-bg {
        width: 65px;
        height: 8px;
        background-color: #242E42;
        border-radius: 4px;
        overflow: hidden;
        display: inline-block;
        margin-left: 10px;
    }

    .metric-mini {
        background-color: #141926;
        border: 1px solid #263045;
        border-radius: 8px;
        padding: 10px 12px;
        text-align: center;
        margin-bottom: 8px;
    }
    .metric-mini-label { font-size: 0.72rem; color: #8B98B0; text-transform: uppercase; }
    .metric-mini-val { font-size: 1.05rem; font-weight: 800; color: #FFFFFF; margin-top: 2px; }
</style>
"""
