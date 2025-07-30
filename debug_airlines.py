#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data

def debug_airline_filtering():
    print("=== 航司过滤调试分析 ===")
    
    # 1. 解析原始数据
    print("\n1. 解析原始Excel数据...")
    raw_data = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    raw_df = pd.DataFrame(raw_data)
    
    print(f"原始解析后数据: {len(raw_df)} 条记录")
    raw_airlines = set(raw_df['airline'].dropna())
    print(f"原始航司数量: {len(raw_airlines)}")
    print(f"原始航司列表: {sorted(raw_airlines)}")
    
    # 2. 数据清理
    print("\n2. 执行数据清理...")
    cleaned_data = clean_route_data(raw_data)
    cleaned_df = pd.DataFrame(cleaned_data)
    
    print(f"清理后数据: {len(cleaned_df)} 条记录")
    cleaned_airlines = set(cleaned_df['airline'].dropna())
    print(f"清理后航司数量: {len(cleaned_airlines)}")
    print(f"清理后航司列表: {sorted(cleaned_airlines)}")
    
    # 3. 找出被过滤的航司
    print("\n3. 分析被过滤的航司...")
    filtered_out_airlines = raw_airlines - cleaned_airlines
    
    if filtered_out_airlines:
        print(f"被过滤掉的航司 ({len(filtered_out_airlines)}家): {sorted(filtered_out_airlines)}")
        
        # 分析每个被过滤航司的原因
        for airline in sorted(filtered_out_airlines):
            print(f"\n--- 分析航司: {airline} ---")
            airline_routes = raw_df[raw_df['airline'] == airline]
            print(f"该航司原始航线数: {len(airline_routes)}")
            
            # 检查每条航线的过滤原因
            for idx, route in airline_routes.iterrows():
                origin = route['origin']
                destination = route['destination']
                print(f"  航线: {origin} -> {destination}")
                
                # 检查是否在清理后的数据中
                matching_routes = cleaned_df[
                    (cleaned_df['airline'] == airline) & 
                    (cleaned_df['origin'] == origin) & 
                    (cleaned_df['destination'] == destination)
                ]
                
                if len(matching_routes) == 0:
                    print(f"    ❌ 被过滤 - 可能原因: 城市无效或其他清理规则")
                else:
                    print(f"    ✅ 保留")
    else:
        print("✅ 没有航司被完全过滤掉")
    
    # 4. 统计每个航司的航线数变化
    print("\n4. 各航司航线数变化统计:")
    print("航司名称\t原始航线数\t清理后航线数\t变化")
    print("-" * 50)
    
    for airline in sorted(raw_airlines | cleaned_airlines):
        raw_count = len(raw_df[raw_df['airline'] == airline])
        cleaned_count = len(cleaned_df[cleaned_df['airline'] == airline])
        change = cleaned_count - raw_count
        status = "✅" if cleaned_count > 0 else "❌"
        print(f"{status} {airline}\t{raw_count}\t{cleaned_count}\t{change:+d}")
    
    print(f"\n=== 总结 ===")
    print(f"原始航司: {len(raw_airlines)} 家")
    print(f"清理后航司: {len(cleaned_airlines)} 家")
    print(f"被过滤航司: {len(filtered_out_airlines)} 家")
    
if __name__ == "__main__":
    debug_airline_filtering()