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
# THEME TOGGLE
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

# ---------------------------
# LOAD DATA (FIXED)
# ---------------------------
@st.cache_data
def load_data():
    zip_file = [f for f in os.listdir() if f.endswith(".zip")][0]

    with zipfile.ZipFile(zip_file) as z:
        file_name = [f for f in z.namelist() if f.endswith(".csv")][0]
        with z.open(file_name) as f:
            df = pd.read_csv(f, encoding="cp1252")

    return df

df = load_data()

# ---------------------------
# CLEAN DATA (CRITICAL FIX)
# ---------------------------
df["Operator_Code"] = df["Operator_Code"].astype(str).str.strip()
df["Service"] = df["Service"].astype(str).str.strip()
df["From_Port"] = df["From_Port"].astype(str).str.strip().str.upper()
df["To_Port"] = df["To_Port"].astype(str).str.strip().str.upper()

# Date conversion WITHOUT dropping data
df["Inserted_At"] = pd.to_datetime(df["Inserted_At"], errors="coerce")
df["Inserted_Date"] = df["Inserted_At"].dt.date

# ---------------------------
# FILTERS
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

operator = col1.multiselect("Operator", sorted(df["Operator_Code"].dropna().unique()))
service = col2.multiselect("Service", sorted(df["Service"].dropna().unique()))
from_port = col3.multiselect("From Port", sorted(df["From_Port"].dropna().unique()))
to_port = col4.multiselect("To Port", sorted(df["To_Port"].dropna().unique()))

# ---------------------------
# DATE FILTER (OPTIONAL SAFE)
# ---------------------------
valid_dates = df["Inserted_Date"].dropna()

if not valid_dates.empty:
    min_date = valid_dates.min()
    max_date = valid_dates.max()
else:
    min_date, max_date = None, None

date_range = st.date_input(
    "Select Date Range (Optional)",
    value=(min_date, max_date) if min_date else None
)

# Defaults (show all)
if not operator: operator = df["Operator_Code"].unique()
if not service: service = df["Service"].unique()
if not from_port: from_port = df["From_Port"].unique()
if not to_port: to_port = df["To_Port"].unique()

# ---------------------------
# FILTER DATA (NO DATA LOSS)
# ---------------------------
filtered_df = df[
    (df["Operator_Code"].isin(operator)) &
    (df["Service"].isin(service)) &
    (df["From_Port"].isin(from_port)) &
    (df["To_Port"].isin(to_port))
]

# Apply date filter ONLY if selected
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Inserted_Date"].isna()) |  # keep rows without date
        (
            (filtered_df["Inserted_Date"] >= start_date) &
            (filtered_df["Inserted_Date"] <= end_date)
        )
    ]

# ---------------------------
# KPI CARDS (CORRECT NOW)
# ---------------------------
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="card card1">OPERATORS<br><h1>{df["Operator_Code"].nunique()}</h1></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card card2">PORTS<br><h1>{df["From_Port"].nunique()}</h1></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card card3">TERMINALS<br><h1>{df["From_Port_Terminal"].nunique()}</h1></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card card4">VESSELS<br><h1>{df["Vessel_Name"].nunique()}</h1></div>', unsafe_allow_html=True)

# ---------------------------
# OPERATOR TREND
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
