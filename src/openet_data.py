import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

START_YEAR = 2020
END_YEAR = 2023
MAX_RETRIES = 5
WAIT_BETWEEN_REQUESTS = 2

load_dotenv()

api_key = os.getenv("OPENET_API_KEY")

if not api_key:
    raise ValueError("OPENET_API_KEY not found")

yield_df = pd.read_csv(
    "data/processed/nass_weather.csv",
    dtype={"county_fips": str}
)

locations_df = pd.read_csv(
    "data/processed/idaho_county_locations.csv",
    dtype={"county_fips": str}
)

counties = (
    yield_df[
        [
            "county_fips",
            "county_name"
        ]
    ]
    .drop_duplicates()
    .merge(
        locations_df[
            [
                "county_fips",
                "latitude",
                "longitude"
            ]
        ],
        on="county_fips",
        how="left",
        validate="one_to_one"
    )
    .sort_values("county_name")
    .reset_index(drop=True)
)

if counties[
    [
        "latitude",
        "longitude"
    ]
].isna().any().any():
    missing_counties = counties[
        counties["latitude"].isna()
        | counties["longitude"].isna()
    ]

    raise ValueError(
        f"Missing county coordinates:\n{missing_counties}"
    )

print("Counties to download:", len(counties))

url = "https://openet-api.org/raster/timeseries/point"

headers = {
    "Authorization": api_key,
    "accept": "application/json",
    "Content-Type": "application/json"
}

session = requests.Session()

all_monthly_data = []
failed_counties = []

for index, county in counties.iterrows():

    county_name = county["county_name"]
    county_fips = county["county_fips"]
    latitude = float(county["latitude"])
    longitude = float(county["longitude"])

    payload = {
        "date_range": [
            f"{START_YEAR}-01-01",
            f"{END_YEAR}-12-31"
        ],
        "interval": "monthly",
        "geometry": [
            longitude,
            latitude
        ],
        "model": "Ensemble",
        "variable": "ET",
        "reference_et": "gridMET",
        "units": "mm",
        "file_format": "JSON"
    }

    records = None

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):
        try:
            response = session.post(
                url,
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                records = response.json()
                break

            if response.status_code == 429:
                print(
                    county_name,
                    "| rate limit reached",
                    "| waiting 65 seconds",
                    f"| attempt {attempt}/{MAX_RETRIES}"
                )

                time.sleep(65)
                continue

            if response.status_code >= 500:
                print(
                    county_name,
                    "| server error:",
                    response.status_code,
                    "| waiting 20 seconds",
                    f"| attempt {attempt}/{MAX_RETRIES}"
                )

                time.sleep(20)
                continue

            print(
                county_name,
                "| request failed:",
                response.status_code
            )

            print(response.text)
            break

        except requests.RequestException as error:

            print(
                county_name,
                "| network error:",
                error,
                f"| attempt {attempt}/{MAX_RETRIES}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(20)

    if records is None:
        failed_counties.append(
            {
                "county_fips": county_fips,
                "county_name": county_name
            }
        )

        continue

    if not isinstance(records, list):
        failed_counties.append(
            {
                "county_fips": county_fips,
                "county_name": county_name
            }
        )

        print(
            county_name,
            "| unexpected response:",
            records
        )

        continue

    monthly_df = pd.DataFrame(records)

    required_columns = {
        "time",
        "et"
    }

    if not required_columns.issubset(
        monthly_df.columns
    ):
        failed_counties.append(
            {
                "county_fips": county_fips,
                "county_name": county_name
            }
        )

        print(
            county_name,
            "| missing expected columns"
        )

        continue

    monthly_df["time"] = pd.to_datetime(
        monthly_df["time"]
    )

    monthly_df["et"] = pd.to_numeric(
        monthly_df["et"],
        errors="coerce"
    )

    monthly_df["county_fips"] = county_fips
    monthly_df["county_name"] = county_name
    monthly_df["latitude"] = latitude
    monthly_df["longitude"] = longitude

    all_monthly_data.append(monthly_df)

    print(
        f"{index + 1}/{len(counties)}",
        "|",
        county_name,
        "| downloaded:",
        len(monthly_df)
    )

    time.sleep(WAIT_BETWEEN_REQUESTS)

if failed_counties:
    failed_df = pd.DataFrame(
        failed_counties
    )

    print("\nFailed counties:")
    print(
        failed_df.to_string(
            index=False
        )
    )

    raise RuntimeError(
        "OpenET data collection was incomplete."
    )

if not all_monthly_data:
    raise ValueError(
        "No OpenET data was downloaded."
    )

openet_raw = pd.concat(
    all_monthly_data,
    ignore_index=True
)

openet_raw["year"] = (
    openet_raw["time"].dt.year
)

openet_raw["month"] = (
    openet_raw["time"].dt.month
)

openet_raw = openet_raw[
    [
        "county_fips",
        "county_name",
        "latitude",
        "longitude",
        "time",
        "year",
        "month",
        "et"
    ]
]

openet_raw = openet_raw.sort_values(
    [
        "county_name",
        "time"
    ]
).reset_index(drop=True)

print("\nRaw monthly OpenET shape:")
print(openet_raw.shape)

print("\nCounties downloaded:")
print(
    openet_raw[
        "county_fips"
    ].nunique()
)

print("\nRaw monthly missing values:")
print(
    openet_raw.isna().sum()
)

print("\nMonthly records per county:")
print(
    openet_raw
    .groupby("county_name")
    .size()
    .value_counts()
    .sort_index()
)

openet_raw.to_csv(
    "data/raw/openet_monthly.csv",
    index=False
)

growing_season = openet_raw[
    openet_raw["month"].between(
        4,
        9
    )
].copy()

openet_processed = (
    growing_season
    .groupby(
        [
            "county_fips",
            "county_name",
            "year"
        ]
    )
    .agg(
        actual_et_mm=(
            "et",
            lambda values: values.sum(
                min_count=6
            )
        ),
        openet_months=(
            "time",
            "count"
        ),
        valid_et_months=(
            "et",
            "count"
        ),
        openet_point_latitude=(
            "latitude",
            "first"
        ),
        openet_point_longitude=(
            "longitude",
            "first"
        )
    )
    .reset_index()
)

openet_processed = (
    openet_processed
    .sort_values(
        [
            "year",
            "county_name"
        ]
    )
    .reset_index(drop=True)
)

duplicate_count = (
    openet_processed
    .duplicated(
        subset=[
            "county_fips",
            "year"
        ]
    )
    .sum()
)

print("\nProcessed OpenET shape:")
print(openet_processed.shape)

print("\nExpected processed rows:")
print(
    len(counties)
    * (
        END_YEAR
        - START_YEAR
        + 1
    )
)

print("\nActual processed rows:")
print(len(openet_processed))

print("\nMissing values:")
print(
    openet_processed.isna().sum()
)

print("\nDuplicate county-year rows:")
print(duplicate_count)

print("\nOpenET month counts:")
print(
    openet_processed[
        [
            "openet_months",
            "valid_et_months"
        ]
    ]
    .value_counts()
    .sort_index()
)

print("\nActual ET summary:")
print(
    openet_processed[
        "actual_et_mm"
    ].describe()
)

print("\nFirst 10 processed rows:")
print(
    openet_processed
    .head(10)
    .to_string(index=False)
)

openet_processed.to_csv(
    "data/processed/openet_seasonal.csv",
    index=False
)

print(
    "\nRaw OpenET data saved to:",
    "data/raw/openet_monthly.csv"
)

print(
    "Processed OpenET data saved to:",
    "data/processed/openet_seasonal.csv"
)