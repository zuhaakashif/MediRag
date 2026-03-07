"""
admin.py — Phase 4
Admin observability dashboard for MediRAG.
Run with: streamlit run dashboard/admin.py --server.port 8502
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from app.logger import load_logs

st.set_page_config(page_title="MediRAG Admin", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .metric-card { background:white; border-radius:12px; padding:20px; border:1px solid #e0e0e0; text-align:center; }
    .metric-number { font-size:42px; font-weight:700; color:#0D7377; }
    .metric-label  { font-size:14px; color:#666; margin-top:4px; }
    .gap-item { background:#fff8e1; border-left:4px solid #f57c00; padding:10px 14px; border-radius:0 8px 8px 0; margin:6px 0; font-size:14px; color:#333; }
    .conf-high   { color:#2e7d32; font-weight:600; }
    .conf-medium { color:#f57c00; font-weight:600; }
    .conf-low    { color:#c62828; font-weight:600; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 📊 MediRAG Admin Dashboard")
st.markdown("*Query logs, role analytics, and knowledge gap tracking*")
st.divider()

logs = load_logs()

if st.button("🔄 Refresh"):
    st.rerun()

if not logs:
    st.info("No queries logged yet. Start asking questions in the main chat UI first!")
    st.stop()

df = pd.DataFrame(logs)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["time_str"]  = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

total       = len(df)
role_counts = df["role"].value_counts()
low_conf    = df[df["confidence"].str.contains("Low", na=False)]
high_conf   = df[df["confidence"].str.contains("High", na=False)]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-number">{total}</div><div class="metric-label">Total Queries</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-number" style="color:#2e7d32">{len(high_conf)}</div><div class="metric-label">High Confidence</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-number" style="color:#c62828">{len(low_conf)}</div><div class="metric-label">Knowledge Gaps</div></div>', unsafe_allow_html=True)
with col4:
    most_active = role_counts.index[0].title() if len(role_counts) else "—"
    st.markdown(f'<div class="metric-card"><div class="metric-number" style="font-size:28px">{most_active}</div><div class="metric-label">Most Active Role</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns(2)
with col_left:
    st.markdown("#### Queries by Role")
    role_df = role_counts.reset_index()
    role_df.columns = ["Role", "Count"]
    st.bar_chart(role_df.set_index("Role"), color="#0D7377")

with col_right:
    st.markdown("#### Confidence Distribution")
    def conf_bucket(c):
        if "High"   in str(c): return "High"
        if "Medium" in str(c): return "Medium"
        return "Low"
    conf_df = df["confidence"].apply(conf_bucket).value_counts().reset_index()
    conf_df.columns = ["Confidence", "Count"]
    st.bar_chart(conf_df.set_index("Confidence"), color="#14A098")

st.divider()
st.markdown("#### 🔍 Knowledge Gap Tracker")
st.markdown("*Low confidence queries — these indicate missing content in your knowledge base.*")

if low_conf.empty:
    st.success("No knowledge gaps detected — all answers returned Medium or High confidence!")
else:
    for _, row in low_conf.iterrows():
        st.markdown(
            f'<div class="gap-item"><strong>[{row["role"].upper()}]</strong> {row["query"]}'
            f'<br><span style="color:#999;font-size:12px">{row["time_str"]}</span></div>',
            unsafe_allow_html=True
        )

st.divider()
st.markdown("#### 📋 Full Query Log")

role_filter = st.selectbox("Filter by role", ["All", "doctor", "patient", "staff"])
filtered_df = df if role_filter == "All" else df[df["role"] == role_filter]
filtered_df = filtered_df.sort_values("timestamp", ascending=False)

icons = {"doctor": "👨‍⚕️", "patient": "🤒", "staff": "🏥"}
for _, row in filtered_df.iterrows():
    icon = icons.get(row["role"], "❓")
    conf = str(row["confidence"])
    conf_class = "conf-high" if "High" in conf else ("conf-medium" if "Medium" in conf else "conf-low")
    label = f"{icon} [{row['role'].upper()}]  {row['query'][:80]}{'...' if len(row['query'])>80 else ''}  —  {row['time_str']}"
    with st.expander(label):
        st.markdown(f"**Query:** {row['query']}")
        st.markdown(f"**Role:** {row['role'].title()}")
        st.markdown(f'**Confidence:** <span class="{conf_class}">{conf}</span>', unsafe_allow_html=True)
        if row.get("sources"):
            st.markdown(f"**Sources:** {', '.join(row['sources'])}")
        st.markdown("**Answer:**")
        st.markdown(row["answer"])

st.divider()
st.markdown('<p style="text-align:center;color:#999;font-size:13px">MediRAG Admin Dashboard — Phase 4</p>', unsafe_allow_html=True)
