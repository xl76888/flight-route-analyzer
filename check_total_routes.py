from data_cleaner import clean_route_data
from fix_parser import parse_excel_route_data
import pandas as pd

# 解析原始数据
data = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
print(f'解析后原始记录数: {len(data)}')

# 清理数据
cleaned = clean_route_data(data)
print(f'清理后总航线数: {len(cleaned)}')

# 转换为DataFrame并去重
df = pd.DataFrame(cleaned)
print(f'去重后DataFrame行数: {len(df)}')

# 统计航司数量
airline_col = 'airline'
print(f'航司数量: {len(df[airline_col].unique())}')

# 显示航司列表
airlines = sorted(df[airline_col].unique())
print(f'航司列表: {", ".join(airlines)}')