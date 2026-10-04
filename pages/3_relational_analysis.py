import streamlit as st
import pandas as pd


# ============================================================
# PAGE
# ============================================================

st.title("Relational Analysis")


# ============================================================
# LOAD DATA
# ============================================================

if "df" not in st.session_state:
    st.warning("Upload dataset first.")
    st.stop()

if "list_df" not in st.session_state:
    st.warning("LIST sheet missing.")
    st.stop()

df = st.session_state["df"].copy()
list_df = st.session_state["list_df"].copy()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

def clean_columns(dataframe):
    dataframe = dataframe.copy()

    dataframe.columns = (
        dataframe.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )

    dataframe = dataframe.loc[
        :,
        ~dataframe.columns.str.startswith("unnamed")
    ]

    return dataframe


df = clean_columns(df)
list_df = clean_columns(list_df)


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = {"id", "idp"}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    st.error(
        "Main dataset is missing required column(s): "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()


# ============================================================
# LINK SPEAKER
# ============================================================

if {"id", "speaker"}.issubset(list_df.columns):

    speaker_map = (
        list_df[["id", "speaker"]]
        .drop_duplicates(subset=["id"])
        .set_index("id")["speaker"]
    )

    df["speaker"] = df["id"].map(speaker_map)
    df["speaker"] = df["speaker"].fillna("Unknown")

else:
    df["speaker"] = "Unknown"


# ============================================================
# PHRASE LEVEL
# ============================================================

df_phrase = df.drop_duplicates(
    subset=["idp"]
).copy()


# ============================================================
# CATEGORY CONFIGURATION
# ============================================================

category_map = {
    "Stylistics": "stylistics",
    "Function": "function",
    "Domain": "domain",
}


# ============================================================
# CATEGORY SELECTION
# ============================================================

st.header("1. Select Category")

available_categories = {
    label: column
    for label, column in category_map.items()
    if column in df_phrase.columns
}

if not available_categories:
    st.error(
        "No category columns found. "
        "Expected at least one of: "
        "`stylistics`, `function`, `domain`."
    )
    st.stop()


category = st.selectbox(
    "Category",
    list(available_categories.keys())
)

cat_col = available_categories[category]


# ============================================================
# SUB-CATEGORY SELECTION
# ============================================================

st.header("2. Select Sub-category")

sub_values = (
    df_phrase[cat_col]
    .dropna()
    .astype(str)
    .str.strip()
)

sub_values = sorted(
    value
    for value in sub_values.unique()
    if value
)

if not sub_values:
    st.warning(
        f"No values found in `{cat_col}`."
    )
    st.stop()


selected_value = st.selectbox(
    "Sub-category",
    sub_values
)


# ============================================================
# FILTER
# ============================================================

filtered_phrase = df_phrase[
    df_phrase[cat_col]
    .astype(str)
    .str.strip()
    == selected_value
].copy()

filtered_full = df[
    df["idp"].isin(filtered_phrase["idp"])
].copy()


# ============================================================
# SUMMARY
# ============================================================

total_phrases = len(filtered_phrase)
total_prayers = filtered_phrase["id"].nunique()

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Total phrases",
        total_phrases
    )

with col2:
    st.metric(
        "Total prayers",
        total_prayers
    )


# ============================================================
# HELPER FUNCTION
# ============================================================

def relation(series, total):
    if series is None or series.empty:
        return pd.DataFrame(
            columns=["value", "n", "%"]
        )

    values = (
        series
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[values != ""]

    if values.empty:
        return pd.DataFrame(
            columns=["value", "n", "%"]
        )

    table = (
        values
        .value_counts()
        .rename_axis("value")
        .reset_index(name="n")
    )

    if total > 0:
        table["%"] = (
            table["n"] / total * 100
        ).round(2)
    else:
        table["%"] = 0.0

    return table


# ============================================================
# RESULT
# ============================================================

st.header("3. Result")


# ============================================================
# BLOCK 1 — KEYWORD RELATION
# TABLE ONLY
# ============================================================

st.subheader("Block 1 — Keyword Relation")

if "keyword" in filtered_full.columns:

    keyword_mask = (
        filtered_full["keyword"].notna()
        & filtered_full["keyword"]
        .astype(str)
        .str.strip()
        .ne("")
    )

    keyword_data = filtered_full.loc[
        keyword_mask
    ].copy()

    if not keyword_data.empty:

        kw = (
            keyword_data
            .groupby("keyword")
            .agg(
                n=("keyword", "size"),
                prayers=(
                    "id",
                    lambda x: ", ".join(
                        sorted(
                            set(x.astype(str))
                        )
                    )
                ),
                speakers=(
                    "speaker",
                    lambda x: ", ".join(
                        sorted(
                            set(x.astype(str))
                        )
                    )
                ),
            )
            .reset_index()
            .sort_values(
                "n",
                ascending=False
            )
        )

        total_keywords = kw["n"].sum()

        if total_keywords > 0:
            kw["%"] = (
                kw["n"]
                / total_keywords
                * 100
            ).round(2)

        st.dataframe(
            kw,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.write(
            "No keyword data for this selection."
        )

else:
    st.write(
        "Keyword column not available."
    )


# ============================================================
# BLOCK 2 — INTERNAL STRUCTURE
# BAR CHARTS ONLY
# ============================================================

st.subheader("Block 2 — Internal Structure")

other_dims = {
    "stylistics": "Stylistics",
    "function": "Function",
    "domain": "Domain",
}


for col, label in other_dims.items():

    if col == cat_col:
        continue

    if col not in filtered_phrase.columns:
        continue

    st.markdown(f"**→ {label}**")

    table = relation(
        filtered_phrase[col],
        total_phrases
    )

    if not table.empty:

        chart_data = (
            table
            .set_index("value")["n"]
        )

        st.bar_chart(
            chart_data,
            use_container_width=True
        )

    else:
        st.write(
            "No data available."
        )


# ============================================================
# BLOCK 3 — PRAYER (ID LEVEL)
# BAR CHART ONLY
# ============================================================

st.subheader("Block 3 — Prayer (ID Level)")

if not filtered_full.empty:

    id_table = (
        filtered_full
        .groupby("id")
        .agg(
            phrases=("idp", "nunique")
        )
        .reset_index()
        .sort_values(
            "phrases",
            ascending=False
        )
    )

    if not id_table.empty:

        st.bar_chart(
            id_table.set_index("id")["phrases"],
            use_container_width=True
        )

    else:
        st.write(
            "No prayer data available."
        )

else:
    st.write(
        "No prayer data available."
    )


# ============================================================
# BLOCK 4 — PHRASE TRACE
# TABLE ONLY
# ============================================================

st.subheader("Block 4 — Phrase Trace")

trace_cols = [
    "id",
    "idp",
    "phrase",
    "stylistics",
    "function",
    "domain",
    "keyword",
    "speaker",
]

trace_cols = [
    col
    for col in trace_cols
    if col in filtered_full.columns
]


if trace_cols:

    trace = (
        filtered_full[trace_cols]
        .sort_values(
            ["id", "idp"]
        )
    )

    st.dataframe(
        trace,
        use_container_width=True,
        hide_index=True
    )

else:
    st.write(
        "No trace columns available."
    )
