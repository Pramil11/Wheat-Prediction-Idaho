import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NASS_API_KEY")

if not api_key:
    raise ValueError("NASS_API_KEY not found")

url = "https://quickstats.nass.usda.gov/api/api_GET/"

special_records = []

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

        for record in records:
            if not record["county_ansi"]:
                special_records.append(record)

        print(
            year,
            "| records checked:",
            len(records)
        )

    else:
        print(
            year,
            "| request failed:",
            response.status_code
        )

print("\nRecords without county ANSI:", len(special_records))

special_county_names = set(
    record["county_name"]
    for record in special_records
)

print("\nSpecial county names:")

for county in sorted(special_county_names):
    print(county)

print("\nExample special records:")

for record in special_records[:10]:
    print(
        record["year"],
        "|",
        record["county_name"],
        "| county_code:",
        record["county_code"],
        "| county_ansi:",
        record["county_ansi"],
        "| value:",
        record["Value"]
    )