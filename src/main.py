import os
from pathlib import Path
import streamlit as st

from dashboards.Inflation_analyzer import InflationAnalyzer
from dashboards.volality_analyzer import VolatilityAnalyzer

# ================== FILE PATHS ==================
script_path = os.path.abspath(__file__)
root_dir = Path(script_path).parent.parent
source_file = root_dir / "data" / "processed" / "data.csv"

# ================== STREAMLIT MAIN APP ==================
st.set_page_config(page_title="Local Commodity Price Tracker", layout="wide")

st.title("📊 Commodity Analysis Dashboard")

# Sidebar navigation
page = st.sidebar.radio(
    "Select Dashboard", ["📈 Inflation Analysis", "📉 Volatility Analysis"]
)

# Initialize analyzers
inflation_analyzer = InflationAnalyzer(source_file)
volatility_analyzer = VolatilityAnalyzer(source_file)

# Load datasets
inflation_yearly_df = inflation_analyzer.generate_year_wise_inflation_dataset(
    inflation_analyzer.df
)
inflation_monthly_df = inflation_analyzer.generate_month_wise_inflation_dataset(
    inflation_analyzer.df
)
volatility_df = volatility_analyzer.calculate_yearly_volatility()

# Render selected dashboard
if page == "📈 Inflation Analysis":
    tab1, tab2 = st.tabs(["📅 Yearly Inflation", "📅 Monthly Inflation"])
    with tab1:
        inflation_analyzer.show_dashboard(inflation_yearly_df, "Yearly")
    with tab2:
        inflation_analyzer.show_dashboard(inflation_monthly_df, "Monthly")

elif page == "📉 Volatility Analysis":
    volatility_analyzer.show_dashboard(volatility_df)
