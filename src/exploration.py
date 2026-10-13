import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv(
    "data/processed/final_dataset.csv",
    dtype={"county_fips": str}
)

os.makedirs(
    "figures",
    exist_ok=True
)

yield_data = df["yield_bu_acre"]

print("Yield summary:")
print(yield_data.describe())

print("\nMedian yield:")
print(yield_data.median())

plt.figure(
    figsize=(8, 5)
)

plt.hist(
    yield_data,
    bins=10,
    edgecolor="black"
)

plt.title(
    "Distribution of Idaho Spring Wheat Yield, 2020-2023"
)

plt.xlabel(
    "Yield (Bushels per Acre)"
)

plt.ylabel(
    "Number of County-Year Observations"
)

plt.tight_layout()

plt.savefig(
    "figures/yield_distribution.png",
    dpi=300
)

plt.show()


x = df["precip_total_mm"]
y = df["yield_bu_acre"]

correlation = x.corr(y)

print("\nPrecipitation vs. yield correlation:")
print(correlation)

slope, intercept = np.polyfit(
    x,
    y,
    1
)

regression_line = slope * x + intercept

plt.figure(
    figsize=(8, 5)
)

plt.scatter(
    x,
    y
)

plt.plot(
    x,
    regression_line
)

plt.title(
    "Growing-Season Precipitation vs. Spring Wheat Yield"
)

plt.xlabel(
    "April-September Precipitation (mm)"
)

plt.ylabel(
    "Yield (Bushels per Acre)"
)

plt.tight_layout()

plt.savefig(
    "figures/precipitation_vs_yield.png",
    dpi=300
)

plt.show()

x = df["actual_et_mm"]
y = df["yield_bu_acre"]

correlation = x.corr(y)

print("\nActual ET vs. yield correlation:")
print(correlation)

slope, intercept = np.polyfit(
    x,
    y,
    1
)

regression_line = slope * x + intercept

plt.figure(
    figsize=(8, 5)
)

plt.scatter(
    x,
    y
)

plt.plot(
    x,
    regression_line
)

plt.title(
    "Actual Evapotranspiration vs. Spring Wheat Yield"
)

plt.xlabel(
    "April-September Actual ET (mm)"
)

plt.ylabel(
    "Yield (Bushels per Acre)"
)

plt.tight_layout()

plt.savefig(
    "figures/actual_et_vs_yield.png",
    dpi=300
)

plt.show()

correlation_columns = [
    "yield_bu_acre",
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

correlation_matrix = df[
    correlation_columns
].corr()

print("\nCorrelation matrix:")
print(correlation_matrix)

print("\nCorrelations with wheat yield:")

yield_correlations = (
    correlation_matrix["yield_bu_acre"]
    .drop("yield_bu_acre")
    .sort_values(
        key=abs,
        ascending=False
    )
)

print(yield_correlations)

plt.figure(
    figsize=(10, 8)
)

image = plt.imshow(
    correlation_matrix,
    vmin=-1,
    vmax=1,
    aspect="auto"
)

plt.colorbar(
    image,
    label="Pearson Correlation"
)

plt.xticks(
    range(len(correlation_columns)),
    correlation_columns,
    rotation=45,
    ha="right"
)

plt.yticks(
    range(len(correlation_columns)),
    correlation_columns
)

for row in range(len(correlation_columns)):
    for column in range(len(correlation_columns)):
        value = correlation_matrix.iloc[
            row,
            column
        ]

        plt.text(
            column,
            row,
            f"{value:.2f}",
            ha="center",
            va="center",
            fontsize=8
        )

plt.title(
    "Correlation Matrix of Wheat Yield and Environmental Features"
)

plt.tight_layout()

plt.savefig(
    "figures/correlation_matrix.png",
    dpi=300
)

plt.show()