import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Keyword Analysis")

# ============================================================
# LOAD DATA
# ============================================================

if "df" not in st.session_state:
    st.warning("Please upload the dataset from the main page first.")
    st.stop()

if "list_df" not in st.session_state:
    st.warning("LIST sheet is not available.")
    st.stop()

df = st.session_state["df"].copy()
list_df = st.session_state["list_df"].copy()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

def clean_columns(data):
    data.columns = (
        data.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    data = data.loc[
        :,
        ~data.columns.str.contains("^unnamed")
    ]

    return data


df = clean_columns(df)
list_df = clean_columns(list_df)


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_breakdown = [
    "id",
    "idp",
    "phrase",
    "stylistics",
    "function",
    "domain",
    "keyword",
    "key_concept",
    "key_type"
]

for col in required_breakdown:
    if col not in df.columns:
        st.error(f"Breakdown is missing column: {col}")
        st.stop()


if "id" not in list_df.columns or "speaker" not in list_df.columns:
    st.error("LIST sheet must contain 'id' and 'speaker' columns.")
    st.stop()


# ============================================================
# CLEAN KEYWORD COLUMNS
# ============================================================

for col in ["keyword", "key_concept", "key_type"]:
    df[col] = (
        df[col]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# ============================================================
# PHRASE-LEVEL DATA
# ============================================================

# One row per IDp.
# Used for stylistics, function, and domain.

df_phrase = (
    df
    .drop_duplicates(subset=["idp"])
    .copy()
)


# ============================================================
# LINK SPEAKER FROM LIST
# ============================================================

speaker_map = (
    list_df[
        ["id", "speaker"]
    ]
    .drop_duplicates(subset=["id"])
    .set_index("id")["speaker"]
)

df["speaker"] = df["id"].map(speaker_map)
df_phrase["speaker"] = df_phrase["id"].map(speaker_map)

df["speaker"] = (
    df["speaker"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)

df_phrase["speaker"] = (
    df_phrase["speaker"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)


# ============================================================
# 1. KEYWORD INVENTORY
# ============================================================

st.header("1. Keyword Inventory")

# ------------------------------------------------------------
# 1.1 Keyword Table
# ------------------------------------------------------------

st.subheader("1.1 Keyword Table")

keyword_df = df[df["keyword"] != ""].copy()

keyword_inventory = (
    keyword_df
    .groupby("keyword")
    .agg(
        Instances=("keyword", "size"),

        Key_Concept=(
            "key_concept",
            lambda x: ", ".join(
                sorted(
                    set(
                        v for v in x
                        if v
                    )
                )
            )
        ),

        Key_Type=(
            "key_type",
            lambda x: ", ".join(
                sorted(
                    set(
                        v for v in x
                        if v
                    )
                )
            )
        ),

        Speakers=(
            "speaker",
            lambda x: ", ".join(
                sorted(
                    set(
                        v for v in x
                        if v
                    )
                )
            )
        ),

        Prayer_IDs=(
            "id",
            lambda x: ", ".join(
                sorted(
                    set(
                        v for v in x
                        if v
                    )
                )
            )
        )
    )
    .reset_index()
    .sort_values(
        ["Instances", "keyword"],
        ascending=[False, True]
    )
)

st.dataframe(
    keyword_inventory,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 2. KEYWORD FREQUENCY
# ============================================================

st.header("2. Keyword Frequency")

# ------------------------------------------------------------
# 2.1 Top-N Keyword Chart
# ------------------------------------------------------------

st.subheader("2.1 Top-N Keyword Chart")

top_n = st.slider(
    "Number of keywords",
    min_value=5,
    max_value=50,
    value=20,
    key="keyword_top_n"
)

top_keywords = (
    keyword_inventory
    .head(top_n)
    .set_index("keyword")["Instances"]
)

st.bar_chart(top_keywords)


# ============================================================
# 3. SPEAKER COMPOSITION
# ============================================================

st.header("3. Speaker Composition")

st.caption(
    "Each bar represents the internal composition of a speaker's "
    "prayers. Stylistics, function, and domain use phrase-level "
    "data; keyword uses the full keyword-level data."
)


# ------------------------------------------------------------
# HELPER FUNCTION
# ------------------------------------------------------------

def speaker_composition_chart(
    data,
    category_column,
    category_title,
    chart_key
):

    composition = (
        data
        .groupby(
            ["speaker", category_column]
        )
        .size()
        .reset_index(name="count")
    )

    totals = (
        composition
        .groupby("speaker")["count"]
        .sum()
        .reset_index(name="total")
    )

    composition = composition.merge(
        totals,
        on="speaker"
    )

    composition["percentage"] = (
        composition["count"]
        / composition["total"]
        * 100
    )

    composition["speaker_label"] = (
        composition["speaker"]
        + " (n="
        + composition["total"]
        .astype(int)
        .astype(str)
        + ")"
    )

    fig = px.bar(
        composition,
        x="percentage",
        y="speaker_label",
        color=category_column,
        orientation="h",
        text=None
    )

    fig.update_layout(
        barmode="stack",
        xaxis=dict(
            range=[0, 100],
            ticksuffix="%",
            title="Percentage"
        ),
        yaxis=dict(
            title="Speaker",
            categoryorder="total ascending"
        ),
        legend_title=category_title,
        height=500,
        margin=dict(
            l=120,
            r=30,
            t=30,
            b=50
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=chart_key
    )


# ------------------------------------------------------------
# 3.1 SPEAKER → STYLISTICS
# ------------------------------------------------------------

st.subheader("3.1 Speaker → Stylistics")

speaker_composition_chart(
    df_phrase,
    "stylistics",
    "Stylistics",
    "speaker_stylistics_chart"
)


# ------------------------------------------------------------
# 3.2 SPEAKER → FUNCTION
# ------------------------------------------------------------

st.subheader("3.2 Speaker → Function")

speaker_composition_chart(
    df_phrase,
    "function",
    "Function",
    "speaker_function_chart"
)


# ------------------------------------------------------------
# 3.3 SPEAKER → DOMAIN
# ------------------------------------------------------------

st.subheader("3.3 Speaker → Domain")

speaker_composition_chart(
    df_phrase,
    "domain",
    "Domain",
    "speaker_domain_chart"
)


# ------------------------------------------------------------
# 3.4 SPEAKER → KEYWORD
# ------------------------------------------------------------

st.subheader("3.4 Speaker → Keyword")

keyword_composition = df[
    df["keyword"] != ""
].copy()

speaker_composition_chart(
    keyword_composition,
    "keyword",
    "Keyword",
    "speaker_keyword_chart"
)


# ============================================================
# 4. KEYWORD-CENTERED ANALYSIS
# ============================================================

st.header("4. Keyword-Centered Analysis")


# ------------------------------------------------------------
# 4.1 SELECT KEYWORD
# ------------------------------------------------------------

st.subheader("4.1 Select Keyword")

keyword_list = sorted(
    keyword_df["keyword"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

selected_keyword = st.selectbox(
    "Keyword",
    keyword_list,
    key="keyword_select"
)


# ------------------------------------------------------------
# FILTER ONLY BY KEYWORD
# ------------------------------------------------------------

kw_df = keyword_df[
    keyword_df["keyword"] == selected_keyword
].copy()


# ------------------------------------------------------------
# 4.2 SUMMARY
# ------------------------------------------------------------

st.subheader("4.2 Summary")

st.markdown(
    f"**Keyword:** `{selected_keyword}`"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Instances",
        len(kw_df)
    )

with col2:
    st.metric(
        "Prayer IDs",
        kw_df["id"].nunique()
    )

with col3:
    st.metric(
        "Phrases",
        kw_df["idp"].nunique()
    )


# ------------------------------------------------------------
# 4.3 KEY CONCEPT
# ------------------------------------------------------------

st.subheader("4.3 Key Concept")

concepts = (
    kw_df["key_concept"]
    .replace("", pd.NA)
    .dropna()
    .value_counts()
)

if concepts.empty:
    st.info("No key concept available.")
else:
    st.dataframe(
        concepts.rename("Instances"),
        use_container_width=True
    )


# ------------------------------------------------------------
# 4.4 KEY TYPE
# ------------------------------------------------------------

st.subheader("4.4 Key Type")

types = (
    kw_df["key_type"]
    .replace("", pd.NA)
    .dropna()
    .value_counts()
)

if types.empty:
    st.info("No key type available.")
else:
    st.dataframe(
        types.rename("Instances"),
        use_container_width=True
    )


# ------------------------------------------------------------
# 4.5 SPEAKER DISTRIBUTION
# ------------------------------------------------------------

st.subheader("4.5 Speaker Distribution")

speaker_counts = (
    kw_df["speaker"]
    .value_counts()
)

st.bar_chart(
    speaker_counts
)


# ------------------------------------------------------------
# 4.6 PRAYER DISTRIBUTION
# ------------------------------------------------------------

st.subheader("4.6 Prayer Distribution")

id_counts = (
    kw_df["id"]
    .value_counts()
)

st.bar_chart(
    id_counts
)


# ------------------------------------------------------------
# 4.7 KEYWORD OCCURRENCES
# ------------------------------------------------------------

st.subheader("4.7 Keyword Occurrences")

occurrence_columns = [
    "id",
    "idp",
    "phrase",
    "keyword",
    "key_concept",
    "key_type",
    "stylistics",
    "function",
    "domain",
    "speaker"
]

available_columns = [
    col
    for col in occurrence_columns
    if col in kw_df.columns
]

occurrences = (
    kw_df[available_columns]
    .drop_duplicates()
    .sort_values(
        ["id", "idp"]
    )
)

st.dataframe(
    occurrences,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 5. SPEAKER-CENTERED ANALYSIS
# ============================================================

st.header("5. Speaker-Centered Analysis")


# ------------------------------------------------------------
# 5.1 SELECT SPEAKER
# ------------------------------------------------------------

st.subheader("5.1 Select Speaker")

speaker_list = sorted(
    df["speaker"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

selected_speaker = st.selectbox(
    "Speaker",
    speaker_list,
    key="speaker_keyword_select"
)


# ------------------------------------------------------------
# FILTER ONLY BY SPEAKER
# ------------------------------------------------------------

speaker_df = df[
    df["speaker"] == selected_speaker
].copy()


# ------------------------------------------------------------
# 5.2 KEYWORD DISTRIBUTION
# ------------------------------------------------------------

st.subheader("5.2 Keyword Distribution")

speaker_keywords = (
    speaker_df[
        speaker_df["keyword"] != ""
    ]["keyword"]
    .value_counts()
)

st.bar_chart(
    speaker_keywords
)


# ------------------------------------------------------------
# 5.3 KEYWORD INVENTORY
# ------------------------------------------------------------

st.subheader("5.3 Keyword Inventory")

speaker_inventory = (
    speaker_df[
        speaker_df["keyword"] != ""
    ]
    .groupby("keyword")
    .agg(
        Instances=("keyword", "size"),

        Key_Concept=(
            "key_concept",
            lambda x: ", ".join(
                sorted(
                    set(
                        v for v in x
                        if v
                    )
                )
            )
        ),

        Key_Type=(
            "key_type",
            lambda x: ", ".join(
                sorted(
                    set(
                        v for v in x
                        if v
                    )
                )
            )
        ),

        Prayer_IDs=(
            "id",
            lambda x: ", ".join(
                sorted(
                    set(
                        v for v in x
                        if v
                    )
                )
            )
        )
    )
    .reset_index()
    .sort_values(
        ["Instances", "keyword"],
        ascending=[False, True]
    )
)

st.dataframe(
    speaker_inventory,
    use_container_width=True,
    hide_index=True
)


# ------------------------------------------------------------
# 5.4 SPEAKER KEYWORD OCCURRENCES
# ------------------------------------------------------------

st.subheader("5.4 Speaker Keyword Occurrences")

speaker_occurrence_columns = [
    "id",
    "idp",
    "phrase",
    "keyword",
    "key_concept",
    "key_type",
    "stylistics",
    "function",
    "domain",
    "speaker"
]

available_speaker_columns = [
    col
    for col in speaker_occurrence_columns
    if col in speaker_df.columns
]

speaker_occurrences = (
    speaker_df[
        speaker_df["keyword"] != ""
    ][available_speaker_columns]
    .drop_duplicates()
    .sort_values(
        ["keyword", "id", "idp"]
    )
)

st.dataframe(
    speaker_occurrences,
    use_container_width=True,
    hide_index=True
)