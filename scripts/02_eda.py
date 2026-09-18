"""Exploratory Data Analysis"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/traffic_clean.csv", parse_dates=["date_time"])

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

# Hourly pattern
hourly = df.groupby("hour")["traffic_volume"].mean()
axes[0,0].plot(hourly.index, hourly.values, marker='o')
axes[0,0].set_title("Average Traffic Volume by Hour of Day")
axes[0,0].set_xlabel("Hour"); axes[0,0].set_ylabel("Avg Volume")

# Day of week pattern
dow_labels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
dow = df.groupby("day_of_week")["traffic_volume"].mean()
axes[0,1].bar(dow_labels, dow.values)
axes[0,1].set_title("Average Traffic Volume by Day of Week")

# Weather impact
weather_avg = df.groupby("weather_main")["traffic_volume"].mean().sort_values(ascending=False)
axes[1,0].barh(weather_avg.index, weather_avg.values)
axes[1,0].set_title("Average Traffic Volume by Weather Condition")

# Distribution
axes[1,1].hist(df["traffic_volume"], bins=50)
axes[1,1].set_title("Traffic Volume Distribution")
axes[1,1].set_xlabel("Volume")

plt.tight_layout()
plt.savefig("figures/eda_overview.png", dpi=120)
print("Saved figures/eda_overview.png")

print("\nHourly averages:\n", hourly.round(0))
print("\nWeekday vs Weekend avg:", df.groupby("is_weekend")["traffic_volume"].mean().to_dict())
print("\nHoliday vs non-holiday avg:", df.groupby("is_holiday")["traffic_volume"].mean().to_dict())
