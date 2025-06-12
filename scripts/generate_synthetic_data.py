import pandas as pd
import numpy as np

def generate_data(start_date='2024-01-01', end_date='2024-06-30', seed=42, output_path='data/ecommerce_campaign_data.csv'):
    np.random.seed(seed)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    channels = ['Google Ads', 'Facebook Ads', 'Email', 'Instagram', 'LinkedIn']
    data = []
    for date in date_range:
        for idx, channel in enumerate(channels):
            impressions = np.random.poisson(lam=1000 + 50 * idx)
            clicks = np.random.binomial(impressions, p=0.05)
            cpc = np.random.uniform(0.5, 2.0) if channel != 'Email' else 0.1
            spend = clicks * cpc
            base_cr = 0.02 + 0.005 * idx
            conversions = np.random.binomial(clicks, p=min(base_cr, 0.3))
            aov = np.random.uniform(50, 150)
            revenue = conversions * aov
            data.append({
                'date': date,
                'channel': channel,
                'impressions': impressions,
                'clicks': clicks,
                'spend': round(spend, 2),
                'conversions': conversions,
                'revenue': round(revenue, 2)
            })
    df = pd.DataFrame(data)
    df['ctr'] = df['clicks'] / df['impressions']
    df['conversion_rate'] = df['conversions'] / df['clicks'].replace(0, pd.NA)
    df['cpc'] = df['spend'] / df['clicks'].replace(0, pd.NA)
    df['cpa'] = df['spend'] / df['conversions'].replace(0, pd.NA)
    df['roi'] = (df['revenue'] - df['spend']) / df['spend'].replace(0, pd.NA)
    df.to_csv(output_path, index=False)
    print(f"Synthetic data saved to {output_path}")

if __name__ == "__main__":
    generate_data()
