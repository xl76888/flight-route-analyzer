import pandas as pd
from parser import load_data
import glob

# 加载所有数据
files = glob.glob('data/*.xlsx') + glob.glob('data/*.csv')
df = load_data(files)

print(f'总航线数: {len(df)}')

# 筛选国货航数据
guohuo_all = df[df['airline'].str.contains('国货航', na=False)]
print(f'国货航总航线: {len(guohuo_all)}')

# 检查国货航中转航线
transit_condition = (guohuo_all['origin'].str.contains('-', na=False) | 
                    guohuo_all['destination'].str.contains('-', na=False) |
                    guohuo_all['origin'].str.contains('—', na=False) | 
                    guohuo_all['destination'].str.contains('—', na=False))

guohuo_transit = guohuo_all[transit_condition]
print(f'国货航中转航线: {len(guohuo_transit)}')

if len(guohuo_transit) > 0:
    print('\n国货航中转航线样本:')
    print(guohuo_transit[['origin', 'destination']].head(10).to_string())
    
    print('\n国货航中转航线详细信息:')
    for idx, row in guohuo_transit.head(5).iterrows():
        print(f'  {row["origin"]} → {row["destination"]}')
else:
    print('\n国货航没有中转航线')
    print('\n国货航航线样本:')
    print(guohuo_all[['origin', 'destination']].head(10).to_string())

# 检查数据来源
print('\n数据来源分析:')
print('国货航数据的文件来源分布:')
if 'source_file' in guohuo_all.columns:
    print(guohuo_all['source_file'].value_counts())
else:
    print('没有source_file字段')

# 检查是否有重复数据
print('\n重复数据检查:')
duplicates = guohuo_all.duplicated(subset=['origin', 'destination'], keep=False)
print(f'重复航线数: {duplicates.sum()}')

if duplicates.sum() > 0:
    print('重复航线样本:')
    print(guohuo_all[duplicates][['origin', 'destination']].head(10).to_string())