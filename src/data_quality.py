import pandas as pd

df = pd.read_csv(
    "data/processed/final_dataset.csv",
    dtype={"county_fips": str}
)

print("Dataset shape:")
print(df.shape)

print("\nMissing values:")
print(df.isna().sum())

print("\nDuplicate county-year rows:")
print(
    df.duplicated(
        subset=["year", "county_fips"]
    ).sum()
)

print("\nUnique values for categorical / constant fields:")

categorical_columns = [
    "county_name",
    "county_fips",
    "asd_desc",
    "unit_desc"
]

for column in categorical_columns:
    print(
        column,
        ":",
        df[column].nunique(),
        "unique values"
    )

print("\nConstant columns:")

for column in df.columns:
    if df[column].nunique(dropna=False) == 1:
        print(
            column,
            "=",
            df[column].iloc[0]
        )

print("\nNumeric ranges:")

numeric_columns = [
    "yield_bu_acre",
    "cv_percent",
    "temp_mean_c",
    "temp_max_c",
    "temp_min_c",
    "precip_total_mm",
    "solar_radiation_total",
    "et0_total_mm",
    "soil_moisture_mean",
    "hot_days_30c",
    "actual_et_mm"
]

for column in numeric_columns:
    print(
        column,
        "| min:",
        df[column].min(),
        "| max:",
        df[column].max()
    )

print("\nNonsense / invalid value checks:")

checks = {
    "Invalid year": (
        ~df["year"].between(2020, 2023)
    ).sum(),

    "Yield <= 0": (
        df["yield_bu_acre"] <= 0
    ).sum(),

    "CV below 0": (
        df["cv_percent"] < 0
    ).sum(),

    "CV above 100": (
        df["cv_percent"] > 100
    ).sum(),

    "Negative precipitation": (
        df["precip_total_mm"] < 0
    ).sum(),

    "Negative solar radiation": (
        df["solar_radiation_total"] < 0
    ).sum(),

    "Negative ET0": (
        df["et0_total_mm"] < 0
    ).sum(),

    "Negative actual ET": (
        df["actual_et_mm"] < 0
    ).sum(),

    "Soil moisture below 0": (
        df["soil_moisture_mean"] < 0
    ).sum(),

    "Soil moisture above 1": (
        df["soil_moisture_mean"] > 1
    ).sum(),

    "Hot days below 0": (
        df["hot_days_30c"] < 0
    ).sum(),

    "Hot days greater than season": (
        df["hot_days_30c"]
        > df["season_days"]
    ).sum(),

    "Season not equal to 183 days": (
        df["season_days"] != 183
    ).sum(),

    "OpenET months not equal to 6": (
        df["openet_months"] != 6
    ).sum(),

    "Valid ET months not equal to 6": (
        df["valid_et_months"] != 6
    ).sum(),

    "Temperature order problem": (
        (df["temp_min_c"] > df["temp_mean_c"])
        |
        (df["temp_mean_c"] > df["temp_max_c"])
    ).sum()
}

for check_name, count in checks.items():
    print(check_name, ":", count)

print("\nIQR outlier analysis:")

outlier_columns = [
    "yield_bu_acre",
    "cv_percent",
    "temp_mean_c",
    "temp_max_c",
    "temp_min_c",
    "precip_total_mm",
    "solar_radiation_total",
    "et0_total_mm",
    "soil_moisture_mean",
    "hot_days_30c",
    "actual_et_mm"
]

for column in outlier_columns:

    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = df[
        (df[column] < lower_bound)
        |
        (df[column] > upper_bound)
    ]

    print(
        "\n",
        column,
        "| lower:",
        round(lower_bound, 3),
        "| upper:",
        round(upper_bound, 3),
        "| outliers:",
        len(outliers)
    )

    if not outliers.empty:
        print(
            outliers[
                [
                    "year",
                    "county_name",
                    column
                ]
            ].to_string(index=False)
        )