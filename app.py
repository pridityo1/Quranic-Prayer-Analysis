import streamlit as st
import pandas as pd
import os

st.title("Qur'anic Prayer Analysis")

# ============================================================
# 0. INSTRUCTION
# ============================================================

st.markdown("Upload dataset (.xlsx) to begin")

# ============================================================
# 1. FILE UPLOAD & BACKUP CONFIGURATION
# ============================================================

file = st.file_uploader("Upload Dataset", type=["xlsx", "csv"])
DEFAULT_FILE_NAME = "Qur'anic Prayer Analysis 2.1.xlsx"

# ============================================================
# 2. CLEAN FUNCTION
# ============================================================

def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    df = df.loc[:, ~df.columns.str.contains("^unnamed")]
    return df

# ============================================================
# 3. LOAD DATA (SMART ACCELERATOR WITH AUTOMATED CLOUD FALLBACK)
# ============================================================

# Step A: Check if a file was explicitly uploaded by the user
if file:
    try:
        # CASE 1: EXCEL (MAIN MODE)
        if file.name.endswith(".xlsx"):
            breakdown = pd.read_excel(file, sheet_name="Breakdown", engine="openpyxl")
            list_df = pd.read_excel(file, sheet_name="LIST", engine="openpyxl")
            codebook = pd.read_excel(file, sheet_name="Codebook", engine="openpyxl")

            breakdown = clean_columns(breakdown)
            list_df = clean_columns(list_df)
            codebook = clean_columns(codebook)

            st.session_state["df"] = breakdown
            st.session_state["list_df"] = list_df
            st.session_state["codebook"] = codebook
        
        # CASE 2: CSV (LIMITED)
        else:
            df = pd.read_csv(file)
            df = clean_columns(df)

            st.session_state["df"] = df
            st.session_state["list_df"] = None
            st.session_state["codebook"] = None

        st.success("Dataset loaded successfully!")

    except Exception as e:
        st.error(f"Error loading uploaded dataset: {e}")

# Step B: CLOUD SAFE FIX — If no file is uploaded, automatically check for repo data
elif os.path.exists(DEFAULT_FILE_NAME):
    try:
        breakdown = pd.read_excel(DEFAULT_FILE_NAME, sheet_name="Breakdown", engine="openpyxl")
        list_df = pd.read_excel(DEFAULT_FILE_NAME, sheet_name="LIST", engine="openpyxl")
        codebook = pd.read_excel(DEFAULT_FILE_NAME, sheet_name="Codebook", engine="openpyxl")

        st.session_state["df"] = clean_columns(breakdown)
        st.session_state["list_df"] = clean_columns(list_df)
        st.session_state["codebook"] = clean_columns(codebook)
        
        st.info(f"💡 Live Demo Mode: Automatically loaded '{DEFAULT_FILE_NAME}' from repository.")
        
    except Exception as e:
        st.error(f"Error loading system fallback dataset: {e}")

# ============================================================
# 4. STATUS PANEL
# ============================================================

st.markdown("---")
st.subheader("System Status")

if "df" in st.session_state:

    st.success("Breakdown loaded")

    if st.session_state.get("list_df") is not None:
        st.success("LIST loaded")
    else:
        st.warning("LIST not available")

    if st.session_state.get("codebook") is not None:
        st.success("Codebook loaded")
    else:
        st.warning("Codebook not available")

    # Basic diagnostics
    st.markdown("### Dataset Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Total phrases (IDp):", len(st.session_state["df"]))

    if st.session_state.get("list_df") is not None:
        with col2:
            st.write(
                "Total prayers (ID):",
                st.session_state["list_df"]["id"].nunique()
            )

    st.info("Navigate using sidebar pages")

else:
    st.warning("Please upload dataset first")
