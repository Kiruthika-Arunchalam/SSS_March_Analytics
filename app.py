import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import os

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="SSS Dashboard", layout="wide")

# ---------------------------
# TITLE
# ---------------------------
st.title("📊 SSS DATA ANALYTICS DASHBOARD")

# ---------------------------
# AUTO DETECT ZIP FILE
# ---------------------------
files = os.listdir()

zip_files = [f for f in files if f.lower().endswith(".zip")]

if not zip_files:
    st.error("❌ No ZIP file found in app folder")
    st.write("Available files:", files)
    st.stop()

FILE_PATH = zip_files[0]

st.write("📁 Using file:", FILE_PATH)

# ---------------------------
# LOAD ZIP
# ---------------------------
with zipfile.ZipFile(FILE_PATH, 'r') as z:
    file_list = z.namelist()

    st.write("ZIP contains:", file_list)

    csv_files = [f for f in file_list if f.endswith(".csv")]

    if not csv_files:
        st.error("❌ No CSV inside ZIP")
        st.stop()

    df = pd.read_csv(z.open(csv_files[0]))

st.success("✅ File Loaded Successfully")
# ---------------------------
# CLEAN DATA
# ---------------------------
df.columns = df.columns.str.strip()

df["Operator_Code"] = df["Operator_Code"].astype(str).str.strip()
df["Service"] = df["Service"].astype(str).str.strip()
df["From_Port"] = df["From_Port"].astype(str).str.upper().str.strip()
df["To_Port"] = df["To_Port"].astype(str).str.upper().str.strip()

df["Inserted_At"] = pd.to_datetime(df["Inserted_At"], errors="coerce", dayfirst=True)
df["Inserted_Date"] = df["Inserted_At"].dt.normalize()

# ---------------------------
# DEBUG
# ---------------------------
st.write("Rows:", len(df))
st.write("Operators:", df["Operator_Code"].nunique())

# ---------------------------
# SUMMARY TABLE
# ---------------------------
st.subheader("📅 Date vs Operator Summary")

summary_df = (
    df
    .dropna(subset=["Inserted_Date", "Operator_Code"])
    .groupby(["Inserted_Date", "Operator_Code"])
    .size()
    .reset_index(name="Operator_Count")
)

# TOTAL
total_df = summary_df.groupby("Inserted_Date", as_index=False)["Operator_Count"].sum()
total_df["Operator_Code"] = "TOTAL"

# Merge
final_df = pd.concat([summary_df, total_df], ignore_index=True)

# Format date
final_df["Inserted_Date"] = pd.to_datetime(final_df["Inserted_Date"]).dt.strftime("%d-%m-%Y")

# Sort
final_df = final_df.sort_values(
    by=["Inserted_Date", "Operator_Code"],
    key=lambda col: col if col.name != "Operator_Code" else col.replace("TOTAL", "ZZZ")
).reset_index(drop=True)

st.dataframe(final_df, use_container_width=True)

# ---------------------------
# CHART
# ---------------------------
st.subheader("📊 Operator Trend")

trend = (
    df.groupby(["Inserted_Date", "Operator_Code"])
    .size()
    .reset_index(name="Count")
)

fig = px.bar(
    trend,
    y="Inserted_Date",
    x="Count",
    color="Operator_Code",
    orientation="h",
    text="Operator_Code"
)

fig.update_traces(textposition="outside")

st.plotly_chart(fig, use_container_width=True)
# ---------------------------
# SERVICE DISTRIBUTION
# ---------------------------
st.markdown('<div class="section">Service Distribution</div>', unsafe_allow_html=True)

service_df = filtered_df["Service"].value_counts().reset_index()
service_df.columns = ["Service", "Count"]

fig_service = px.bar(service_df.head(10), x="Count", y="Service", orientation="h", color="Count")
fig_service = style_chart(fig_service)

st.plotly_chart(fig_service, use_container_width=True)
