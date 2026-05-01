import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv(r"C:\Users\HP\Music\new project\#3 — STR  CoStar\hotel_bookings.csv")

# Remove cancelled
df = df[df['is_canceled'] == 0]

# Occupancy
df['is_occupied'] = 1

# Group by segment
segment_perf = df.groupby('market_segment').agg({
    'adr': 'mean',
    'is_occupied': 'mean'
}).reset_index()

# RevPAR
segment_perf['revpar'] = segment_perf['adr'] * segment_perf['is_occupied']

print(segment_perf)

# Plot
plt.figure(figsize=(8,5))
sns.barplot(data=segment_perf, x='market_segment', y='revpar')

plt.title("RevPAR by Market Segment")
plt.xticks(rotation=45)
plt.show()