from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

from utils.functions import convert_to_datetime


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

        latest_prices = df[df["date"] == latest_date].drop(columns=["date"])
        year_back_prices = df[df["date"] == one_year_ago].drop(columns=["date"])

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

        latest_prices = df[df["date"] == latest_date].drop(columns=["date"])
        month_back_prices = df[df["date"] == one_month_ago].drop(columns=["date"])

        inflation_df = latest_prices.merge(
            month_back_prices,
            on=["commodity", "unit"],
            suffixes=("_latest", "_month_back"),
        )

        inflation_df["inflation_rate"] = self.calculate_inflation_rate(
            inflation_df["price_latest"], inflation_df["price_month_back"]
        )
        return inflation_df[["commodity", "unit", "inflation_rate"]]

    def show_dashboard(self, df: pd.DataFrame, title: str):
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Highest Inflation", f"{df['inflation_rate'].max():.2f}%")
        col2.metric("📉 Lowest Inflation", f"{df['inflation_rate'].min():.2f}%")
        col3.metric("⚖️ Avg Inflation", f"{df['inflation_rate'].mean():.2f}%")

        # Data Table
        st.subheader("📋 Inflation Data Table")
        st.dataframe(
            df.style.background_gradient(
                cmap="RdYlGn_r", subset=["inflation_rate"], vmin=-5, vmax=20
            ).format({"inflation_rate": "{:.2f}%"})
        )

        # Chart
        st.subheader("📊 Inflation by Commodity")
        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("commodity", sort="-y"),
                y="inflation_rate",
                color=alt.Color(
                    "inflation_rate",
                    scale=alt.Scale(scheme="redyellowgreen", reverse=True),
                ),
                tooltip=[
                    "commodity",
                    "unit",
                    alt.Tooltip("inflation_rate", format=".2f"),
                ],
            )
            .properties(width="container", height=400)
        )
        st.altair_chart(chart, use_container_width=True)
