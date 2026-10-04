# Qur'an Narrative & Thematic Annotation Framework (v2.1)

An interactive Computational Linguistics dashboard engineered using **Python** and **Streamlit** to track, isolate, and structurally map phrase-level layers and semantic fields across scriptural text datasets. 

Instead of treating textual data as unorganized blocks, this framework applies text-critical methodology to transform classical semantic arrays into machine-readable datasets designed for natural language search optimization and ontological mapping.

---

###  Dataset Core Metrics (Current Manifest)
*   **Total Data Elements Checked (IDp):** 936 Morphological/Linguistic Phrases
*   **Identified System Nodes (ID):** 102 Structured Analytical Units
*   **Source Format Pipeline:** Multi-sheet relation parsing (`Breakdown`, `LIST`, `Codebook`)

---

### Architecture & Pipeline Processing
The dashboard breaks down multi-relational datasets into clean tabular session state models:

1.  **Linguistic Layer Parsing:** Isolates phrase components, syntax structures, and text context tracking markers.
2.  **Taxonomy Harmonization:** Automatically handles row striping, token cleaning, spaces-to-underscore normalization, and data alignment across relational analysis sub-sheets.
3.  **Real-Time Data Distribution:** Passes clean text indices downstream to populate interactive phrase statistical maps and structural semantic network graphs without full-app processing reloads.

---

### Local Environment Execution
To run this text database dashboard framework on your local system, execute the following commands in your console terminal environment:

```bash
# Clone the repository assets
git clone https://github.com

# Move into project repository location
cd quranic-nlp-annotation-framework

# Install primary data handling libraries
pip install -r requirements.txt

# Boot the local application pipeline
streamlit run app.py
```

### Project Repository Layout File Blueprint
```text
├── app.py                            # Primary application dashboard layout entry point
├── Qur'an Prayer Analysis 2.1.xlsx   # Core baseline tracking dataset file matrix
├── requirements.txt                  # Deployment library dependency declarations (streamlit, pandas, openpyxl)
├── README.md                         # Project structural documentation overview file
└── pages/                            # Multi-page sidebar analytics execution scripts
    ├── statistics.py                 # Graph distribution and numeric summaries
    ├── prayer_analysis.py            # Sentence structural and semantic tagging view
    ├── relational_analysis.py        # Relational connections network mapping
    └── keyword_analysis.py           # Text metadata tracking metrics
```
