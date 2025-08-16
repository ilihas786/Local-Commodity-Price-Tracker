import os
from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

from utils.functions import convert_to_datetime

# File paths
script_path = os.path.abspath(__file__)
root_dir = Path(script_path).parent.parent
source_file = root_dir / "data" / "processed" / "data.csv"


class InflationAnalyzer:
    def __init__(self, data_file: Path):
        self.df = pd.read_csv(data_file.resolve())

    def calculate_inflation_rate(
        self, from_column: pd.Series, to_column: pd.Series
    ) -> pd.Series:
        return ((to_column - from_column) / from_column) * 100

    def generate_year_wise_inflation_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        df["date"] = convert_to_datetime(df["date"])
        latest_date = df["date"].max()
        one_year_ago = latest_date.replace(year=latest_date.year - 1)

        latest_prices = df[df["date"] == latest_date]
        year_back_prices = df[df["date"] == one_year_ago]

        latest_prices = latest_prices.drop(columns=["date"])
        year_back_prices = year_back_prices.drop(columns=["date"])

        inflation_df = latest_prices.merge(
            year_back_prices,
            on=["commodity", "unit"],
            suffixes=("_latest", "_year_back"),
        )

        inflation_df["inflation_rate"] = self.calculate_inflation_rate(
            inflation_df["price_latest"], inflation_df["price_year_back"]
        )

        return inflation_df[["commodity", "unit", "inflation_rate"]]

    def generate_month_wise_inflation_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        df["date"] = convert_to_datetime(df["date"])
        latest_date = df["date"].max()
        one_month_ago = latest_date - pd.DateOffset(months=1)

        latest_prices = df[df["date"] == latest_date]
        month_back_prices = df[df["date"] == one_month_ago]

        latest_prices = latest_prices.drop(columns=["date"])
        month_back_prices = month_back_prices.drop(columns=["date"])

        inflation_df = latest_prices.merge(
            month_back_prices,
            on=["commodity", "unit"],
            suffixes=("_latest", "_month_back"),
        )

        inflation_df["inflation_rate"] = self.calculate_inflation_rate(
            inflation_df["price_latest"], inflation_df["price_month_back"]
        )

        return inflation_df[["commodity", "unit", "inflation_rate"]]


# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="Inflation Dashboard", layout="wide")

st.title("📈 Inflation Rate Dashboard")

inflation_analyzer = InflationAnalyzer(source_file)
inflation_yearly_df = inflation_analyzer.generate_year_wise_inflation_dataset(
    inflation_analyzer.df
)
inflation_monthly_df = inflation_analyzer.generate_month_wise_inflation_dataset(
    inflation_analyzer.df
)

tab1, tab2 = st.tabs(["📅 Yearly Inflation", "📅 Monthly Inflation"])


def show_dashboard(df: pd.DataFrame, view_type: str):
    # Metrics at top
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Highest Inflation", f"{df['inflation_rate'].max():.2f}%")
    col2.metric("📉 Lowest Inflation", f"{df['inflation_rate'].min():.2f}%")
    col3.metric("⚖️ Avg Inflation", f"{df['inflation_rate'].mean():.2f}%")

    # Styled Dataframe
    st.subheader("📋 Data Table")
    st.dataframe(
        df.style.background_gradient(
            cmap="RdYlGn_r",
            subset=["inflation_rate"],
            vmin=-5,  # lowest meaningful inflation (deflation)
            vmax=20,  # cap for high inflation
        ).format({"inflation_rate": "{:.2f}%"})
    )
    # Interactive Chart (Altair)
    st.subheader("📊 Inflation by Commodity")
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("commodity", sort="-y"),
            y="inflation_rate",
            color=alt.Color(
                "inflation_rate",
                scale=alt.Scale(
                    scheme="redyellowgreen", reverse=True
                ),  # green = low, red = high
            ),
            tooltip=["commodity", "unit", alt.Tooltip("inflation_rate", format=".2f")],
        )
        .properties(width="container", height=400)
    )
    st.altair_chart(chart, use_container_width=True)


with tab1:
    show_dashboard(inflation_yearly_df, "Yearly")

with tab2:
    show_dashboard(inflation_monthly_df, "Monthly")
