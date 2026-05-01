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
# 📊 MONTHLY KPI
# -------------------------------

monthly = df.groupby(['hotel', 'year', 'month']).agg({
    'adr': 'mean',
    'is_occupied': 'mean'
}).reset_index()

# RevPAR
monthly['revpar'] = monthly['adr'] * monthly['is_occupied']

# -------------------------------
# 🏨 CREATE HOTEL TIERS (Proxy)
# -------------------------------

def classify_tier(adr):
    if adr < 80:
        return "Budget"
    elif adr < 150:
        return "Midscale"
    else:
        return "Upscale"

monthly['tier'] = monthly['adr'].apply(classify_tier)

# -------------------------------
# 📦 BOX PLOT
# -------------------------------

plt.figure(figsize=(8,6))

sns.boxplot(
    data=monthly,
    x='tier',
    y='revpar'
)

plt.title("RevPAR Distribution by Hotel Tier")
plt.xlabel("Hotel Tier")
plt.ylabel("RevPAR")

plt.show()