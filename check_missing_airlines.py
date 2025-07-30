#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
import pandas as pd

def check_missing_airlines():
    # 解析原始数据
    data = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    df_raw = pd.DataFrame(data)
    
    # 清理数据
    cleaned = clean_route_data(data)
    df_clean = pd.DataFrame(cleaned)
    
    # 找出被过滤的航司
    raw_airlines = set(df_raw['airline'].unique())
    clean_airlines = set(df_clean['airline'].unique())
    missing_airlines = raw_airlines - clean_airlines
    
    print(f"解析后航司数: {len(raw_airlines)}")
    print(f"清理后航司数: {len(clean_airlines)}")
    print(f"被过滤航司: {missing_airlines}")
    
    # 分析每个被过滤的航司
    for airline in missing_airlines:
        print(f"\n=== {airline} 分析 ===")
        routes = df_raw[df_raw['airline'] == airline]
        print(f"该航司原始航线数: {len(routes)}")
        
        for idx, route in routes.iterrows():
            origin = route['origin']
            destination = route['destination']
            direction = route['direction']
            print(f"  航线: {origin} -> {destination} ({direction})")
            
            # 检查是否在清理后的数据中
            matching = df_clean[
                (df_clean['origin'] == origin) & 
                (df_clean['destination'] == destination) &
                (df_clean['direction'] == direction)
            ]
            
            if len(matching) == 0:
                print(f"    ❌ 整条航线被过滤")
            else:
                other_airlines = matching['airline'].unique()
                print(f"    ✅ 航线保留，但由其他航司运营: {other_airlines}")

if __name__ == "__main__":
    check_missing_airlines()