#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
import pandas as pd

def check_remaining():
    # 解析和清理数据
    data = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    df_raw = pd.DataFrame(data)
    cleaned = clean_route_data(data)
    df_clean = pd.DataFrame(cleaned)
    
    # 找出仍被过滤的航司
    raw_airlines = set(df_raw['airline'].unique())
    clean_airlines = set(df_clean['airline'].unique())
    missing = raw_airlines - clean_airlines
    
    print(f'解析后航司数: {len(raw_airlines)}')
    print(f'清理后航司数: {len(clean_airlines)}')
    print(f'仍被过滤的航司: {missing}')
    
    if missing:
        for airline in missing:
            print(f'\n=== {airline} 的航线分析 ===')
            routes = df_raw[df_raw['airline'] == airline]
            print(f'该航司航线数: {len(routes)}')
            
            for idx, route in routes.head(3).iterrows():
                origin = route['origin']
                destination = route['destination']
                print(f'  航线: {origin} -> {destination}')
                print(f'    起点映射后: {origin}')
                print(f'    终点映射后: {destination}')

if __name__ == "__main__":
    check_remaining()