import pandas as pd
import matplotlib.pyplot as plt

# 📂 Load dataset
file_path = r"C:\Users\HP\Music\new project\#3 — STR  CoStar\hotel_bookings.csv"
df = pd.read_csv(file_path)

# -------------------------------
# 🧹 DATA PREP
# -------------------------------

# Remove cancelled bookings (IMPORTANT)
df = df[df['is_canceled'] == 0]

# -------------------------------
# 🧮 CREATE LEAD TIME BUCKETS
# -------------------------------

def lead_category(days):
    if days <= 3:
        return "0-3d"
    elif days <= 7:
        return "4-7d"
    elif days <= 14:
        return "8-14d"
    elif days <= 28:
        return "15-28d"
    elif days <= 60:
        return "29-60d"
    else:
        return "60d+"

df['lead_bucket'] = df['lead_time'].apply(lead_category)

# -------------------------------
# 📊 AGGREGATION
# -------------------------------

lead_analysis = df.groupby('lead_bucket')['adr'].mean().reset_index()

# Sort in correct order
order = ["0-3d", "4-7d", "8-14d", "15-28d", "29-60d", "60d+"]
lead_analysis['lead_bucket'] = pd.Categorical(lead_analysis['lead_bucket'], categories=order, ordered=True)
lead_analysis = lead_analysis.sort_values('lead_bucket')

print(lead_analysis)

# -------------------------------
# 📈 LINE CHART
# -------------------------------

plt.figure(figsize=(8,5))

plt.plot(lead_analysis['lead_bucket'], lead_analysis['adr'], marker='o')

plt.title("ADR vs Booking Lead Time")
plt.xlabel("Booking Window")
plt.ylabel("Average ADR")

plt.grid()
plt.show()