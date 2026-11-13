import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

def init_journal_state(default_start_bal=699.98):
    if "journal_entries" not in st.session_state:
        sast = pytz.timezone("Africa/Johannesburg")
        today_str = datetime.now(sast).strftime("%Y-%m-%d")
        st.session_state.journal_entries = [
            {
                "Date": today_str,
                "Time (SAST)": "08:15",
                "Session": "Pre-London",
                "Pair": "GOLD (XAU/USD)",
                "Direction": "SELL",
                "Lots": 0.01,
                "Entry": 3898.02,
                "Exit": 3910.09,
                "Net P&L (ZAR)": -202.38,
                "Rule Followed": "No (Pre-Open)",
                "Notes": "Entered before 10:15 SAST liquidity; wide spread."
            },
            {
                "Date": today_str,
                "Time (SAST)": "10:10",
                "Session": "London (10:15)",
                "Pair": "GOLD (XAU/USD)",
                "Direction": "SELL",
                "Lots": 0.01,
                "Entry": 3894.94,
                "Exit": 3898.41,
                "Net P&L (ZAR)": -67.60,
                "Rule Followed": "Yes",
                "Notes": "SL hit on 10:12 stop-hunt spike; respected R400 floor."
            }
        ]
    if "starting_capital" not in st.session_state:
        st.session_state.starting_capital = float(default_start_bal)

def render_journal_page(live_xm_balance, daily_floor, target_goal=1000.00):
    init_journal_state()

    st.markdown("<div class='ticker-title'>📓 MARS_BOT PRO · Trading Journal & Recon</div>", unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.journal_entries)
    total_pnl = float(df["Net P&L (ZAR)"].sum()) if not df.empty else 0.0
    start_cap = st.number_input("Initial Live Deposit / Starting Capital (ZAR)", value=st.session_state.starting_capital, step=10.0)
    st.session_state.starting_capital = start_cap

    expected_bal = start_cap + total_pnl
    recon_diff = live_xm_balance - expected_bal
    to_goal = max(target_goal - live_xm_balance, 0.0)

    wins = len(df[df["Net P&L (ZAR)"] > 0]) if not df.empty else 0
    total_trades = len(df)
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0

    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Expected Balance</div><div class='metric-mini-val'>R{expected_bal:.2f}</div></div>", unsafe_allow_html=True)
    r2.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Actual XM Balance</div><div class='metric-mini-val' style='color:#39FF14;'>R{live_xm_balance:.2f}</div></div>", unsafe_allow_html=True)

    recon_color = "#39FF14" if abs(recon_diff) < 0.05 else "#FF5722"
    recon_status = "MATCHED ✅" if abs(recon_diff) < 0.05 else f"DIFF R{recon_diff:+.2f}"
    r3.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Recon Status</div><div class='metric-mini-val' style='color:{recon_color};'>{recon_status}</div></div>", unsafe_allow_html=True)

    pnl_color = "#39FF14" if total_pnl >= 0 else "#FF5722"
    r4.markdown(f"<div class='metric-mini'><div class='metric-mini-label'>Net P&L ({win_rate:.0f}% WR)</div><div class='metric-mini-val' style='color:{pnl_color};'>R{total_pnl:+.2f}</div></div>", unsafe_allow_html=True)

    floor_buffer = live_xm_balance - daily_floor
    st.markdown(
        f"<div class='xm-card' style='padding:12px 16px;'>"
        f"<div style='display:flex;justify-content:space-between;font-size:0.86rem;'>"
        f"<span>🛡️ Buffer Above R{daily_floor:.0f} Floor: <b style='color:#39FF14;'>R{floor_buffer:.2f}</b></span>"
        f"<span>🎯 Remaining to R{target_goal:.0f} Goal: <b style='color:#FF8A65;'>R{to_goal:.2f}</b></span>"
        f"</div></div>",
        unsafe_allow_html=True
    )

    with st.expander("➕ Log New Manual Trade", expanded=True):
        with st.form("manual_trade_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            sast = pytz.timezone("Africa/Johannesburg")
            now_sast = datetime.now(sast)

            t_date = c1.text_input("Date", value=now_sast.strftime("%Y-%m-%d"))
            t_time = c2.text_input("Time (SAST)", value=now_sast.strftime("%H:%M"))
            t_session = c3.selectbox("Session", ["London (10:15)", "New York (15:40)", "Pre-London", "Off-Peak"])

            c4, c5, c6 = st.columns(3)
            t_pair = c4.selectbox("Instrument", ["GOLD (XAU/USD)", "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF", "NZD/USD"])
            t_dir = c5.selectbox("Direction", ["SELL", "BUY"])
            t_lots = c6.number_input("Lot Size", value=0.01, step=0.01, format="%.2f")

            c7, c8, c9 = st.columns(3)
            t_entry = c7.number_input("Entry Price", value=0.00, step=0.01, format="%.5f")
            t_exit = c8.number_input("Exit Price", value=0.00, step=0.01, format="%.5f")
            t_pnl = c9.number_input("Net P&L (ZAR)", value=0.00, step=1.00, format="%.2f")

            c10, c11 = st.columns(2)
            t_rule = c10.selectbox("Followed All Rules?", ["Yes", "No (Early/Late)", "No (Oversized)"])
            t_notes = c11.text_input("Lesson / Execution Note", placeholder="e.g., Waited for 15m close, moved SL to BE...")

            submitted = st.form_submit_button("✅ Save Trade to Journal", use_container_width=True)
            if submitted:
                st.session_state.journal_entries.append({
                    "Date": t_date,
                    "Time (SAST)": t_time,
                    "Session": t_session,
                    "Pair": t_pair,
                    "Direction": t_dir,
                    "Lots": t_lots,
                    "Entry": t_entry,
                    "Exit": t_exit,
                    "Net P&L (ZAR)": float(t_pnl),
                    "Rule Followed": t_rule,
                    "Notes": t_notes
                })
                st.rerun()

    if not df.empty:
        df["Running Balance (ZAR)"] = start_cap + df["Net P&L (ZAR)"].cumsum()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(df) + 1)),
            y=df["Running Balance (ZAR)"],
            mode="lines+markers",
            line=dict(color="#39FF14", width=2.5),
            marker=dict(size=8, color="#FF5722", line=dict(width=1.5, color="#FFFFFF")),
            name="Balance"
        ))
        fig.add_hline(y=daily_floor, line_dash="dash", line_color="#FF5722", annotation_text=f"Floor R{daily_floor:.0f}")
        fig.update_layout(
            height=220,
            margin=dict(l=10, r=15, t=15, b=10),
            paper_bgcolor="#0B0E14",
            plot_bgcolor="#0B0E14",
            xaxis=dict(title="Trade #", gridcolor="#181E2B", color="#8B98B0", dtick=1),
            yaxis=dict(title="ZAR", gridcolor="#181E2B", color="#8B98B0")
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("#### 📋 Trade Ledger (Editable)")
        edited_df = st.data_editor(
            df.drop(columns=["Running Balance (ZAR)"]),
            num_rows="dynamic",
            use_container_width=True,
            key="journal_editor"
        )
        if st.button("💾 Apply Table Edits"):
            st.session_state.journal_entries = edited_df.to_dict("records")
            st.rerun()

        b1, b2 = st.columns(2)
        csv_data = df.to_csv(index=False).encode("utf-8")
        b1.download_button(
            "⬇️ Download CSV Backup",
            data=csv_data,
            file_name=f"mars_journal_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        uploaded_csv = b2.file_uploader("⬆️ Restore CSV Backup", type=["csv"], label_visibility="collapsed")
        if uploaded_csv is not None:
            restored = pd.read_csv(uploaded_csv)
            if "Running Balance (ZAR)" in restored.columns:
                restored = restored.drop(columns=["Running Balance (ZAR)"])
            st.session_state.journal_entries = restored.to_dict("records")
            st.success("Journal restored!")
            st.rerun()
