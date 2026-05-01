import pandas as pd
import matplotlib.pyplot as plt

# 📂 Load dataset
file_path = r"C:\Users\HP\Music\new project\#3 — STR  CoStar\hotel_bookings.csv"
df = pd.read_csv(file_path)

# -------------------------------
# 🧹 DATA PREPARATION
# -------------------------------

# Occupancy flag
df['is_occupied'] = df['is_canceled'].apply(lambda x: 0 if x == 1 else 1)

# Convert month name to number (IMPORTANT FIX)
month_map = {
    'January':1, 'February':2, 'March':3, 'April':4,
    'May':5, 'June':6, 'July':7, 'August':8,
    'September':9, 'October':10, 'November':11, 'December':12
}

df['month_num'] = df['arrival_date_month'].map(month_map)

# Create proper date
df['date'] = pd.to_datetime(
    df['arrival_date_year'].astype(str) + '-' +
    df['month_num'].astype(str) + '-01'
)

# -------------------------------
# 📊 AGGREGATION (Monthly)
# -------------------------------

monthly = df.groupby(df['date'].dt.to_period('M')).agg({
    'adr': 'mean',
    'is_occupied': 'mean'
}).reset_index()

monthly['date'] = monthly['date'].dt.to_timestamp()

# -------------------------------
# 📈 SCATTER PLOT
# -------------------------------

plt.figure(figsize=(8,6))

plt.scatter(monthly['is_occupied'], monthly['adr'])

# Labels
plt.xlabel("Occupancy Rate")
plt.ylabel("ADR (Average Daily Rate)")
plt.title("ADR vs Occupancy Analysis")

# Annotate points (month labels)
for i in range(len(monthly)):
    plt.text(monthly['is_occupied'][i],
             monthly['adr'][i],
             str(monthly['date'][i].strftime('%Y-%m')),
             fontsize=8)

plt.grid()
plt.show()