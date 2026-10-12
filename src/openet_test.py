import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENET_API_KEY")

if not api_key:
    raise ValueError("OPENET_API_KEY not found")

url = "https://openet-api.org/raster/timeseries/point"

headers = {
    "Authorization": api_key,
    "accept": "application/json",
    "Content-Type": "application/json"
}

payload = {
    "date_range": [
        "2020-01-01",
        "2023-12-31"
    ],
    "interval": "monthly",
    "geometry": [
        -116.244376,
        43.451476
    ],
    "model": "Ensemble",
    "variable": "ET",
    "reference_et": "gridMET",
    "units": "mm",
    "file_format": "JSON"
}

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=120
)

print("Status code:", response.status_code)

if response.status_code == 200:
    records = response.json()

    openet_df = pd.DataFrame(records)

    openet_df["time"] = pd.to_datetime(
        openet_df["time"]
    )

    openet_df["year"] = openet_df["time"].dt.year
    openet_df["month"] = openet_df["time"].dt.month

    print("\nMonthly OpenET data shape:")
    print(openet_df.shape)

    print("\nFirst 12 monthly records:")
    print(openet_df.head(12))

    print("\nMissing values:")
    print(openet_df.isna().sum())

    growing_season_df = openet_df[
        openet_df["month"].between(4, 9)
    ].copy()

    yearly_openet = (
        growing_season_df
        .groupby("year")
        .agg(
            actual_et_mm=("et", "sum"),
            openet_months=("et", "count")
        )
        .reset_index()
    )

    yearly_openet.insert(
        1,
        "county_name",
        "ADA"
    )

    yearly_openet.insert(
        2,
        "county_fips",
        "16001"
    )

    print("\nApril-September OpenET summary:")
    print(
        yearly_openet.to_string(
            index=False
        )
    )

else:
    print("\nOpenET request failed:")
    print(response.text)