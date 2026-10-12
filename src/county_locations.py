import pandas as pd

file_path = "data/raw/idaho_counties_gazetteer.txt"

df = pd.read_csv(
    file_path,
    sep="\t",
    dtype={"GEOID": str}
)

df.columns = df.columns.str.strip()

print("Rows:", len(df))

print("\nColumns:")
print(df.columns.tolist())

county_locations = df[
    [
        "GEOID",
        "NAME",
        "INTPTLAT",
        "INTPTLONG"
    ]
].copy()

county_locations = county_locations.rename(
    columns={
        "GEOID": "county_fips",
        "NAME": "county_name",
        "INTPTLAT": "latitude",
        "INTPTLONG": "longitude"
    }
)

county_locations["county_name"] = (
    county_locations["county_name"]
    .str.replace(" County", "", regex=False)
    .str.upper()
)

print("\nFirst 10 counties:")
print(county_locations.head(10))

print("\nShape:")
print(county_locations.shape)

print("\nMissing values:")
print(county_locations.isna().sum())

county_locations.to_csv(
    "data/processed/idaho_county_locations.csv",
    index=False
)

print("\nSaved to data/processed/idaho_county_locations.csv")