import pandas as pd

# 📂 Load your file (change name if needed)
file_path = r"C:\Users\HP\Music\new project\#3 — STR  CoStar\hotel_bookings.csv"

df = pd.read_csv(file_path)

# -------------------------------
# 🧹 DATA PREPARATION
# -------------------------------

# Total nights stayed
df['total_nights'] = df['stays_in_week_nights'] + df['stays_in_weekend_nights']

# Occupancy flag (1 = occupied, 0 = not occupied)
df['is_occupied'] = df['is_canceled'].apply(lambda x: 0 if x == 1 else 1)

# -------------------------------
# 📊 KPI CALCULATIONS
# -------------------------------

# Occupancy Rate
occupancy_rate = df['is_occupied'].mean()

# ADR (only non-cancelled bookings)
adr = df[df['is_canceled'] == 0]['adr'].mean()

# RevPAR
revpar = adr * occupancy_rate

# -------------------------------
# 📈 RESULTS
# -------------------------------

print("\n📊 HOTEL PERFORMANCE METRICS")
print("-----------------------------")
print(f"Occupancy Rate: {occupancy_rate:.2%}")
print(f"ADR (Average Daily Rate): ₹{adr:.2f}")
print(f"RevPAR: ₹{revpar:.2f}")