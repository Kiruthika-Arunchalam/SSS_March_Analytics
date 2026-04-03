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
# THEME
# ---------------------------
theme = st.toggle("🌙 Dark Mode")

bg_color = "#0e1117" if theme else "white"
text_color = "white" if theme else "black"

# ---------------------------
# CSS
# ---------------------------
st.markdown(f"""
<style>
body {{
    background-color: {bg_color};
    color: {text_color};
}}
.title {{
    background: linear-gradient(90deg, #ff9a9e, #a18cd1, #84fab0);
    padding: 18px;
    text-align: center;
    font-size: 30px;
    font-weight: bold;
    color: white;
    border-radius: 12px;
    margin-bottom: 20px;
}}
.section {{
    background: linear-gradient(90deg, #36d1dc, #5b86e5);
    padding: 10px;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    margin-top: 25px;
}}
.card {{
    padding: 25px;
    border-radius: 14px;
    color: white;
    text-align: center;
    font-weight: bold;
}}
.card1 {{ background: linear-gradient(135deg, #ff9a9e, #fad0c4); }}
.card2 {{ background: linear-gradient(135deg, #a18cd1, #fbc2eb); }}
.card3 {{ background: linear-gradient(135deg, #f6d365, #fda085); }}
.card4 {{ background: linear-gradient(135deg, #84fab0, #8fd3f4); }}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# CHART STYLE
# ---------------------------
def style_chart(fig):
    axis_color = "white" if theme else "black"
    fig.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font_color=text_color,
        xaxis=dict(tickfont=dict(color=axis_color)),
        yaxis=dict(tickfont=dict(color=axis_color))
    )
    return fig

# ---------------------------
# TITLE
# ---------------------------
st.markdown('<div class="title">SSS DATA ANALYTICS DASHBOARD</div>', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import zipfile

st.set_page_config(layout="wide")

st.title("📊 Operator Summary Dashboard")

# ---------------------------
# FILE UPLOAD
# ---------------------------
uploaded_file = st.file_uploader("Upload CSV or ZIP file", type=["csv", "zip"])

if uploaded_file:

    # 🔍 Show file name (debug)
    st.write("📁 File Loaded:", uploaded_file.name)

    # ---------------------------
    # READ FILE (CSV / ZIP)
    # ---------------------------
    if uploaded_file.name.endswith(".zip"):
        with zipfile.ZipFile(uploaded_file, 'r') as z:
            file_list = z.namelist()
            st.write("ZIP contains:", file_list)

            # Read first CSV inside zip
            csv_files = [f for f in file_list if f.endswith(".csv")]

            if csv_files:
                df = pd.read_csv(z.open(csv_files[0]))
            else:
                st.error("❌ No CSV file found inside ZIP")
                st.stop()
    else:
        df = pd.read_csv(uploaded_file)

    st.success("✅ File Loaded Successfully")

    # ---------------------------
    # BASIC CLEANING
    # ---------------------------
    df.columns = df.columns.str.strip()

    # Convert date
    df["Inserted_Date"] = pd.to_datetime(df["Inserted_Date"], errors="coerce")

    # ---------------------------
    # DEBUG (IMPORTANT)
    # ---------------------------
    st.write("🔢 Total Rows:", len(df))
    st.write("🧾 Unique Operators:", df["Operator_Code"].nunique())
    st.dataframe(df.tail(5))

    # ---------------------------
    # FILTER DATA (optional)
    # ---------------------------
    filtered_df = df.copy()

    # ---------------------------
    # SUMMARY TABLE WITH TOTAL
    # ---------------------------
    st.markdown("### 📅 Date vs Operator Summary")

    summary_df = (
        filtered_df
        .dropna(subset=["Inserted_Date", "Operator_Code"])
        .groupby(["Inserted_Date", "Operator_Code"])
        .size()
        .reset_index(name="Operator_Count")
    )

    # Sort
    summary_df = summary_df.sort_values(by=["Inserted_Date", "Operator_Code"])

    # ---------------------------
    # TOTAL ROW PER DATE
    # ---------------------------
    total_df = (
        summary_df
        .groupby("Inserted_Date", as_index=False)["Operator_Count"]
        .sum()
    )

    total_df["Operator_Code"] = "TOTAL"

    # Combine
    final_df = pd.concat([summary_df, total_df], ignore_index=True)

    # ---------------------------
    # FORMAT DATE
    # ---------------------------
    final_df["Inserted_Date"] = final_df["Inserted_Date"].dt.strftime("%d-%m-%Y")

    # ---------------------------
    # SORT (TOTAL LAST)
    # ---------------------------
    final_df = final_df.sort_values(
        by=["Inserted_Date", "Operator_Code"],
        key=lambda col: col if col.name != "Operator_Code" else col.replace("TOTAL", "ZZZ")
    ).reset_index(drop=True)

    # ---------------------------
    # DISPLAY
    # ---------------------------
    st.dataframe(final_df, use_container_width=True)

else:
    st.info("👆 Please upload a CSV or ZIP file to proceed")
# ---------------------------
# CLEAN DATA
# ---------------------------
df["Operator_Code"] = df["Operator_Code"].astype(str).str.strip()
df["Service"] = df["Service"].astype(str).str.strip()
df["From_Port"] = df["From_Port"].astype(str).str.strip().str.upper()
df["To_Port"] = df["To_Port"].astype(str).str.strip().str.upper()

df["Inserted_At"] = pd.to_datetime(df["Inserted_At"], errors="coerce", dayfirst=True)
df["Inserted_Date"] = df["Inserted_At"].dt.normalize()

# ---------------------------
# FILTER UI
# ---------------------------
st.markdown("### Filters")

col1, col2, col3, col4 = st.columns(4)

operator_list = sorted(df["Operator_Code"].dropna().unique())
service_list = sorted(df["Service"].dropna().unique())
from_port_list = sorted(df["From_Port"].dropna().unique())
to_port_list = sorted(df["To_Port"].dropna().unique())

operator = col1.multiselect("Operator", operator_list)
service = col2.multiselect("Service", service_list)
from_port = col3.multiselect("From Port", from_port_list)
to_port = col4.multiselect("To Port", to_port_list)

# ---------------------------
# DATE SLIDER (FIXED)
# ---------------------------
valid_dates = df["Inserted_Date"].dropna()

if not valid_dates.empty:
    min_date = valid_dates.min().to_pydatetime()
    max_date = valid_dates.max().to_pydatetime()

    date_range = st.slider(
        "📅 Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )
else:
    date_range = None

# ---------------------------
# DEFAULT FILTERS
# ---------------------------
if not operator: operator = operator_list
if not service: service = service_list
if not from_port: from_port = from_port_list
if not to_port: to_port = to_port_list

# ---------------------------
# APPLY FILTERS
# ---------------------------
filtered_df = df[
    (df["Operator_Code"].isin(operator)) &
    (df["Service"].isin(service)) &
    (df["From_Port"].isin(from_port)) &
    (df["To_Port"].isin(to_port))
]

# DATE FILTER
if date_range:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Inserted_Date"] >= pd.to_datetime(start_date)) &
        (filtered_df["Inserted_Date"] <= pd.to_datetime(end_date))
    ]

# ---------------------------
# KPI CARDS
# ---------------------------
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="card card1">OPERATORS<br><h1>{filtered_df["Operator_Code"].nunique()}</h1></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card card2">PORTS<br><h1>{filtered_df["From_Port"].nunique()}</h1></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card card3">TERMINALS<br><h1>{filtered_df["From_Port_Terminal"].nunique()}</h1></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card card4">VESSELS<br><h1>{filtered_df["Vessel_Name"].nunique()}</h1></div>', unsafe_allow_html=True)

import pandas as pd

# Ensure date format is correct
df['Inserted_Date'] = pd.to_datetime(df['Inserted_Date']).dt.date



# ---------------------------
# SUMMARY TABLE WITH TOTAL
# ---------------------------
st.markdown('<div class="section">Date vs Operator Summary</div>', unsafe_allow_html=True)

# Create summary from FILTERED DATA
summary_df = (
    filtered_df
    .dropna(subset=["Inserted_Date", "Operator_Code"])
    .groupby(["Inserted_Date", "Operator_Code"])
    .size()
    .reset_index(name="Operator_Count")   # ✅ FIX
)

# Sort before formatting
summary_df = summary_df.sort_values(by=["Inserted_Date", "Operator_Code"])

# ✅ Add TOTAL row per date
total_df = (
    summary_df
    .groupby("Inserted_Date", as_index=False)["Operator_Count"]
    .sum()
)

total_df["Operator_Code"] = "TOTAL"

# Combine both
final_df = pd.concat([summary_df, total_df], ignore_index=True)

# ✅ Format date (ONLY for display)
final_df["Inserted_Date"] = pd.to_datetime(final_df["Inserted_Date"]).dt.strftime("%d-%m-%Y")

# ✅ Sort so TOTAL comes last
final_df = final_df.sort_values(
    by=["Inserted_Date", "Operator_Code"],
    key=lambda col: col if col.name != "Operator_Code" else col.replace("TOTAL", "ZZZ")
).reset_index(drop=True)   # ✅ Fix continuous index

# Display
st.dataframe(final_df, use_container_width=True)# OPERATOR TREND
# ---------------------------
st.markdown('<div class="section">Date Wise Operator Trend</div>', unsafe_allow_html=True)

trend = (
    filtered_df.dropna(subset=["Inserted_Date"])
    .groupby(["Inserted_Date", "Operator_Code"])
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

fig.update_traces(textposition="outside", textfont=dict(size=9))
fig = style_chart(fig)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# OPERATOR COMPARISON
# ---------------------------
st.markdown('<div class="section">Operator Comparison</div>', unsafe_allow_html=True)

compare = filtered_df["Operator_Code"].value_counts().reset_index()
compare.columns = ["Operator", "Count"]

fig_compare = px.bar(compare, x="Operator", y="Count", color="Operator")
fig_compare = style_chart(fig_compare)

st.plotly_chart(fig_compare, use_container_width=True)

# ---------------------------
# TOP ROUTES
# ---------------------------
st.markdown('<div class="section">Top Routes</div>', unsafe_allow_html=True)

route_df = (
    filtered_df.groupby(["From_Port", "To_Port"])
    .size()
    .reset_index(name="Count")
)

route_df["Route"] = route_df["From_Port"] + " → " + route_df["To_Port"]
route_df = route_df.sort_values(by="Count", ascending=False).head(10)

fig_route = px.bar(route_df, x="Count", y="Route", orientation="h", color="Route")
fig_route = style_chart(fig_route)

st.plotly_chart(fig_route, use_container_width=True)

# ---------------------------
# SERVICE DISTRIBUTION
# ---------------------------
st.markdown('<div class="section">Service Distribution</div>', unsafe_allow_html=True)

service_df = filtered_df["Service"].value_counts().reset_index()
service_df.columns = ["Service", "Count"]

fig_service = px.bar(service_df.head(10), x="Count", y="Service", orientation="h", color="Count")
fig_service = style_chart(fig_service)

st.plotly_chart(fig_service, use_container_width=True)
