import pandas as pd

nass_weather_df = pd.read_csv(
    "data/processed/nass_weather_2020_2023.csv",
    dtype={"county_fips": str}
)

openet_df = pd.read_csv(
    "data/processed/openet_growing_season_2020_2023.csv",
    dtype={"county_fips": str}
)

nass_weather_df["county_fips"] = (
    nass_weather_df["county_fips"]
    .astype(str)
    .str.zfill(5)
)

openet_df["county_fips"] = (
    openet_df["county_fips"]
    .astype(str)
    .str.zfill(5)
)

nass_weather_df["county_name"] = (
    nass_weather_df["county_name"]
    .str.strip()
    .str.upper()
)

openet_df["county_name"] = (
    openet_df["county_name"]
    .str.strip()
    .str.upper()
)

nass_weather_df["year"] = (
    nass_weather_df["year"].astype(int)
)

openet_df["year"] = (
    openet_df["year"].astype(int)
)

print("USDA-weather rows:", len(nass_weather_df))
print("OpenET rows:", len(openet_df))

final_df = nass_weather_df.merge(
    openet_df,
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
print(final_df["_merge"].value_counts())

unmatched_df = final_df[
    final_df["_merge"] != "both"
]

print("\nUnmatched USDA-weather rows:")
print(
    unmatched_df[
        [
            "year",
            "county_fips",
            "county_name"
        ]
    ].to_string(index=False)
)

openet_columns = [
    "actual_et_mm",
    "openet_months",
    "valid_et_months",
    "openet_point_latitude",
    "openet_point_longitude"
]

print("\nMissing OpenET values:")
print(
    final_df[
        openet_columns
    ].isna().sum()
)

print("\nRows missing actual ET:")
print(
    final_df[
        "actual_et_mm"
    ].isna().sum()
)

print("\nDuplicate county-year rows:")
print(
    final_df.duplicated(
        subset=[
            "year",
            "county_fips"
        ]
    ).sum()
)

final_df = final_df.drop(
    columns=["_merge"]
)

final_df = final_df.sort_values(
    [
        "year",
        "county_name"
    ]
).reset_index(drop=True)

output_path = (
    "data/processed/"
    "idaho_spring_wheat_final_2020_2023.csv"
)

final_df.to_csv(
    output_path,
    index=False
)

print("\nFinal integrated dataset shape:")
print(final_df.shape)

print("\nFinal columns:")
print(final_df.columns.tolist())

print("\nMissing values in final dataset:")
print(final_df.isna().sum())

print("\nFirst 10 integrated rows:")
print(
    final_df[
        [
            "year",
            "county_name",
            "county_fips",
            "yield_bu_acre",
            "temp_mean_c",
            "precip_total_mm",
            "et0_total_mm",
            "actual_et_mm",
            "soil_moisture_mean",
            "hot_days_30c"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nFinal dataset saved to:")
print(output_path)