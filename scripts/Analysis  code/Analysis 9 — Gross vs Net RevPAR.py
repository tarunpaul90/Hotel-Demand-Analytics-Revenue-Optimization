import pandas as pd
import matplotlib.pyplot as plt

# 📂 Load dataset
file_path = r"C:\Users\HP\Music\new project\#3 — STR  CoStar\hotel_bookings.csv"
df = pd.read_csv(file_path)

# -------------------------------
# 🧹 DATA PREP
# -------------------------------

# Remove cancelled bookings
df = df[df['is_canceled'] == 0]

# Occupancy
df['is_occupied'] = 1

# Month mapping
month_map = {
    'January':1, 'February':2, 'March':3, 'April':4,
    'May':5, 'June':6, 'July':7, 'August':8,
    'September':9, 'October':10, 'November':11, 'December':12
}

df['month'] = df['arrival_date_month'].map(month_map)

# Create date
df['date'] = pd.to_datetime(
    df['arrival_date_year'].astype(str) + '-' +
    df['month'].astype(str) + '-01'
)

# -------------------------------
# 💸 COMMISSION LOGIC
# -------------------------------

def get_commission(channel):
    if channel in ['TA/TO', 'GDS']:
        return 0.15  # OTA commission
    else:
        return 0.0   # Direct / corporate

df['commission'] = df['distribution_channel'].apply(get_commission)

# -------------------------------
# 📊 CALCULATE REVENUE
# -------------------------------

# Gross revenue = ADR
df['gross_revenue'] = df['adr']

# Net revenue after commission
df['net_revenue'] = df['adr'] * (1 - df['commission'])

# -------------------------------
# 📅 MONTHLY AGGREGATION
# -------------------------------

monthly = df.groupby(df['date'].dt.to_period('M')).agg({
    'gross_revenue': 'mean',
    'net_revenue': 'mean'
}).reset_index()

monthly['date'] = monthly['date'].dt.to_timestamp()

# -------------------------------
# 📈 PLOT
# -------------------------------

plt.figure(figsize=(10,5))

plt.plot(monthly['date'], monthly['gross_revenue'], label='Gross RevPAR')
plt.plot(monthly['date'], monthly['net_revenue'], label='Net RevPAR')

plt.title("Gross vs Net RevPAR Over Time")
plt.xlabel("Date")
plt.ylabel("Revenue")

plt.legend()
plt.grid()

plt.show()
