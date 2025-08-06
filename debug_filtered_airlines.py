import pandas as pd
from parse_sixteen_airlines import parse_sixteen_airlines_excel
from data_cleaner import clean_route_data, is_valid_city

# 加载原始数据
df = parse_sixteen_airlines_excel('data/中国十六家货航国际航线.xlsx')
print(f"原始数据总记录数: {len(df)}")
print(f"原始航司数量: {len(df['airline'].unique())}")
print(f"原始航司列表: {sorted(df['airline'].unique())}")

# 被过滤掉的航司
lost_airlines = ['京东航空', '南航', '国货航', '圆通航空', '天津货航', '西北货航', '邮政航空', '首都航']

print("\n=== 分析被过滤航司的数据 ===")
for airline in lost_airlines:
    airline_data = df[df['airline'] == airline]
    print(f"\n{airline}: {len(airline_data)} 条记录")
    
    # 检查前几条记录的始发地和目的地
    sample = airline_data.head(3)
    for idx, row in sample.iterrows():
        origin = row['origin']
        destination = row['destination']
        origin_valid = is_valid_city(origin)
        dest_valid = is_valid_city(destination)
        print(f"  始发地: '{origin}' (有效: {origin_valid}), 目的地: '{destination}' (有效: {dest_valid})")
        
        # 如果城市无效，检查原因
        if not origin_valid:
            print(f"    始发地 '{origin}' 被过滤的原因")
        if not dest_valid:
            print(f"    目的地 '{destination}' 被过滤的原因")

print("\n=== 清理后的数据 ===")
cleaned = clean_route_data(df, enable_deduplication=False)
print(f"清理后数据总记录数: {len(cleaned)}")
print(f"清理后航司数量: {len(cleaned['airline'].unique())}")
print(f"清理后航司列表: {sorted(cleaned['airline'].unique())}")