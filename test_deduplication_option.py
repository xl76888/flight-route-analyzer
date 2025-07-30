from data_cleaner import clean_route_data
from fix_parser import parse_excel_route_data
import pandas as pd

# 解析原始数据
data = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
print(f'解析后原始记录数: {len(data)}')

# 测试不去重的情况
print("\n=== 测试不去重选项 ===")
cleaned_no_dedup = clean_route_data(data, enable_deduplication=False)
print(f'不去重后记录数: {len(cleaned_no_dedup)}')

# 测试去重的情况
print("\n=== 测试去重选项 ===")
cleaned_with_dedup = clean_route_data(data, enable_deduplication=True)
print(f'去重后记录数: {len(cleaned_with_dedup)}')

# 统计航司数量
print(f"\n=== 航司数量对比 ===")
print(f'不去重时航司数: {len(cleaned_no_dedup["airline"].unique())}')
print(f'去重时航司数: {len(cleaned_with_dedup["airline"].unique())}')

# 显示航司列表
print(f"\n=== 航司列表 ===")
airlines_no_dedup = sorted(cleaned_no_dedup['airline'].unique())
airlines_with_dedup = sorted(cleaned_with_dedup['airline'].unique())
print(f'不去重航司: {", ".join(airlines_no_dedup)}')
print(f'去重航司: {", ".join(airlines_with_dedup)}')