import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 📂 Load dataset
file_path = r"C:\Users\HP\Music\new project\#3 — STR  CoStar\hotel_bookings.csv"
df = pd.read_csv(file_path)

# -------------------------------
# 🧹 DATA PREP
# -------------------------------

# Remove cancelled bookings
df = df[df['is_canceled'] == 0]

# Create proper date
month_map = {
    'January':1, 'February':2, 'March':3, 'April':4,
    'May':5, 'June':6, 'July':7, 'August':8,
    'September':9, 'October':10, 'November':11, 'December':12
}

df['month'] = df['arrival_date_month'].map(month_map)

df['date'] = pd.to_datetime(
    df['arrival_date_year'].astype(str) + '-' +
    df['month'].astype(str) + '-01'
)

# Day of week
df['day_of_week'] = df['date'].dt.day_name()

# Occupancy flag
df['is_occupied'] = 1

# -------------------------------
# 📊 AGGREGATION
# -------------------------------

dow_perf = df.groupby('day_of_week').agg({
    'adr': 'mean',
    'is_occupied': 'mean'
}).reset_index()

# RevPAR
dow_perf['revpar'] = dow_perf['adr'] * dow_perf['is_occupied']

# Correct order of days
order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
dow_perf['day_of_week'] = pd.Categorical(dow_perf['day_of_week'], categories=order, ordered=True)
dow_perf = dow_perf.sort_values('day_of_week')

print(dow_perf)

# -------------------------------
# 📈 BAR CHART
# -------------------------------

plt.figure(figsize=(10,5))

sns.barplot(data=dow_perf, x='day_of_week', y='revpar')

plt.title("RevPAR by Day of Week")
plt.xlabel("Day of Week")
plt.ylabel("RevPAR")

plt.show()