import streamlit as st
from design import XM_THEME_CSS
from journal import render_journal_page

st.set_page_config(page_title="Trading Journal 📓", page_icon="📓", layout="wide")
st.markdown(XM_THEME_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 👽 Account Recon Settings")
    actual_xm_bal = st.number_input("Actual XM Live Balance (ZAR)", value=430.00, step=10.0)
    daily_floor = st.number_input("Hard Daily Floor (ZAR)", value=400.00, step=10.0)
    target_goal = st.number_input("Target Balance Goal (ZAR)", value=1000.00, step=50.0)

render_journal_page(actual_xm_bal, daily_floor, target_goal)
