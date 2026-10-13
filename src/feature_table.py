import pandas as pd

df = pd.read_csv(
    "data/processed/final_dataset.csv",
    dtype={"county_fips": str}
)

rows = [
    {
        "Feature / Description": "year - Calendar year of the wheat-growing season",
        "Variable Type": "Numeric, discrete",
        "Missing Data": "0",
        "Outliers / Nonsense": "None"
    },
    {
        "Feature / Description": "county_name - Idaho county name",
        "Variable Type": "Categorical, nominal",
        "Missing Data": "0",
        "Outliers / Nonsense": "None"
    },
    {
        "Feature / Description": "county_fips - Five-digit county identifier",
        "Variable Type": "Categorical identifier",
        "Missing Data": "0",
        "Outliers / Nonsense": "None"
    },
    {
        "Feature / Description": "asd_desc - USDA agricultural statistics district",
        "Variable Type": "Categorical, nominal",
        "Missing Data": "0",
        "Outliers / Nonsense": "None"
    },
    {
        "Feature / Description": "yield_bu_acre - Spring wheat yield in bushels per acre; outcome variable",
        "Variable Type": "Numeric, continuous",
        "Missing Data": "0",
        "Outliers / Nonsense": "No IQR outliers; no invalid values"
    },
    {
        "Feature / Description": "unit_desc - Unit used for wheat yield",
        "Variable Type": "Categorical, constant",
        "Missing Data": "0",
        "Outliers / Nonsense": "None; all values are BU / ACRE"
    },
    {
        "Feature / Description": "cv_percent - USDA coefficient of variation for the yield estimate",
        "Variable Type": "Numeric, continuous",
        "Missing Data": "0",
        "Outliers / Nonsense": "5 IQR outliers; no invalid values"
    },
    {
        "Feature / Description": "temp_mean_c - Mean April-September air temperature",
        "Variable Type": "Numeric, continuous",
        "Missing Data": "0",
        "Outliers / Nonsense": "No IQR outliers; no invalid values"
    },
    {
        "Feature / Description": "temp_max_c - Highest daily maximum temperature during the season",
        "Variable Type": "Numeric, continuous",
        "Missing Data": "0",
        "Outliers / Nonsense": "No IQR outliers; no invalid values"
    },
    {
        "Feature / Description": "temp_min_c - Lowest daily minimum temperature during the season",
        "Variable Type": "Numeric, continuous",
        "Missing Data": "0",
        "Outliers / Nonsense": "No IQR outliers; no invalid values"
    },
    {
        "Feature / Description": "precip_total_mm - Total April-September precipitation",
        "Variable Type": "Numeric, continuous",
        "Missing Data": "0",
        "Outliers / Nonsense": "3 high IQR outliers; physically plausible"
    },
    {
        "Feature / Description": "solar_radiation_total - Total growing-season shortwave solar radiation",
        "Variable Type": "Numeric, continuous",
        "Missing Data": "0",
        "Outliers / Nonsense": "5 low IQR outliers; physically plausible"
    },
    {
        "Feature / Description": "et0_total_mm - Total reference evapotranspiration from Open-Meteo",
        "Variable Type": "Numeric, continuous",
        "Missing Data": "0",
        "Outliers / Nonsense": "No IQR outliers; no invalid values"
    },
    {
        "Feature / Description": "soil_moisture_mean - Mean 0-7 cm soil moisture during the growing season",
        "Variable Type": "Numeric, continuous",
        "Missing Data": "0",
        "Outliers / Nonsense": "No IQR outliers; all values between 0 and 1"
    },
    {
        "Feature / Description": "hot_days_30c - Number of days with maximum temperature >= 30 C",
        "Variable Type": "Numeric, discrete count",
        "Missing Data": "0",
        "Outliers / Nonsense": "No IQR outliers; all counts valid"
    },
    {
        "Feature / Description": "season_days - Number of days included in the April-September weather window",
        "Variable Type": "Numeric, discrete count",
        "Missing Data": "0",
        "Outliers / Nonsense": "None; all values equal 183"
    },
    {
        "Feature / Description": "actual_et_mm - April-September actual evapotranspiration from OpenET",
        "Variable Type": "Numeric, continuous",
        "Missing Data": "0",
        "Outliers / Nonsense": "No IQR outliers; no invalid values"
    },
    {
        "Feature / Description": "openet_months - Number of OpenET months included",
        "Variable Type": "Numeric, discrete count",
        "Missing Data": "0",
        "Outliers / Nonsense": "None; all values equal 6"
    },
    {
        "Feature / Description": "valid_et_months - Number of valid OpenET monthly ET values",
        "Variable Type": "Numeric, discrete count",
        "Missing Data": "0",
        "Outliers / Nonsense": "None; all values equal 6"
    },
    {
        "Feature / Description": "openet_point_latitude - Latitude used for the OpenET county representative point",
        "Variable Type": "Numeric coordinate",
        "Missing Data": "0",
        "Outliers / Nonsense": "No invalid coordinate values"
    },
    {
        "Feature / Description": "openet_point_longitude - Longitude used for the OpenET county representative point",
        "Variable Type": "Numeric coordinate",
        "Missing Data": "0",
        "Outliers / Nonsense": "No invalid coordinate values"
    }
]

feature_table = pd.DataFrame(rows)

feature_table.to_csv(
    "data/processed/feature_table.csv",
    index=False
)

print(feature_table.to_string(index=False))

print(
    "\nFeature table saved to: "
    "data/processed/feature_table.csv"
)