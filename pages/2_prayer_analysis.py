import streamlit as st
import pandas as pd

st.title("Prayer Analysis")

# ============================================================
# LOAD DATA
# ============================================================

if "df" not in st.session_state:
    st.warning("Please upload dataset first.")
    st.stop()

if "list_df" not in st.session_state:
    st.warning("LIST sheet not loaded.")
    st.stop()

df = st.session_state["df"].copy()
list_df = st.session_state["list_df"].copy()

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
list_df = clean(list_df)

# ============================================================
# VALIDATION
# ============================================================

required_breakdown = [
    "id", "idp", "ayat", "phrase",
    "stylistics", "function", "domain", "keyword"
]

required_list = [
    "id", "text", "ayat", "speaker",
    "prayer_status", "prayer_type", "tradition"
]

for col in required_breakdown:
    if col not in df.columns:
        st.error(f"Missing Breakdown column: {col}")
        st.stop()

for col in required_list:
    if col not in list_df.columns:
        st.error(f"Missing LIST column: {col}")
        st.stop()

# ============================================================
# MAP LIST → BREAKDOWN
# ============================================================

meta = list_df.drop_duplicates("id").set_index("id")

df["speaker"] = df["id"].map(meta["speaker"])
df["prayer_status"] = df["id"].map(meta["prayer_status"])
df["prayer_type"] = df["id"].map(meta["prayer_type"])
df["tradition"] = df["id"].map(meta["tradition"])
df["text"] = df["id"].map(meta["text"])

# ============================================================
# SELECT ID
# ============================================================

ids = sorted(df["id"].dropna().unique())

selected_id = st.selectbox("1. Select ID", ids)

subset = df[df["id"] == selected_id].copy()
subset_phrase = subset.drop_duplicates("idp")

# ============================================================
# RESULT
# ============================================================

st.header("2. Result")

# -------------------------
# TEXT
# -------------------------
st.subheader("a. Text")
st.write(subset["text"].dropna().iloc[0])

# -------------------------
# AYAT
# -------------------------
st.subheader("b. Ayat")
st.write(", ".join(subset["ayat"].dropna().astype(str).unique()))

# -------------------------
# SPEAKER
# -------------------------
st.subheader("c. Speaker")
st.write(", ".join(subset["speaker"].dropna().unique()))

# -------------------------
# STATUS + TYPE
# -------------------------
st.subheader("d. Prayer Status & Discourse")
st.write(
    f"{', '.join(subset['prayer_status'].dropna().unique())} | "
    f"{', '.join(subset['prayer_type'].dropna().unique())}"
)

# -------------------------
# STYLISTICS PATTERN
# -------------------------
st.subheader("e. Stylistics Pattern")
st.write(" → ".join(subset_phrase["stylistics"].dropna()))

# -------------------------
# FUNCTION PATTERN
# -------------------------
st.subheader("f. Function Pattern")
st.write(" → ".join(subset_phrase["function"].dropna()))

# -------------------------
# PHRASE MATRIX
# -------------------------
st.subheader("g. Phrase-Level Analysis")

matrix = subset_phrase[[
    "idp", "phrase", "stylistics", "function", "domain"
]].sort_values("idp")

st.dataframe(matrix, use_container_width=True)

# -------------------------
# DOMINANT DOMAIN
# -------------------------
st.subheader("h. Dominant Domain")

if not subset_phrase["domain"].dropna().empty:
    st.write(subset_phrase["domain"].value_counts().idxmax())
else:
    st.write("-")

# -------------------------
# KEYWORD DISTRIBUTION
# -------------------------
st.subheader("i. Keyword Distribution")

kw = subset["keyword"].dropna()
kw = kw[kw != ""]

if not kw.empty:
    st.bar_chart(kw.value_counts().head(15))
else:
    st.write("-")

# ============================================================
# SEMANTIC GRAPH
# ============================================================

st.subheader("j. Semantic Graph")

try:
    from pyvis.network import Network
    import tempfile, os

    net = Network(height="600px", width="100%")

    id_node = f"ID::{selected_id}"
    net.add_node(id_node, label=str(selected_id), size=25)

    added_nodes = set([id_node])

    def add_node_safe(node_id, label, size=10):
        if node_id not in added_nodes:
            net.add_node(node_id, label=label, size=size)
            added_nodes.add(node_id)

    for _, row in subset.iterrows():

        sty = str(row["stylistics"]).strip() if pd.notna(row["stylistics"]) else ""
        fun = str(row["function"]).strip() if pd.notna(row["function"]) else ""
        kw = str(row["keyword"]).strip() if pd.notna(row["keyword"]) else ""

        if sty:
            sty_node = f"STY::{sty}"
            add_node_safe(sty_node, sty, 15)
            net.add_edge(id_node, sty_node)

        if fun:
            fun_node = f"FUN::{fun}"
            add_node_safe(fun_node, fun, 12)
            net.add_edge(sty_node if sty else id_node, fun_node)

        if kw:
            kw_node = f"KW::{kw}"
            add_node_safe(kw_node, kw, 6)
            net.add_edge(fun_node if fun else id_node, kw_node)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        path = tmp.name

    net.write_html(path)

    with open(path, "r", encoding="utf-8") as f:
        st.components.v1.html(f.read(), height=620)

    os.remove(path)

except Exception as e:
    st.warning(f"Graph error: {e}")

# ============================================================
# NOTES (AUTO COMMENTARY)
# ============================================================

st.subheader("k. Notes")

speaker = subset["speaker"].dropna().unique()
status = subset["prayer_status"].dropna().unique()
ptype = subset["prayer_type"].dropna().unique()
trad = subset["tradition"].dropna().unique()

commentary = []

if len(speaker) > 0:
    commentary.append(f"This prayer is attributed to {', '.join(speaker)}.")

if len(status) > 0:
    commentary.append(f"It is classified as {', '.join(status)}.")

if len(ptype) > 0:
    commentary.append(f"The discourse mode is {', '.join(ptype)}.")

if len(trad) > 0:
    commentary.append(f"This prayer also appears in {', '.join(trad)}.")

if commentary:
    st.write(" ".join(commentary))
else:
    st.write("-")