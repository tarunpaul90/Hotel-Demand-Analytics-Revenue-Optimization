import pandas as pd
import matplotlib.pyplot as plt

# 📂 Load dataset
file_path = r"C:\Users\HP\Music\new project\#3 — STR  CoStar\hotel_bookings.csv"
df = pd.read_csv(file_path)

# -------------------------------
# 🧹 DATA PREP
# -------------------------------

# Remove cancelled
df = df[df['is_canceled'] == 0]

# Occupancy
df['is_occupied'] = 1

# -------------------------------
# 📊 BASE METRICS
# -------------------------------

total_revenue = df['adr'].sum()

avg_adr = df['adr'].mean()
max_adr = df['adr'].max()

# ADR compression (gap from potential)
adr_loss = (max_adr - avg_adr) * len(df)

# Occupancy loss (proxy)
occupancy_rate = df['is_occupied'].mean()
occupancy_loss = (1 - occupancy_rate) * total_revenue

# Commission loss
def commission(channel):
    return 0.15 if channel in ['TA/TO', 'GDS'] else 0

df['commission'] = df['distribution_channel'].apply(commission)
commission_loss = (df['adr'] * df['commission']).sum()

# Operating cost (assumption)
operating_cost = total_revenue * 0.4

# Net profit
net_profit = total_revenue - adr_loss - occupancy_loss - commission_loss - operating_cost

# -------------------------------
# 📊 WATERFALL DATA
# -------------------------------

labels = [
    'Total Revenue',
    'ADR Loss',
    'Occupancy Loss',
    'Commission',
    'Operating Cost',
    'Net Profit'
]

values = [
    total_revenue,
    -adr_loss,
    -occupancy_loss,
    -commission_loss,
    -operating_cost,
    net_profit
]

# -------------------------------
# 📈 PLOT WATERFALL
# -------------------------------

plt.figure(figsize=(10,5))

running_total = [values[0]]

for i in range(1, len(values)):
    running_total.append(running_total[i-1] + values[i])

plt.bar(labels, running_total)

plt.title("Profitability Waterfall Analysis")
plt.xticks(rotation=30)

plt.show()