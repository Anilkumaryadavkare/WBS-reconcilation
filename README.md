# 📊 WBS-AUC Reconciliation Dashboard

A clean and efficient **Streamlit app** for reconciling WBS-level transactions — classifying POs vs Non-POs, filtering out unwanted document types, and auto-removing offsetting entries.

Built to streamline **Capex and AUC validation** workflows for project teams and finance analysts.

---

## 🚀 Features

✅ Auto-classifies transactions as **PO / Non-PO** based on `Purch.Doc.`  
✅ Excludes rows where **`DocTyp == 'CS'`**  
✅ Identifies and removes **offsetting entries** (same WBS, description, vendor, and ± amount)  
✅ Generates clean downloads:
- A file with **only Non POs**
- A **final full cleaned report** with:
  - PO count
  - Non PO count
  - CS exclusions
  - Offset pairs removed

---

## 📂 File Upload Structure

Ensure your Excel file includes the following columns:

- `Purch.Doc.` — (used to classify PO vs Non PO)
- `DocTyp` — (used to filter CS entries)
- `ValCOArCur` — (used to identify offsetting entries)
- Other key context columns: `WBS Element`, `Purchase order text`, `Offset. acct name`, `Text`...

---

## 📸 Screenshot

![Dashboard Screenshot](./assets/dashboard_sample.png)

---

## 🛠️ Installation

```bash
git clone https://github.com/Anilkumaryadavkare/WBS-reconcilation.git
cd WBS-reconcilation
pip install -r requirements.txt
streamlit run streamlit_app.py
