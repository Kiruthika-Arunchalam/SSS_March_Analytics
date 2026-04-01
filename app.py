import streamlit as st
import pandas as pd
import plotly.express as px

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
# PREMIUM CSS
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
def style_chart(fig, bg_color, text_color, theme):
    axis_color = "white" if theme else "black"
    grid_color = "#444" if theme else "#e5e5e5"

    fig.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font_color=text_color,
        xaxis=dict(
            showgrid=False,
            gridcolor=grid_color,
            linecolor=axis_color,
            tickfont=dict(color=axis_color),
            tickcolor=axis_color,
            showline=False,
            title=dict(font=dict(color=axis_color))
        ),
        yaxis=dict(
            showgrid=False,
            gridcolor=grid_color,
            linecolor=axis_color,
            tickfont=dict(color=axis_color),
            tickcolor=axis_color,
            showline=False,
            title=dict(font=dict(color=axis_color))
        )
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
    import zipfile

    with zipfile.ZipFile("SSS_Mar_26.zip") as z:
        file_name = z.namelist()[0]
        with z.open(file_name) as f:
            df = pd.read_csv(f, encoding="cp1252")

    return df


# ✅ CALL FUNCTION OUTSIDE (NO INDENT)
df = load_data()


df["From_Port"] = df["From_Port"].str.upper()
df["To_Port"] = df["To_Port"].str.upper()

if df is None or df.empty:
    st.error("Data not loaded!")
    st.stop()

df["Inserted_At"] = pd.to_datetime(df["Inserted_At"], errors="coerce")

# ---------------------------
# DATE CLEANING (FIXED)
# ---------------------------

# Remove invalid dates
df = df.dropna(subset=["Inserted_At"])

# Convert to date
df["Inserted_Date"] = df["Inserted_At"].dt.date

# ---------------------------
# FILTERS
# ---------------------------


col1, col2, col3, col4 = st.columns(4)

operator = col1.multiselect("Operator", df["Operator_Code"].unique())
service = col2.multiselect("Service", df["Service"].unique())
from_port = col3.multiselect("From Port", df["From_Port"].unique())
to_port = col4.multiselect("To Port", df["To_Port"].unique())

# ---------------------------
# DATE RANGE FILTER (FIXED)
# ---------------------------
min_date = df["Inserted_Date"].min()
max_date = df["Inserted_Date"].max()

date_range = st.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Handle single date selection
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Defaults
if not operator: operator = df["Operator_Code"].unique()
if not service: service = df["Service"].unique()
if not from_port: from_port = df["From_Port"].unique()
if not to_port: to_port = df["To_Port"].unique()

# ---------------------------
# FILTER DATA
# ---------------------------
filtered_df = df[
    (df["Operator_Code"].isin(operator)) &
    (df["Service"].isin(service)) &
    (df["From_Port"].isin(from_port)) &
    (df["To_Port"].isin(to_port)) &
    (df["Inserted_Date"] >= start_date) &
    (df["Inserted_Date"] <= end_date)
]

# ---------------------------
# KPI CARDS
# ---------------------------
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="card card1">OPERATORS<br><h1>{filtered_df["Operator_Code"].nunique()}</h1></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card card2">PORTS<br><h1>{filtered_df["From_Port"].nunique()}</h1></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card card3">TERMINALS<br><h1>{filtered_df["From_Port_Terminal"].nunique()}</h1></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card card4">VESSELS<br><h1>{filtered_df["Vessel_Name"].nunique()}</h1></div>', unsafe_allow_html=True)

# ---------------------------
# OPERATOR TREND (STACKED BAR)
# ---------------------------
st.markdown('<div class="section">Date Wise Operator Trend</div>', unsafe_allow_html=True)

trend = (
    filtered_df.groupby(["Inserted_Date", "Operator_Code"])
    .size()
    .reset_index(name="Count")
)

fig = px.bar(
    trend,
    y="Inserted_Date",
    x="Count",
    color="Operator_Code",
    barmode="stack",
    orientation="h",
    text="Operator_Code"   # ✅ Correct mapping
)

# ✅ FIXED LABEL DISPLAY
fig.update_traces(
    textposition="outside",   # auto inside/outside
    textfont=dict(size=9)
)

# ✅ FIXED SYNTAX (NO EXTRA BRACKET)
fig.update_layout(
    yaxis=dict(
        tickformat="%d-%m-%Y"
    )
)

fig = style_chart(fig, bg_color, text_color, theme)

st.plotly_chart(fig, use_container_width=True)
# ---------------------------
# OPERATOR COMPARISON
# ---------------------------
st.markdown('<div class="section"> Operator Comparison</div>', unsafe_allow_html=True)

compare = (
    filtered_df["Operator_Code"]
    .value_counts()
    .reset_index()
)

compare.columns = ["Operator", "Count"]

fig_compare = px.bar(
    compare,
    x="Operator",
    y="Count",
    color="Operator",
    color_discrete_sequence=px.colors.qualitative.Dark24
)

fig_compare = style_chart(fig_compare, bg_color, text_color, theme)

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

fig_route = px.bar(
    route_df,
    x="Count",
    y="Route",
    orientation="h",
    color="Route",
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig_route = style_chart(fig_route, bg_color, text_color, theme)

st.plotly_chart(fig_route, use_container_width=True)

# ---------------------------
# SERVICE DISTRIBUTION
# ---------------------------
st.markdown('<div class="section">Service Distribution</div>', unsafe_allow_html=True)

service_df = filtered_df["Service"].value_counts().reset_index()
service_df.columns = ["Service", "Count"]

fig_service = px.bar(
    service_df.head(10),
    x="Count",
    y="Service",
    orientation="h",
    color="Count",
    color_continuous_scale="Sunset"
)

fig_service = style_chart(fig_service, bg_color, text_color, theme)

st.plotly_chart(fig_service, use_container_width=True)

# ---------------------------
# DOWNLOAD BUTTON 🔥
# ---------------------------
#st.markdown("### 📥 Download Data")

#st.download_button(
    #label="Download Filtered Data (CSV)",
    #data=filtered_df.to_csv(index=False),
    #file_name="filtered_data.csv",
    #mime="text/csv"
#)
