import time
import requests
import pandas as pd

yield_df = pd.read_csv(
    "data/processed/nass_spring_wheat_yield_clean.csv",
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
        how="left"
    )
    .sort_values("county_name")
    .reset_index(drop=True)
)

print("Counties to download:", len(counties))

url = "https://archive-api.open-meteo.com/v1/archive"

all_daily_weather = []

for index, county in counties.iterrows():

    county_name = county["county_name"]
    county_fips = county["county_fips"]
    latitude = county["latitude"]
    longitude = county["longitude"]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": "2020-01-01",
        "end_date": "2023-12-31",
        "daily": [
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "shortwave_radiation_sum",
            "et0_fao_evapotranspiration",
            "soil_moisture_0_to_7cm_mean"
        ],
        "timezone": "auto"
    }

    max_retries = 5
    attempt = 0

    while attempt < max_retries:

        response = requests.get(
            url,
            params=params,
            timeout=60
        )

        if response.status_code == 200:

            data = response.json()

            daily_df = pd.DataFrame(
                data["daily"]
            )

            daily_df["county_name"] = county_name
            daily_df["county_fips"] = county_fips

            daily_df["requested_latitude"] = latitude
            daily_df["requested_longitude"] = longitude

            daily_df["weather_latitude"] = data["latitude"]
            daily_df["weather_longitude"] = data["longitude"]

            daily_df["timezone"] = data["timezone"]

            all_daily_weather.append(daily_df)

            print(
                f"{index + 1}/{len(counties)}",
                "|",
                county_name,
                "| downloaded:",
                len(daily_df)
            )

            break

        elif response.status_code == 429:

            attempt += 1

            print(
                county_name,
                "| rate limit reached",
                "| waiting 65 seconds",
                "| attempt:",
                attempt
            )

            time.sleep(65)

        else:

            print(
                county_name,
                "| failed:",
                response.status_code
            )

            print(response.text)

            break

    time.sleep(1)

if not all_daily_weather:
    raise ValueError(
        "No Open-Meteo weather data was downloaded."
    )

weather_raw = pd.concat(
    all_daily_weather,
    ignore_index=True
)

weather_raw["time"] = pd.to_datetime(
    weather_raw["time"]
)

print("\nRaw weather shape:")
print(weather_raw.shape)

print("\nCounties successfully downloaded:")
print(weather_raw["county_name"].nunique())

print("\nRaw weather missing values:")
print(weather_raw.isna().sum())

weather_raw.to_csv(
    "data/raw/open_meteo_daily_weather.csv",
    index=False
)

weather_raw["year"] = weather_raw["time"].dt.year
weather_raw["month"] = weather_raw["time"].dt.month

growing_season = weather_raw[
    weather_raw["month"].between(4, 9)
].copy()

growing_season["hot_day"] = (
    growing_season["temperature_2m_max"] >= 30
).astype(int)

weather_processed = (
    growing_season
    .groupby(
        [
            "county_fips",
            "county_name",
            "year"
        ]
    )
    .agg(
        temp_mean_c=(
            "temperature_2m_mean",
            "mean"
        ),
        temp_max_c=(
            "temperature_2m_max",
            "max"
        ),
        temp_min_c=(
            "temperature_2m_min",
            "min"
        ),
        precip_total_mm=(
            "precipitation_sum",
            "sum"
        ),
        solar_radiation_total=(
            "shortwave_radiation_sum",
            "sum"
        ),
        et0_total_mm=(
            "et0_fao_evapotranspiration",
            "sum"
        ),
        soil_moisture_mean=(
            "soil_moisture_0_to_7cm_mean",
            "mean"
        ),
        hot_days_30c=(
            "hot_day",
            "sum"
        ),
        season_days=(
            "time",
            "count"
        )
    )
    .reset_index()
)

weather_processed = weather_processed.sort_values(
    [
        "year",
        "county_name"
    ]
).reset_index(drop=True)

print("\nProcessed weather shape:")
print(weather_processed.shape)

print("\nCounties in processed dataset:")
print(weather_processed["county_name"].nunique())

print("\nMissing values:")
print(weather_processed.isna().sum())

print("\nDuplicate county-year rows:")
print(
    weather_processed.duplicated(
        subset=[
            "county_fips",
            "year"
        ]
    ).sum()
)

print("\nSeason day counts:")
print(
    weather_processed[
        "season_days"
    ].value_counts().sort_index()
)

weather_processed.to_csv(
    "data/processed/open_meteo_growing_season_weather.csv",
    index=False
)

print(
    "\nProcessed weather saved to:",
    "data/processed/open_meteo_growing_season_weather.csv"
)