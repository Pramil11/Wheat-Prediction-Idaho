import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NASS_API_KEY")

if not api_key:
    raise ValueError("NASS_API_KEY not found")

url = "https://quickstats.nass.usda.gov/api/api_GET/"

all_records = []

for year in range(2000, 2024):
    params = {
        "key": api_key,
        "commodity_desc": "WHEAT",
        "state_alpha": "ID",
        "agg_level_desc": "COUNTY",
        "year": str(year),
        "freq_desc": "ANNUAL",
        "statisticcat_desc": "YIELD",
        "class_desc": "SPRING, (EXCL DURUM)",
        "prodn_practice_desc": "ALL PRODUCTION PRACTICES",
        "unit_desc": "BU / ACRE",
        "format": "JSON"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        records = data.get("data", [])

        usable_records = [
            record
            for record in records
            if record["county_ansi"]
        ]

        all_records.extend(usable_records)

        print(year, "| downloaded:", len(usable_records))

    else:
        print(year, "| request failed:", response.status_code)
        print(response.text)

invalid_records = [
    record
    for record in all_records
    if not record["county_ansi"]
]

print("\nTotal usable records:", len(all_records))
print("Invalid county records remaining:", len(invalid_records))

df = pd.DataFrame(all_records)

print("\nRaw DataFrame shape:", df.shape)

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

raw_file_path = "data/raw/nass_raw.csv"

df.to_csv(
    raw_file_path,
    index=False
)

print("\nRaw dataset saved to:", raw_file_path)

yield_df = df[
    [
        "year",
        "county_name",
        "county_ansi",
        "state_ansi",
        "asd_desc",
        "Value",
        "unit_desc",
        "CV (%)"
    ]
].copy()

yield_df = yield_df.rename(
    columns={
        "Value": "yield_bu_acre",
        "CV (%)": "cv_percent"
    }
)

yield_df["yield_bu_acre"] = pd.to_numeric(
    yield_df["yield_bu_acre"],
    errors="coerce"
)

yield_df["cv_percent"] = pd.to_numeric(
    yield_df["cv_percent"],
    errors="coerce"
)

yield_df["county_fips"] = (
    yield_df["state_ansi"].astype(str)
    + yield_df["county_ansi"].astype(str).str.zfill(3)
)

yield_df = yield_df[
    [
        "year",
        "county_name",
        "county_fips",
        "asd_desc",
        "yield_bu_acre",
        "unit_desc",
        "cv_percent"
    ]
]

yield_df = yield_df.sort_values(
    by=["year", "county_name"]
).reset_index(drop=True)

print("\nCleaned DataFrame shape:", yield_df.shape)

print("\nCleaned columns:")
print(yield_df.columns.tolist())

print("\nFirst 10 cleaned rows:")
print(yield_df.head(10))

print("\nData types:")
print(yield_df.dtypes)

print("\nMissing values:")
print(yield_df.isna().sum())

print("\nDuplicate county-year rows:")
print(
    yield_df.duplicated(
        subset=["year", "county_fips"]
    ).sum()
)

print("\nYield summary:")
print(yield_df["yield_bu_acre"].describe())

print("\nLowest 10 yields:")
print(
    yield_df[
        [
            "year",
            "county_name",
            "yield_bu_acre"
        ]
    ]
    .sort_values("yield_bu_acre")
    .head(10)
)

print("\nHighest 10 yields:")
print(
    yield_df[
        [
            "year",
            "county_name",
            "yield_bu_acre"
        ]
    ]
    .sort_values(
        "yield_bu_acre",
        ascending=False
    )
    .head(10)
)

print("\nCV values available by year:")
print(
    yield_df
    .groupby("year")["cv_percent"]
    .count()
)

q1 = yield_df["yield_bu_acre"].quantile(0.25)
q3 = yield_df["yield_bu_acre"].quantile(0.75)

iqr = q3 - q1

lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

outliers = yield_df[
    (yield_df["yield_bu_acre"] < lower_bound)
    | (yield_df["yield_bu_acre"] > upper_bound)
]

print("\nQ1:", q1)
print("Q3:", q3)
print("IQR:", iqr)
print("Lower outlier boundary:", lower_bound)
print("Upper outlier boundary:", upper_bound)

print("\nNumber of statistical outliers:", len(outliers))

processed_file_path = "data/processed/nass_yield.csv"

yield_df.to_csv(
    processed_file_path,
    index=False
)

print("\nCleaned dataset saved to:", processed_file_path)