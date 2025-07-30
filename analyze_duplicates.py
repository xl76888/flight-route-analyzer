# D:\flight_tool\analyze_duplicates.py
import pandas as pd
from parser import load_data
from data_cleaner import clean_route_data
import os

def analyze_route_aircraft_combinations():
    """分析航线和机型的组合情况"""
    
    # 加载数据文件
    data_dir = "D:\\flight_tool\\data"
    files_to_load = []
    
    for file in os.listdir(data_dir):
        if file.endswith(('.csv', '.xlsx', '.xls')):
            files_to_load.append(os.path.join(data_dir, file))
    
    if not files_to_load:
        print("未找到数据文件")
        return
    
    print(f"正在分析 {len(files_to_load)} 个数据文件...")
    
    # 加载原始数据（不去重）
    routes_df = load_data(files_to_load)
    
    if routes_df.empty:
        print("数据为空")
        return
    
    print(f"\n📊 原始数据分析：")
    print(f"总记录数：{len(routes_df)}")
    
    # 分析相同路线不同机型的情况
    if 'origin' in routes_df.columns and 'destination' in routes_df.columns and 'aircraft' in routes_df.columns:
        # 创建路线标识
        routes_df['route_key'] = routes_df['origin'] + ' -> ' + routes_df['destination']
        
        # 按路线分组，查看每条路线的机型情况
        route_aircraft_analysis = routes_df.groupby('route_key')['aircraft'].agg([
            'count',  # 该路线的记录数
            'nunique',  # 该路线的机型种类数
            lambda x: list(x.unique())  # 该路线的所有机型
        ]).rename(columns={'<lambda_0>': 'aircraft_types'})
        
        # 找出有多种机型的路线
        multi_aircraft_routes = route_aircraft_analysis[route_aircraft_analysis['nunique'] > 1]
        
        print(f"\n🔍 路线机型分析：")
        print(f"总路线数：{len(route_aircraft_analysis)}")
        print(f"有多种机型的路线数：{len(multi_aircraft_routes)}")
        
        if len(multi_aircraft_routes) > 0:
            print(f"\n📋 相同路线不同机型的详细情况：")
            for route, data in multi_aircraft_routes.iterrows():
                print(f"\n路线：{route}")
                print(f"  记录数：{data['count']}")
                print(f"  机型种类：{data['nunique']}")
                print(f"  机型列表：{', '.join(data['aircraft_types'])}")
                
                # 显示该路线的详细记录
                route_records = routes_df[routes_df['route_key'] == route][['airline', 'aircraft', 'flight_number']]
                for idx, record in route_records.iterrows():
                    print(f"    - {record['airline']} | {record['aircraft']} | {record.get('flight_number', 'N/A')}")
        else:
            print("✅ 未发现相同路线使用不同机型的情况")
        
        # 分析当前去重逻辑的影响
        print(f"\n🔄 去重逻辑分析：")
        print(f"当前去重字段：airline, origin, destination, aircraft, direction")
        
        # 模拟去重后的结果
        key_columns = ['airline', 'origin', 'destination', 'aircraft', 'direction']
        existing_key_columns = [col for col in key_columns if col in routes_df.columns]
        
        if existing_key_columns:
            dedup_df = routes_df.drop_duplicates(subset=existing_key_columns, keep='first')
            removed_count = len(routes_df) - len(dedup_df)
            print(f"去重前记录数：{len(routes_df)}")
            print(f"去重后记录数：{len(dedup_df)}")
            print(f"移除记录数：{removed_count}")
            
            # 检查去重是否会影响多机型路线
            if len(multi_aircraft_routes) > 0:
                print(f"\n⚠️  去重对多机型路线的影响：")
                print(f"由于去重逻辑包含'aircraft'字段，相同路线的不同机型记录会被保留")
                print(f"这意味着如果同一航司在同一路线上使用不同机型，这些记录不会被误删")
    
    else:
        print("数据中缺少必要的字段（origin, destination, aircraft）")

if __name__ == "__main__":
    analyze_route_aircraft_combinations()