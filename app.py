
import streamlit as st
import pandas as pd
from pulp import LpProblem, LpVariable, LpMaximize, LpBinary, lpSum
import io

st.set_page_config(page_title="Furnace Plate Optimizer", layout="centered")
st.title("🔥 Furnace Plate Optimizer (Optimized by ILP)")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel File with Plate Data", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [col.strip() for col in df.columns]

    if "Plate Weight" not in df.columns:
        st.error("❌ Excel must include a 'Plate Weight' column.")
    else:
        st.success("✅ File uploaded successfully.")
        st.dataframe(df.head())

        capacity = st.number_input("Enter Furnace Capacity (in MT)", min_value=1, value=100)

        if st.button("Optimize Selection"):
            prob = LpProblem("Furnace_Optimization", LpMaximize)
            x = LpVariable.dicts("Select", df.index, cat=LpBinary)

            # Objective and Constraint
            prob += lpSum([x[i] * df.loc[i, "Plate Weight"] for i in df.index])
            prob += lpSum([x[i] * df.loc[i, "Plate Weight"] for i in df.index]) <= capacity

            prob.solve()

            selected = df[[x[i].varValue == 1 for i in df.index]].copy()
            selected.reset_index(drop=True, inplace=True)
            total_weight = selected["Plate Weight"].sum()

            st.success(f"Selected {len(selected)} plates totaling {total_weight:.2f} MT")
            st.dataframe(selected)

            # Download Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                selected.to_excel(writer, index=False, sheet_name="Optimized Plates")
            output.seek(0)

            st.download_button(
                label="📥 Download Optimized Plate Selection",
                data=output,
                file_name=f"Optimized_Furnace_{int(capacity)}MT_Plates.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
