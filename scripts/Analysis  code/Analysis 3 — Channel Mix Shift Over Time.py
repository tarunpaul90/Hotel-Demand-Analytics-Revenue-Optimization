import pandas as pd
import matplotlib.pyplot as plt

# 📂 Load dataset
file_path = r"C:\Users\HP\Music\new project\#3 — STR  CoStar\hotel_bookings.csv"
df = pd.read_csv(file_path)

# -------------------------------
# 🧹 DATA PREP
# -------------------------------

# Convert month name → number
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
# 📊 CHANNEL MIX CALCULATION
# -------------------------------

# Count bookings per channel per month
channel_trend = df.groupby(
    [df['date'].dt.to_period('M'), 'distribution_channel']
).size().reset_index(name='bookings')

# Convert to percentage share
channel_pivot = channel_trend.pivot(
    index='date',
    columns='distribution_channel',
    values='bookings'
).fillna(0)

channel_pct = channel_pivot.div(channel_pivot.sum(axis=1), axis=0)

# Convert index back to timestamp
channel_pct.index = channel_pct.index.to_timestamp()

# -------------------------------
# 📈 PLOT (STACKED AREA CHART)
# -------------------------------

plt.figure(figsize=(10,6))

channel_pct.plot(kind='area', stacked=True)

plt.title("Channel Mix Shift Over Time")
plt.xlabel("Date")
plt.ylabel("Percentage Share")
plt.legend(title="Channel", bbox_to_anchor=(1.05, 1))

plt.tight_layout()
plt.show()