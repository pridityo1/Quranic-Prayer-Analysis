import streamlit as st
import pandas as pd

st.title("Corpus Statistics")

# ============================================================
# LOAD DATA
# ============================================================

if "df" not in st.session_state:
    st.warning("Please upload dataset first.")
    st.stop()

df = st.session_state["df"].copy()
list_df = st.session_state.get("list_df")

# ============================================================
# CLEAN
# ============================================================

def clean(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    df = df.loc[:, ~df.columns.str.contains("^unnamed")]
    return df

df = clean(df)

if list_df is not None:
    list_df = clean(list_df)

# ============================================================
# VALIDATION
# ============================================================

required_breakdown = [
    "id", "idp", "stylistics", "function", "domain", "keyword"
]

for col in required_breakdown:
    if col not in df.columns:
        st.error(f"Missing Breakdown column: {col}")
        st.stop()

# ============================================================
# DATA VIEWS
# ============================================================

df_phrase = df.drop_duplicates(subset=["idp"])
df_keyword = df.copy()

df_keyword["keyword"] = df_keyword["keyword"].astype(str).str.strip()

# ============================================================
# 1. PRAYER CLASSIFICATION (LIST)
# ============================================================

st.header("1. Prayer Classification")

if list_df is None:
    st.info("LIST sheet not available.")
else:

    required_list = [
        "id", "anchor", "speaker", "prayer_status", "prayer_type"
    ]

    for col in required_list:
        if col not in list_df.columns:
            st.error(f"Missing LIST column: {col}")
            st.stop()

    # -------------------------
    # 1.1 Anchor
    # -------------------------
    st.subheader("1.1 Classification by Anchor")

    anchor_counts = list_df["anchor"].value_counts()
    st.bar_chart(anchor_counts)

    # -------------------------
    # 1.2 Status
    # -------------------------
    st.subheader("1.2 Classification by Status")

    status_counts = list_df["prayer_status"].value_counts()
    st.bar_chart(status_counts)

    # -------------------------
    # 1.3 Speaker
    # -------------------------
    st.subheader("1.3 Classification by Speaker")

    speaker_counts = list_df["speaker"].value_counts()
    st.bar_chart(speaker_counts)

# ============================================================
# 2. PHRASE STRUCTURE (BREAKDOWN)
# ============================================================

st.header("2. Phrase Structure")

# -------------------------
# 2.1 Stylistics
# -------------------------
st.subheader("2.1 Stylistics")

sty_counts = df_phrase["stylistics"].value_counts()
st.bar_chart(sty_counts)

# -------------------------
# 2.2 Function
# -------------------------
st.subheader("2.2 Function")

fun_counts = df_phrase["function"].value_counts()
st.bar_chart(fun_counts)

# -------------------------
# 2.3 Domain
# -------------------------
st.subheader("2.3 Domain")

dom_counts = df_phrase["domain"].value_counts()
st.bar_chart(dom_counts)

# ============================================================
# 3. KEYWORD DISTRIBUTION
# ============================================================

st.header("3. Keyword Distribution")

# Optional: exclude anchor-type keywords
if "key_type" in df_keyword.columns:
    df_kw = df_keyword[df_keyword["key_type"] != "anchor"]
else:
    df_kw = df_keyword

top_keywords = df_kw["keyword"].value_counts().head(20)

st.bar_chart(top_keywords)