import requests
import pandas as pd

latitude = 43.451476
longitude = -116.244376

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": "2000-01-01",
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

response = requests.get(url, params=params)

print("Status code:", response.status_code)

if response.status_code == 200:
    data = response.json()

    weather_df = pd.DataFrame(data["daily"])

    weather_df["time"] = pd.to_datetime(weather_df["time"])

    weather_df["year"] = weather_df["time"].dt.year
    weather_df["month"] = weather_df["time"].dt.month

    growing_season = weather_df[
        weather_df["month"].between(4, 9)
    ].copy()

    growing_season["hot_day"] = (
        growing_season["temperature_2m_max"] >= 30
    ).astype(int)

    yearly_weather = (
        growing_season
        .groupby("year")
        .agg(
            temp_mean_c=("temperature_2m_mean", "mean"),
            temp_max_c=("temperature_2m_max", "max"),
            temp_min_c=("temperature_2m_min", "min"),
            precip_total_mm=("precipitation_sum", "sum"),
            solar_radiation_total=("shortwave_radiation_sum", "sum"),
            et0_total_mm=("et0_fao_evapotranspiration", "sum"),
            soil_moisture_mean=("soil_moisture_0_to_7cm_mean", "mean"),
            hot_days_30c=("hot_day", "sum"),
            season_days=("time", "count")
        )
        .reset_index()
    )

    yearly_weather.insert(1, "county_name", "ADA")
    yearly_weather.insert(2, "county_fips", "16001")

    print("\nDaily records downloaded:", len(weather_df))
    print("Growing-season daily records:", len(growing_season))

    print("\nYearly weather shape:")
    print(yearly_weather.shape)

    print("\nYearly weather:")
    print(yearly_weather.to_string(index=False))

    print("\nMissing values:")
    print(yearly_weather.isna().sum())

else:
    print("Request failed")
    print(response.text)