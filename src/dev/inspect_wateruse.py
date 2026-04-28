import pyreadr, json
import pandas as pd

# load time series
result = pyreadr.read_r('data/processed/water_use_data_time_series.rds')
df_time = list(result.values())[0]

# load descriptive
result = pyreadr.read_r('data/processed/water_use_data_descriptive_treated.rds')
df_desc = list(result.values())[0]

col = 'OD_ZAVL'

print(df_desc[col].describe())
print((df_desc[col] == 0).mean())
print(df_desc[col].isna().mean())

total = len(df_desc)

zero_count = (df_desc[col] == 0).sum()
na_count = df_desc[col].isna().sum()

print(f"Zeros: {zero_count} ({zero_count/total:.2%})")
print(f"NAs: {na_count} ({na_count/total:.2%})")

"""col = 'OD_P_CHL'  # adjust variable name as needed

print(df_desc[col].describe())
print((df_desc[col] == 0).mean())
print(df_desc[col].isna().mean())

total = len(df_desc)

zero_count = (df_desc[col] == 0).sum()
na_count = df_desc[col].isna().sum()

print(f"Zeros: {zero_count} ({zero_count/total:.2%})")
print(f"NAs: {na_count} ({na_count/total:.2%})")"""

# Additional checks for 0s and NAs, apply where makes sense based on variable meaning

"""print((df_time[df_time['MVM'] == 0]['MHV'] == 0).mean())
print(df_time[(df_time['MVM'] == 0) & (df_time['MHV'] != 0)].head(20))"""

"""cond_a = (
    (df_time['MVM'].notna()) &
    (df_time['MVM'] != 0) &
    (
        (df_time['MHV'] == 0) |
        (df_time['MHV'].isna())
    )
)

print(cond_a.sum())
print(df_time[cond_a].head(20))"""

"""cond_b = (
    (
        (df_time['MVM'] == 0) |
        (df_time['MVM'].isna())
    ) &
    (df_time['MHV'].notna()) &
    (df_time['MHV'] != 0)
)

print(cond_b.sum())
print(df_time[cond_b].head(20))"""

#Inspect distribution

"""import numpy as np
import matplotlib.pyplot as plt

# 1. Filter non-zero, non-NA values
df_nonzero = df_time[(df_time['MVM'].notna()) & (df_time['MVM'] > 0)].copy()

# 2. Log transform
df_nonzero['MVM_log'] = np.log1p(df_nonzero['MVM'])

# 3. Plot log distribution
df_nonzero['MVM_log'].hist(bins=100)
plt.title("Log MVM Distribution")
plt.show()

# 4. Define extreme threshold (top 0.1%)
threshold = df_nonzero['MVM'].quantile(0.999)

print(f"Threshold (99.9%): {threshold}")

# 5. Filter extreme values
df_extreme = df_nonzero[df_nonzero['MVM'] > threshold]

print(f"\nNumber of extreme rows: {len(df_extreme)}")

# 6. Inspect sample
print("\nSample extreme rows:")
print(df_extreme.head(20))

# 7. Unique IDs
unique_ids = df_extreme['ID'].nunique()
print(f"\nUnique IDs in extreme set: {unique_ids}")

# 8. Top IDs by frequency
print("\nTop IDs (frequency):")
print(df_extreme['ID'].value_counts().head(10))
print(df_extreme['MVM'].sum() / df_nonzero['MVM'].sum())
print(df_extreme.groupby('ID')['MVM'].agg(['mean', 'std']).head())
print(df_extreme[df_extreme['ID'] == '124114_VYP'].sort_values('DTM')[['DTM','MVM']])
df_extreme[['MVM', 'PML_S']].head(20)"""

#Inspect dynamic behaviour

"""# 1. Work only with valid positive values
df_nonzero = df_time[(df_time['MVM'].notna()) & (df_time['MVM'] > 0)].copy()

# 2. Total water abstraction
total_mvm = df_nonzero['MVM'].sum()

# 3. Aggregate by ID
df_by_id = df_nonzero.groupby('ID')['MVM'].sum().sort_values(ascending=False)

# 4. Compute cumulative share
df_cum = df_by_id.cumsum() / total_mvm

# 5. Check top N users
for n in [1, 5, 10, 20, 50, 100]:
    if n <= len(df_cum):
        share = df_cum.iloc[n-1]
        print(f"Top {n} users: {share:.2%} of total water use")

# 6. Optional: how many users to reach 50%, 80%, 90%
for threshold in [0.5, 0.8, 0.9]:
    n_users = (df_cum <= threshold).sum() + 1
    print(f"{threshold:.0%} of water use is reached by top {n_users} users")

df_time['DTM'] = pd.to_datetime(df_time['DTM'])
df_time['year'] = df_time['DTM'].dt.year
print(df_time[['DTM', 'year']].head())

df_cum.reset_index(drop=True).plot()
plt.title("Cumulative Water Use by Users (Ranked)")
plt.xlabel("User rank")
plt.ylabel("Cumulative share of total MVM")
plt.grid()
plt.show()"""

"""import matplotlib.pyplot as plt

df_time['DTM'] = pd.to_datetime(df_time['DTM'])
df_time['year'] = df_time['DTM'].dt.year

print(df_time[['DTM', 'year']].head())

df_yearly = df_time.groupby('year')['MVM'].sum()
print(df_yearly)

df_yearly.plot(title="Total Water Use per Year")
plt.show()

results = []

for year, df_y in df_time.groupby('year'):
    df_y = df_y[(df_y['MVM'].notna()) & (df_y['MVM'] > 0)]
    
    total = df_y['MVM'].sum()
    
    by_id = df_y.groupby('ID')['MVM'].sum().sort_values(ascending=False)
    cum = by_id.cumsum() / total
    
    top10 = cum.iloc[9] if len(cum) >= 10 else None
    top50 = cum.iloc[49] if len(cum) >= 50 else None
    
    results.append({
        'year': year,
        'top10_share': top10,
        'top50_share': top50
    })

df_concentration = pd.DataFrame(results)
print(df_concentration)

df_concentration.set_index('year')[['top10_share', 'top50_share']].plot()
plt.title("Concentration Over Time")
plt.ylabel("Share of total MVM")
plt.show()"""

"""# decomposition of water use by top users over time
import pandas as pd
import matplotlib.pyplot as plt

# 1. Prepare data
df = df_time.copy()
df = df[(df['MVM'].notna()) & (df['MVM'] > 0)]

# ensure datetime
df['DTM'] = pd.to_datetime(df['DTM'])
df['year'] = df['DTM'].dt.year

# remove broken year
df = df[df['year'] != 2009]

# 2. Compute yearly decomposition
results = []

for year, df_y in df.groupby('year'):
    
    # total
    total = df_y['MVM'].sum()
    
    # aggregate by ID
    by_id = df_y.groupby('ID')['MVM'].sum().sort_values(ascending=False)
    
    # top 10 users
    top10_ids = by_id.head(10).index
    top10_sum = by_id.head(10).sum()
    
    # rest
    rest_sum = total - top10_sum
    
    results.append({
        'year': year,
        'total': total,
        'top10': top10_sum,
        'rest': rest_sum,
        'top10_share': top10_sum / total
    })

df_decomp = pd.DataFrame(results).sort_values('year')

print(df_decomp)

#absolute decomposition
df_decomp.set_index('year')[['top10', 'rest']].plot()
plt.title("Top 10 vs Rest — Absolute Water Use")
plt.ylabel("Total MVM")
plt.show()

#share decomposition
df_decomp.set_index('year')['top10_share'].plot()
plt.title("Top 10 Share Over Time")
plt.ylabel("Share of total MVM")
plt.show()

df_norm = df_decomp.copy()
df_norm[['top10', 'rest']] = df_norm[['top10', 'rest']].div(df_norm.iloc[0][['top10', 'rest']]) * 100

# normalized decomposition
df_norm.set_index('year')[['top10', 'rest']].plot()
plt.title("Relative Change (2000 = 100)")
plt.ylabel("Index")
plt.show()"""


#OD_ examine share of water use from cooling users
"""col = 'OD_P_CHL'

# users with cooling
ids_cooling = df_desc[df_desc[col] > 0]['ID'].unique()

# total MVM
total_mvm = df_time['MVM'].sum()

# MVM from cooling users
mvm_cooling = df_time[df_time['ID'].isin(ids_cooling)]['MVM'].sum()

print("Share of MVM from cooling users:", mvm_cooling / total_mvm)"""

#Share of MVM from cooling within top users

"""col = 'OD_P_CHL'

ids_cooling = df_desc[df_desc[col] > 0]['ID'].unique()

print("Number of cooling users:", len(ids_cooling))


df_nonzero = df_time[(df_time['MVM'].notna()) & (df_time['MVM'] > 0)].copy()

df_by_id = df_nonzero.groupby('ID')['MVM'].sum().sort_values(ascending=False)

print(df_by_id.head(10))

top_n = 50  # you can change: 10, 20, 50, 100

top_ids = df_by_id.head(top_n).index

overlap = [i for i in top_ids if i in ids_cooling]

print(f"Top {top_n} users: {len(overlap)} are cooling users")
print("Overlap IDs:", overlap[:10])


df_top = df_nonzero[df_nonzero['ID'].isin(top_ids)]

total_top_mvm = df_top['MVM'].sum()

top_cooling_mvm = df_top[df_top['ID'].isin(ids_cooling)]['MVM'].sum()

print("Cooling share within top users:", top_cooling_mvm / total_top_mvm)"""


#Examine temporal patterns of cooling users
"""col = 'OD_P_CHL'
import matplotlib.pyplot as plt
# cooling users
ids_cooling = df_desc[df_desc[col] > 0]['ID']

df = df_time[df_time['ID'].isin(ids_cooling)].copy()

df['DTM'] = pd.to_datetime(df['DTM'])
df['year'] = df['DTM'].dt.year

df_yearly = df.groupby('year')['MVM'].sum()

print(df_yearly)

df_yearly.plot(title="MVM of Cooling Users per Year")
plt.show()"""

"""print(df_desc.head())
print(df_desc.columns)

print(df_time['DTM'].min(), df_time['DTM'].max())
print(df_time['ID'].nunique())
print(df_time.describe())

with open('data/processed/water_use_locations_spatial_full.json') as f:
    data = json.load(f)

print(type(data))
print(list(data.keys())[:5])"""