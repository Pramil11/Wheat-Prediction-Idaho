import pandas as pd

df = pd.read_csv(
    "data/processed/final_dataset.csv",
    dtype={"county_fips": str}
)

features = [
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

target = "yield_bu_acre"

X = df[features].copy()
y = df[target].copy()

X = X.apply(
    pd.to_numeric,
    errors="coerce"
)

y = pd.to_numeric(
    y,
    errors="coerce"
)

print("Potential model:")
print("Random Forest Regression")

print("\nNumber of samples:")
print(len(X))

print("\nNumber of features:")
print(len(features))

print("\nFeature columns:")
for feature in features:
    print(feature)

print("\nOutcome variable:")
print(target)

print("\nX shape:")
print(X.shape)

print("\ny shape:")
print(y.shape)

print("\nFeature data types:")
print(X.dtypes)

print("\nMissing values in X:")
print(X.isna().sum())

print("\nTotal missing values in X:")
print(X.isna().sum().sum())

print("\nMissing values in y:")
print(y.isna().sum())

print("\nFirst 5 samples of X:")
print(X.head())

print("\nFirst 5 outcome values:")
print(y.head())

train_mask = df["year"] <= 2022
test_mask = df["year"] == 2023

X_train = X.loc[train_mask].copy()
X_test = X.loc[test_mask].copy()

y_train = y.loc[train_mask].copy()
y_test = y.loc[test_mask].copy()

print("\nTemporal split:")

print("Training years:")
print(
    sorted(
        df.loc[
            train_mask,
            "year"
        ].unique()
    )
)

print("Test year:")
print(
    sorted(
        df.loc[
            test_mask,
            "year"
        ].unique()
    )
)

print("\nX_train shape:")
print(X_train.shape)

print("\ny_train shape:")
print(y_train.shape)

print("\nX_test shape:")
print(X_test.shape)

print("\ny_test shape:")
print(y_test.shape)

model_ready_df = df[
    [
        "year",
        "county_name",
        "county_fips",
        target
    ]
    + features
].copy()

model_ready_df.to_csv(
    "data/processed/model_ready.csv",
    index=False
)

print(
    "\nModel-ready dataset saved to:"
)

print(
    "data/processed/model_ready.csv"
)