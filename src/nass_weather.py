import pandas as pd

yield_df = pd.read_csv(
    "data/processed/nass_yield.csv",
    dtype={"county_fips": str}
)

weather_df = pd.read_csv(
    "data/processed/open_meteo_growing_season_weather.csv",
    dtype={"county_fips": str}
)

yield_df = yield_df[
    yield_df["year"].between(2020, 2023)
].copy()

yield_df["county_fips"] = (
    yield_df["county_fips"]
    .astype(str)
    .str.zfill(5)
)

weather_df["county_fips"] = (
    weather_df["county_fips"]
    .astype(str)
    .str.zfill(5)
)

yield_df["county_name"] = (
    yield_df["county_name"]
    .str.strip()
    .str.upper()
)

weather_df["county_name"] = (
    weather_df["county_name"]
    .str.strip()
    .str.upper()
)

print("USDA yield rows:", len(yield_df))
print("Weather rows:", len(weather_df))

merged_df = yield_df.merge(
    weather_df,
    on=[
        "year",
        "county_fips",
        "county_name"
    ],
    how="left",
    validate="one_to_one",
    indicator=True
)

print("\nMerge results:")
print(merged_df["_merge"].value_counts())

unmatched_df = merged_df[
    merged_df["_merge"] != "both"
]

print("\nUnmatched USDA rows:")
print(
    unmatched_df[
        [
            "year",
            "county_fips",
            "county_name"
        ]
    ].to_string(index=False)
)

weather_columns = [
    "temp_mean_c",
    "temp_max_c",
    "temp_min_c",
    "precip_total_mm",
    "solar_radiation_total",
    "et0_total_mm",
    "soil_moisture_mean",
    "hot_days_30c",
    "season_days"
]

print("\nMissing weather values:")
print(
    merged_df[
        weather_columns
    ].isna().sum()
)

print("\nRows missing at least one weather feature:")
print(
    merged_df[
        weather_columns
    ]
    .isna()
    .any(axis=1)
    .sum()
)

print("\nDuplicate county-year rows:")
print(
    merged_df.duplicated(
        subset=[
            "year",
            "county_fips"
        ]
    ).sum()
)

merged_df = merged_df.drop(
    columns=["_merge"]
)

merged_df = merged_df.sort_values(
    [
        "year",
        "county_name"
    ]
).reset_index(drop=True)

output_path = (
    "data/processed/"
    "nass_weather_2020_2023.csv"
)

merged_df.to_csv(
    output_path,
    index=False
)

print("\nFinal merged shape:")
print(merged_df.shape)

print("\nFirst 10 merged rows:")
print(
    merged_df[
        [
            "year",
            "county_name",
            "county_fips",
            "yield_bu_acre",
            "temp_mean_c",
            "precip_total_mm",
            "et0_total_mm",
            "soil_moisture_mean",
            "hot_days_30c"
        ]
    ].head(10).to_string(index=False)
)

print("\nMerged dataset saved to:")
print(output_path)