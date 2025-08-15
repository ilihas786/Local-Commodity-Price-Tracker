import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from utils.functions import convert_to_datetime

# Use os.path to get the absolute path of this script file
script_path = os.path.abspath(__file__)
root_dir = Path(script_path).parent.parent
source_file = root_dir / "data" / "processed" / "data.csv"

# print(f"Script location: {script_path}")
# print(f"Root directory: {root_dir}")
# print(f"Source file path: {source_file}")
# print(f"Source file exists: {source_file.exists()}")
# print(f"Absolute path: {source_file.resolve()}")


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

        latest_prices.drop(columns=["date"], inplace=True)
        year_back_prices.drop(columns=["date"], inplace=True)

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
        one_month_ago = latest_date.replace(month=latest_date.month - 1)

        latest_prices = df[df["date"] == latest_date]
        month_back_prices = df[df["date"] == one_month_ago]

        latest_prices.drop(columns=["date"], inplace=True)
        month_back_prices.drop(columns=["date"], inplace=True)

        inflation_df = latest_prices.merge(
            month_back_prices,
            on=["commodity", "unit"],
            suffixes=("_latest", "_month_back"),
        )

        inflation_df["inflation_rate"] = self.calculate_inflation_rate(
            inflation_df["price_latest"], inflation_df["price_month_back"]
        )

        return inflation_df[["commodity", "unit", "inflation_rate"]]

    def show_dataset_streamlit(self, df: pd.DataFrame, view_type: str) -> None:
        st.title(f"{view_type} Inflation Rate Data Table")
        st.dataframe(df)


inflation_analyzer = InflationAnalyzer(source_file)
inflation_yearly_df = inflation_analyzer.generate_year_wise_inflation_dataset(
    inflation_analyzer.df
)

inflation_monthly_df = inflation_analyzer.generate_month_wise_inflation_dataset(
    inflation_analyzer.df
)
view_type = st.selectbox("Select view", ["Yearly", "Monthly"])

if view_type == "Yearly":
    inflation_analyzer.show_dataset_streamlit(inflation_yearly_df,view_type)
else :
    inflation_analyzer.show_dataset_streamlit(inflation_monthly_df,view_type)