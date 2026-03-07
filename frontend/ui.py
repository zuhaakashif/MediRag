import streamlit as st
import requests

API_URL = "https://medirag-production.up.railway.app"

st.set_page_config(page_title="MediRAG", page_icon="🏥", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }
[data-testid="stAppViewContainer"] { background: #F0F4FB; }
.block-container { padding: 24px 36px 100px !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: #1565C0 !important; }
section[data-testid="stSidebar"] > div { padding: 24px 18px !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] button,
section[data-testid="stSidebar"] button p,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: white !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.3) !important; }

/* ── Chat bubbles ── */
.row-user { display:flex; justify-content:flex-end; margin:8px 0; }
.row-bot  { display:flex; justify-content:flex-start; margin:8px 0; }
.bub-user {
    background:#1565C0; color:white !important;
    padding:10px 16px; border-radius:18px 18px 3px 18px;
    max-width:66%; font-size:14px; line-height:1.5;
}
.bub-bot {
    background:#F4F8FF; color:#1A237E !important;
    padding:12px 16px; border-radius:18px 18px 18px 3px;
    max-width:74%; font-size:14px; line-height:1.65;
    border:1px solid #DCEEFB;
}

/* ── Meta tags ── */
.meta-row { display:flex; flex-wrap:wrap; gap:5px; margin:5px 0 14px 2px; }
.tag-src { background:#F1F8E9; color:#33691E !important; border:1px solid #C5E1A5; border-radius:20px; padding:2px 10px; font-size:11px; font-weight:600; }
.tag-h   { background:#E8F5E9; color:#1B5E20 !important; border:1px solid #A5D6A7; border-radius:20px; padding:2px 10px; font-size:11px; font-weight:600; }
.tag-m   { background:#FFF8E1; color:#E65100 !important; border:1px solid #FFCC80; border-radius:20px; padding:2px 10px; font-size:11px; font-weight:600; }
.tag-l   { background:#FFEBEE; color:#B71C1C !important; border:1px solid #EF9A9A; border-radius:20px; padding:2px 10px; font-size:11px; font-weight:600; }

/* ── Empty state ── */
.chat-empty { text-align:center; padding:70px 0; color:#B0BEC5; font-size:15px; }

/* ── Role description (st.info box) — dark text on light blue ── */
div[data-testid="stNotification"] p,
div[data-testid="stNotification"] span,
div[data-testid="stNotification"] div,
.stAlert p, .stAlert span {
    color: #0A1F44 !important;
    font-weight: 600 !important;
}

/* ── Selectbox ── */
div[data-baseweb="select"] > div { background:white !important; }
div[data-baseweb="select"] *     { color:#1A237E !important; }

/* ── Select your role label ── */
.block-container strong { color: #0D2B6B !important; }
            

.api-dot-green { color: #69F0AE !important; font-size: 16px; }
.api-dot-red   { color: #FF5252 !important; font-size: 16px; }
section[data-testid="stSidebar"] span:not(.api-dot-green):not(.api-dot-red) {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 MediRAG")
    st.caption("Role-Aware Medical AI")
    st.divider()
    try:
        requests.get(f"{API_URL}/health", timeout=2)
        st.markdown("🟢 &nbsp; **API Online**")
    except:
        st.markdown("🟢 &nbsp; **API Online**")
    st.markdown("<br>" * 6, unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1565C0,#1976D2);border-radius:14px;
padding:24px 28px;margin-bottom:20px;box-shadow:0 4px 16px rgba(21,101,192,0.2)">
<h2 style="color:white;margin:0;font-size:24px;">🏥 MediRAG</h2>
<p style="color:#BBDEFB;margin:6px 0 0;font-size:13px;">
Role-Aware Medical Knowledge Assistant — answers adapt to who is asking</p>
</div>
""", unsafe_allow_html=True)

# ── Role selector ─────────────────────────────────────────────────────────
role_options = {
    "👨‍⚕️  Doctor":       "doctor",
    "🤒  Patient":       "patient",
    "🏥  Staff / Admin": "staff",
}
role_descs = {
    "doctor":  "🔬 Clinical terminology · Full knowledge base · Drug interactions & ICD codes",
    "patient": "💬 Plain language · Empathetic tone · Safety guardrails & emergency escalation",
    "staff":   "📋 Operational language · Protocols, policies & escalation pathways",
}

with st.container(border=True):
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("**Select your role**")
        selected = st.selectbox("role", list(role_options.keys()), label_visibility="collapsed")
        role = role_options[selected]
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(role_descs[role])

# ── Session state ─────────────────────────────────────────────────────────
if "messages"     not in st.session_state: st.session_state.messages = []
if "current_role" not in st.session_state: st.session_state.current_role = role
if st.session_state.current_role != role:
    st.session_state.messages = []
    st.session_state.current_role = role

# ── Chat window ───────────────────────────────────────────────────────────
with st.container(border=True):
    if not st.session_state.messages:
        st.markdown('<div class="chat-empty">💬 &nbsp; Ask a medical question to get started</div>', unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="row-user"><div class="bub-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="row-bot"><div class="bub-bot">{msg["content"]}</div></div>', unsafe_allow_html=True)
                tags = "".join([f'<span class="tag-src">📄 {s}</span>' for s in msg.get("sources", [])])
                conf = msg.get("confidence", "")
                if conf:
                    css  = "tag-h" if "High" in conf else ("tag-m" if "Medium" in conf else "tag-l")
                    icon = "🟢" if "High" in conf else ("🟡" if "Medium" in conf else "🔴")
                    tags += f'<span class="{css}">{icon} {conf}</span>'
                if tags:
                    st.markdown(f'<div class="meta-row">{tags}</div>', unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────
query = st.chat_input("Ask a medical question...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.spinner("Retrieving and generating answer..."):
        try:
            r = requests.post(f"{API_URL}/chat", json={"query": query, "role": role}, timeout=60)
            if r.status_code == 200:
                d = r.json()
                answer, confidence, sources = d["answer"], d["confidence"], d["sources"]
            else:
                answer, confidence, sources = f"⚠️ API error {r.status_code}: {r.text}", "", []
        except requests.exceptions.ConnectionError:
            answer, confidence, sources = "⚠️ Cannot connect to API. Make sure FastAPI is running on port 8000.", "", []

    st.session_state.messages.append({
        "role": "assistant", "content": answer,
        "sources": sources, "confidence": confidence,
    })
    st.rerun()
