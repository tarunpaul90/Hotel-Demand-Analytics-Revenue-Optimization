import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 📂 Load dataset
file_path = r"C:\Users\HP\Music\new project\#3 — STR  CoStar\hotel_bookings.csv"
df = pd.read_csv(file_path)

# -------------------------------
# 🧹 DATA PREP
# -------------------------------

# Occupancy flag
df['is_occupied'] = df['is_canceled'].apply(lambda x: 0 if x == 1 else 1)

# Month mapping
month_map = {
    'January':1, 'February':2, 'March':3, 'April':4,
    'May':5, 'June':6, 'July':7, 'August':8,
    'September':9, 'October':10, 'November':11, 'December':12
}

df['month'] = df['arrival_date_month'].map(month_map)
df['year'] = df['arrival_date_year']

# -------------------------------
# 📊 KPI CALCULATION (Monthly)
# -------------------------------

monthly = df.groupby(['year', 'month']).agg({
    'adr': 'mean',
    'is_occupied': 'mean'
}).reset_index()

# RevPAR calculation
monthly['revpar'] = monthly['adr'] * monthly['is_occupied']

# -------------------------------
# 🔥 HEATMAP DATA
# -------------------------------

heatmap_data = monthly.pivot(index='year', columns='month', values='revpar')

# -------------------------------
# 📈 PLOT HEATMAP
# -------------------------------

plt.figure(figsize=(12,6))

sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".0f",
    cmap="coolwarm"
)

plt.title("Seasonality Heatmap (RevPAR)")
plt.xlabel("Month")
plt.ylabel("Year")

plt.show()