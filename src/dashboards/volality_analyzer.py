from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt
from utils.functions import convert_to_datetime


class VolatilityAnalyzer:
    def __init__(self, data_file: Path):
        self.df = pd.read_csv(data_file.resolve())

    def calculate_yearly_volatility(self) -> pd.DataFrame:
        self.df["date"] = convert_to_datetime(self.df["date"])
        latest_date = self.df["date"].max()
        previous_date = latest_date.replace(year=latest_date.year - 1)

        yearly_data = self.df[self.df["date"].isin([previous_date, latest_date])].drop(
            columns=["date"]
        )

        volatility_dataset = (
            yearly_data.groupby("commodity")["price"]
            .agg(std_dev="std", mean_price="mean")
            .reset_index()
        )
        volatility_dataset["cv"] = (
            volatility_dataset["std_dev"] / volatility_dataset["mean_price"]
        ) * 100
        return volatility_dataset[["commodity", "cv"]]

    def show_dashboard(self, df: pd.DataFrame):
        # Top 5 KPIs
        st.subheader("🔥 Top 5 Most Volatile Commodities (Yearly)")
        cols = st.columns(5)
        top_5 = df.nlargest(5, "cv")

        for i, col in enumerate(cols):
            if i < len(top_5):
                commodity, cv = top_5.iloc[i]
                with col:
                    st.metric(label=commodity, value=f"{cv:.2f}%")

        # Data Table
        st.subheader("📋 Volatility Data Table")
        st.dataframe(
            df.style.background_gradient(
                cmap="RdYlGn_r", subset=["cv"], vmin=0, vmax=100
            ).format({"cv": "{:.2f}%"})
        )

        # Chart
        st.subheader("📈 Volatility by Commodity")
        chart = (
            alt.Chart(df)
            .mark_bar(cornerRadius=4)
            .encode(
                x=alt.X("commodity", sort="-y", title="Commodity"),
                y=alt.Y("cv", title="Volatility (%)"),
                color=alt.Color(
                    "cv",
                    scale=alt.Scale(scheme="redyellowgreen", reverse=True),
                    legend=None,
                ),
                tooltip=["commodity", alt.Tooltip("cv", format=".2f")],
            )
            .properties(height=400)
        )
        st.altair_chart(chart, use_container_width=True)
