import streamlit as st
import pandas as pd
import io

# ------------------ Streamlit Page Config ------------------
st.set_page_config(page_title="WBS-AUC Reconciliation Dashboard", layout="wide")
st.markdown("# The WBS-AUC Reconciliation Dashboard")
st.markdown("""
Upload your **WBS transaction dump** to:
- Auto-classify PO vs Non-PO
- Exclude DocTyp = 'CS'
- Remove exact offsetting entries
- Download final reconciled reports
""")

# ------------------ Upload File ------------------
with st.expander("📁 Upload Transaction File"):
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

# ------------------ Processing Logic ------------------
def process_wbs_auc_data(df):
    original_len = len(df)

    # Tag PO or Non PO based on 'Purch.Doc.' column
    df['PO_Status'] = df['Purch.Doc.'].apply(lambda x: 'Non PO' if pd.isna(x) else 'PO')

    # Filter out DocTyp = 'CS'
    df_cs_excluded = df[df['DocTyp'] == 'CS']
    df = df[df['DocTyp'] != 'CS']

    # Create key for identifying offsetting pairs
    df['ValCOArCur'] = pd.to_numeric(df['ValCOArCur'], errors='coerce')
    df['dup_key'] = df['WBS Element'].astype(str) + '|' + df['Purchase order text'].astype(str) + '|' + df['Offset. acct name'].astype(str) + '|' + df['ValCOArCur'].abs().astype(str)

    # Find and remove offsetting pairs
    key_counts = df['dup_key'].value_counts()
    duplicate_keys = key_counts[key_counts > 1].index

    pairs_removed = 0
    indices_to_remove = []
    for key in duplicate_keys:
        group = df[df['dup_key'] == key]
        if len(group) >= 2:
            pos = group[group['ValCOArCur'] > 0]
            neg = group[group['ValCOArCur'] < 0]
            min_len = min(len(pos), len(neg))
            if min_len > 0:
                indices_to_remove.extend(pos.index[:min_len])
                indices_to_remove.extend(neg.index[:min_len])
                pairs_removed += min_len

    df_cleaned = df.drop(index=indices_to_remove).copy()

    # Split for output
    non_po_df = df_cleaned[df_cleaned['PO_Status'] == 'Non PO'].copy()

    # Final Summary
    summary = {
        "#Original Entries": original_len,
        "#POs": (df_cleaned['PO_Status'] == 'PO').sum(),
        "#Non POs": (df_cleaned['PO_Status'] == 'Non PO').sum(),
        "#Excluded CS docs": len(df_cs_excluded),
        "#Offset pairs removed": pairs_removed,
    }

    # Drop helper col
    df_cleaned.drop(columns=['dup_key'], inplace=True, errors='ignore')

    return df_cleaned, non_po_df, summary

# ------------------ Display & Download ------------------
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        with st.spinner("Processing data..."):
            cleaned_df, non_po_df, summary = process_wbs_auc_data(df)

        st.success("Data processed successfully!")

        # Summary display
        st.markdown("### 🔍 Summary of Reconciliation")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Original", summary["#Original Entries"])
        col2.metric("POs", summary["#POs"])
        col3.metric("Non POs", summary["#Non POs"])
        col4.metric("CS Excluded", summary["#Excluded CS docs"])
        col5.metric("Offset Pairs Removed", summary["#Offset pairs removed"])

        # Convert to Excel
        def to_excel_bytes(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()

        excel_all = to_excel_bytes(cleaned_df)
        excel_non_po = to_excel_bytes(non_po_df)

        st.markdown("### 📄 Download Reports")
        col1, col2 = st.columns(2)
        col1.download_button("📃 Download Cleaned Report", data=excel_all, file_name="WBS_Cleaned_Report.xlsx")
        col2.download_button("📃 Download Non PO Entries", data=excel_non_po, file_name="WBS_Non_PO_Report.xlsx")

    except Exception as e:
        st.error(f"Something went wrong while processing the file: {e}")
