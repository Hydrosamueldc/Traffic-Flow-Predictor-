"""
Plot every raw predictor variable against the target (traffic_volume),
to visually assess which variables carry predictive signal.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/traffic_clean.csv", parse_dates=["date_time"])

fig, axes = plt.subplots(3, 3, figsize=(16, 13))

# 1. Hour vs traffic (categorical/cyclical -> line of means)
hourly = df.groupby("hour")["traffic_volume"].mean()
axes[0,0].plot(hourly.index, hourly.values, marker='o', color='tab:blue')
axes[0,0].set_title("Hour of Day vs Traffic Volume")
axes[0,0].set_xlabel("Hour"); axes[0,0].set_ylabel("Avg Volume")

# 2. Day of week vs traffic
dow_labels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
dow = df.groupby("day_of_week")["traffic_volume"].mean()
axes[0,1].bar(dow_labels, dow.values, color='tab:blue')
axes[0,1].set_title("Day of Week vs Traffic Volume")

# 3. Month vs traffic
month_avg = df.groupby("month")["traffic_volume"].mean()
axes[0,2].plot(month_avg.index, month_avg.values, marker='o', color='tab:blue')
axes[0,2].set_title("Month vs Traffic Volume")
axes[0,2].set_xlabel("Month")

# 4. Temperature vs traffic (scatter, sampled for readability)
sample = df.sample(5000, random_state=1)
axes[1,0].scatter(sample["temp_c"], sample["traffic_volume"], alpha=0.15, s=6, color='tab:orange')
axes[1,0].set_title("Temperature (°C) vs Traffic Volume")
axes[1,0].set_xlabel("Temp (°C)")

# 5. Rain vs traffic
axes[1,1].scatter(sample["rain_1h"], sample["traffic_volume"], alpha=0.15, s=6, color='tab:orange')
axes[1,1].set_title("Rainfall (mm/hr) vs Traffic Volume")
axes[1,1].set_xlabel("Rain (mm/hr)")
axes[1,1].set_xlim(0, sample["rain_1h"].quantile(0.99))

# 6. Snow vs traffic
axes[1,2].scatter(sample["snow_1h"], sample["traffic_volume"], alpha=0.15, s=6, color='tab:orange')
axes[1,2].set_title("Snowfall (mm/hr) vs Traffic Volume")
axes[1,2].set_xlabel("Snow (mm/hr)")

# 7. Cloud cover vs traffic
axes[2,0].scatter(sample["clouds_all"], sample["traffic_volume"], alpha=0.15, s=6, color='tab:orange')
axes[2,0].set_title("Cloud Cover (%) vs Traffic Volume")
axes[2,0].set_xlabel("Cloud Cover (%)")

# 8. Weather category vs traffic
weather_avg = df.groupby("weather_main")["traffic_volume"].mean().sort_values()
axes[2,1].barh(weather_avg.index, weather_avg.values, color='tab:green')
axes[2,1].set_title("Weather Condition vs Traffic Volume")

# 9. Holiday vs traffic
hol_avg = df.groupby("is_holiday")["traffic_volume"].mean()
axes[2,2].bar(["Not Holiday", "Holiday"], hol_avg.values, color='tab:green')
axes[2,2].set_title("Holiday vs Traffic Volume")

plt.tight_layout()
plt.savefig("figures/variable_vs_target.png", dpi=120)
print("Saved figures/variable_vs_target.png")

# Print correlation of numeric variables with target for the writeup
numeric_cols = ["temp_c", "rain_1h", "snow_1h", "clouds_all", "is_holiday", "is_weekend"]
print("\nCorrelation with traffic_volume:")
print(df[numeric_cols + ["traffic_volume"]].corr()["traffic_volume"].drop("traffic_volume").sort_values())
