import pandas as pd
from pathlib import Path

# Get the script's directory and build paths relative to the project root
script_dir = Path(__file__).parent
project_root = script_dir.parent
RAW_FILE = project_root / "data" / "raw" / "retail_prices.xlsx"
FINAL_FILE = project_root / "data" / "processed" / "data.csv"
print(f"Raw file path: {RAW_FILE}")
print(f"Final file path: {FINAL_FILE}")

def clean_dataset(filepath: Path,final_path:Path) -> None:
    print(f"Loading Raw Data from {filepath}")
    df = pd.read_excel(filepath)

    # Convert all column headers to strings
    df.columns = df.columns.astype(str)
    df.columns = df.columns.str.strip()
    df.rename(columns={
        "Commodities": "commodity",
        "Unit": "unit"
    }, inplace=True)
    
    df = df.melt(id_vars=["commodity", "unit"], var_name="date", value_name="price")


    # convert date string to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    print(df.info())
    # convert price string to numeric
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Save final processed dataset
    final_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(final_path, index=False)
    print(f"Cleaned data saved to {final_path}")

if __name__ == "__main__":
    clean_dataset(RAW_FILE, FINAL_FILE)


    
