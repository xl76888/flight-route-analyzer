import pandas as pd
from parser import load_data
import glob

# 加载所有数据
files = glob.glob('data/*.xlsx') + glob.glob('data/*.csv')
df = load_data(files)

print(f'总航线数: {len(df)}')

# 检查中转航线（支持多种分隔符）
transit_separators = ['-', '—', '→', '>']
transit_condition = df['origin'].str.contains('|'.join(transit_separators), na=False) | df['destination'].str.contains('|'.join(transit_separators), na=False)
transit_routes = df[transit_condition]

print(f'中转航线数: {len(transit_routes)}')
print(f'中转航线比例: {len(transit_routes)/len(df)*100:.2f}%')

if len(transit_routes) > 0:
    print('\n中转航线样本:')
    print(transit_routes[['airline', 'origin', 'destination']].head(10).to_string())
    
    print('\n中转航线航司分布:')
    print(transit_routes['airline'].value_counts().head(10))
    
    print('\n各分隔符使用情况:')
    for sep in transit_separators:
        sep_count = (df['origin'].str.contains(sep, na=False) | df['destination'].str.contains(sep, na=False)).sum()
        print(f'  使用 "{sep}" 分隔符: {sep_count} 条航线')
    
    print('\n中转航线详细分析:')
    for idx, row in transit_routes.head(5).iterrows():
        print(f'  {row["airline"]}: {row["origin"]} → {row["destination"]}')
else:
    print('\n没有发现中转航线')
    
    # 检查是否有其他可能的中转标识
    print('\n检查其他可能的中转标识:')
    potential_transit = df[df['origin'].str.contains('经|via|VIA|中转', na=False) | df['destination'].str.contains('经|via|VIA|中转', na=False)]
    print(f'包含"经/via/中转"的航线: {len(potential_transit)} 条')
    
    if len(potential_transit) > 0:
        print('样本:')
        print(potential_transit[['airline', 'origin', 'destination']].head(5).to_string())

print('\n各航司航线数量分布:')
print(df['airline'].value_counts().head(15))