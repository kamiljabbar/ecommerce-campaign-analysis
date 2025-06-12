import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Load data
df = pd.read_csv('data/ecommerce_campaign_data.csv', parse_dates=['date'])
# Compute metrics if missing
df['ctr'] = df['clicks'] / df['impressions']
df['conversion_rate'] = df['conversions'] / df['clicks'].replace(0, np.nan)
df['cpc'] = df['spend'] / df['clicks'].replace(0, np.nan)
df['cpa'] = df['spend'] / df['conversions'].replace(0, np.nan)
df['roi'] = (df['revenue'] - df['spend']) / df['spend'].replace(0, np.nan)

os.makedirs('dashboards', exist_ok=True)

# 1. Daily Spend vs Revenue with 7-day average
daily = df.groupby('date').agg({'spend':'sum','revenue':'sum'}).reset_index()
daily['spend_7d'] = daily['spend'].rolling(7, min_periods=1).mean()
daily['revenue_7d'] = daily['revenue'].rolling(7, min_periods=1).mean()
plt.figure(figsize=(10,5))
plt.plot(daily['date'], daily['spend'], label='Daily Spend')
plt.plot(daily['date'], daily['revenue'], label='Daily Revenue')
plt.plot(daily['date'], daily['spend_7d'], linestyle='--', label='7-day Avg Spend')
plt.plot(daily['date'], daily['revenue_7d'], linestyle='--', label='7-day Avg Revenue')
plt.xlabel('Date')
plt.ylabel('Amount')
plt.title('Daily Spend vs Revenue with 7-day Rolling Average')
plt.legend()
plt.tight_layout()
plt.savefig('dashboards/daily_spend_vs_revenue.png')
plt.close()

# 2. Channel performance summary image (bar charts for ROI, CTR, conversion_rate, cpa)
chan = df.groupby('channel').agg({'impressions':'sum','clicks':'sum','conversions':'sum','spend':'sum','revenue':'sum'}).reset_index()
chan['ctr'] = chan['clicks'] / chan['impressions']
chan['conversion_rate'] = chan['conversions'] / chan['clicks'].replace(0, np.nan)
chan['cpc'] = chan['spend'] / chan['clicks'].replace(0, np.nan)
chan['cpa'] = chan['spend'] / chan['conversions'].replace(0, np.nan)
chan['roi'] = (chan['revenue'] - chan['spend']) / chan['spend'].replace(0, np.nan)

plt.figure(figsize=(10,5))
plt.bar(chan['channel'], chan['roi'])
plt.xlabel('Channel'); plt.ylabel('ROI'); plt.title('Overall ROI by Channel'); plt.xticks(rotation=45); plt.tight_layout()
plt.savefig('dashboards/roi_by_channel.png'); plt.close()

plt.figure(figsize=(10,5))
plt.bar(chan['channel'], chan['ctr'])
plt.xlabel('Channel'); plt.ylabel('CTR'); plt.title('Overall CTR by Channel'); plt.xticks(rotation=45); plt.tight_layout()
plt.savefig('dashboards/ctr_by_channel.png'); plt.close()

plt.figure(figsize=(10,5))
plt.bar(chan['channel'], chan['conversion_rate'])
plt.xlabel('Channel'); plt.ylabel('Conversion Rate'); plt.title('Overall Conversion Rate by Channel'); plt.xticks(rotation=45); plt.tight_layout()
plt.savefig('dashboards/conversion_rate_by_channel.png'); plt.close()

plt.figure(figsize=(10,5))
plt.bar(chan['channel'], chan['cpa'])
plt.xlabel('Channel'); plt.ylabel('CPA'); plt.title('Overall CPA by Channel'); plt.xticks(rotation=45); plt.tight_layout()
plt.savefig('dashboards/cpa_by_channel.png'); plt.close()

# 3. Monthly revenue by channel
df['month'] = df['date'].dt.to_period('M').dt.to_timestamp()
monthly = df.groupby(['month','channel']).agg({'revenue':'sum','spend':'sum'}).reset_index()
plt.figure(figsize=(10,6))
for ch in monthly['channel'].unique():
    subset = monthly[monthly['channel']==ch]
    plt.plot(subset['month'], subset['revenue'], marker='o', label=ch)
plt.xlabel('Month'); plt.ylabel('Revenue'); plt.title('Monthly Revenue by Channel'); plt.xticks(rotation=45); plt.legend(); plt.tight_layout()
plt.savefig('dashboards/monthly_revenue_by_channel.png'); plt.close()

# 4. Monthly spend stacked area
pivot_spend = monthly.pivot(index='month', columns='channel', values='spend').fillna(0)
plt.figure(figsize=(10,6))
plt.stackplot(pivot_spend.index, [pivot_spend[c] for c in pivot_spend.columns], labels=pivot_spend.columns)
plt.xlabel('Month'); plt.ylabel('Spend'); plt.title('Monthly Spend by Channel (Stacked Area)'); plt.legend(loc='upper left', bbox_to_anchor=(1,1)); plt.xticks(rotation=45); plt.tight_layout()
plt.savefig('dashboards/monthly_spend_stacked_area.png'); plt.close()

# 5. Funnel normalized
fdata = chan.set_index('channel')[['impressions','clicks','conversions','revenue']]
fn = fdata.div(fdata['impressions'], axis=0)[['impressions','clicks','conversions','revenue']]
stages = ['impressions','clicks','conversions','revenue']
x = np.arange(len(fn))
height = 0.15
plt.figure(figsize=(12,6))
for i, stage in enumerate(stages):
    plt.barh(x + i*height, fn[stage], height=height, label=stage.capitalize())
plt.yticks(x + height*1.5, fn.index); plt.xlabel('Normalized Proportion (Impressions=1)'); plt.title('Funnel Drop-Off by Channel (Normalized)'); plt.legend(loc='upper right'); plt.tight_layout()
plt.savefig('dashboards/funnel_normalized_by_channel.png'); plt.close()

# 6. Monthly ROI heatmap
roi_data = monthly.copy()
roi_data['roi'] = (roi_data['revenue'] - roi_data['spend']) / roi_data['spend'].replace(0, np.nan)
pivot_roi = roi_data.pivot(index='channel', columns='month', values='roi').fillna(0)
plt.figure(figsize=(10,6))
im = plt.imshow(pivot_roi.values, aspect='auto', interpolation='nearest')
plt.colorbar(im, label='ROI')
plt.yticks(ticks=np.arange(len(pivot_roi.index)), labels=pivot_roi.index)
plt.xticks(ticks=np.arange(len(pivot_roi.columns)), labels=[d.strftime('%Y-%m') for d in pivot_roi.columns], rotation=45)
plt.title('Monthly ROI Heatmap by Channel'); plt.tight_layout()
plt.savefig('dashboards/monthly_roi_heatmap.png'); plt.close()

# 7. Additional charts: cumulative and scatter and pareto
# Cumulative spend vs revenue
daily = df.groupby('date').agg({'spend':'sum','revenue':'sum'}).reset_index()
daily['cum_spend'] = daily['spend'].cumsum()
daily['cum_revenue'] = daily['revenue'].cumsum()
plt.figure(figsize=(10,5))
plt.plot(daily['date'], daily['cum_spend'], label='Cumulative Spend')
plt.plot(daily['date'], daily['cum_revenue'], label='Cumulative Revenue')
plt.xlabel('Date'); plt.ylabel('Cumulative Amount'); plt.title('Cumulative Spend vs Revenue'); plt.legend(); plt.xticks(rotation=45); plt.tight_layout()
plt.savefig('dashboards/cumulative_spend_revenue.png'); plt.close()

# CTR vs Conversion scatter
plt.figure(figsize=(8,6))
sizes = chan['spend'] / 10
plt.scatter(chan['ctr'], chan['conversion_rate'], s=sizes)
for _, row in chan.iterrows():
    plt.text(row['ctr'], row['conversion_rate'], row['channel'], fontsize=9, ha='center', va='center')
plt.xlabel('CTR'); plt.ylabel('Conversion Rate'); plt.title('CTR vs Conversion Rate by Channel (bubble size ~ spend)'); plt.tight_layout()
plt.savefig('dashboards/ctr_vs_conversion_scatter.png'); plt.close()

# Pareto revenue
rev_sorted = chan.sort_values('revenue', ascending=False).reset_index(drop=True)
rev_sorted['cum_rev'] = rev_sorted['revenue'].cumsum()
rev_sorted['cum_rev_pct'] = rev_sorted['cum_rev'] / rev_sorted['revenue'].sum() * 100
fig, ax1 = plt.subplots(figsize=(8,5))
ax2 = ax1.twinx()
ax1.bar(rev_sorted['channel'], rev_sorted['revenue'])
ax2.plot(rev_sorted['channel'], rev_sorted['cum_rev_pct'], color='black', marker='o', linestyle='--')
ax1.set_xlabel('Channel'); ax1.set_ylabel('Revenue'); ax2.set_ylabel('Cumulative % of Revenue'); ax1.set_title('Pareto Chart: Revenue by Channel'); plt.xticks(rotation=45); plt.tight_layout()
plt.savefig('dashboards/pareto_revenue_by_channel.png'); plt.close()
