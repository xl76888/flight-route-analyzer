#!/usr/bin/env python3
"""
验证3D地图数据修复的脚本
"""

import pandas as pd
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airport_coords import get_airport_coords
from data_cleaner import clean_route_data
from parser import parse_file

def verify_3d_data_building():
    """验证3D地图数据构建是否正确"""
    
    print("=== 验证3D地图数据构建 ===")
    
    # 模拟web_app.py中的数据处理流程
    try:
        # 读取测试数据
        df = parse_file("2024-12-18.xlsx")
        df = clean_route_data(df)
        
        print(f"原始数据记录数: {len(df)}")
        
        # 模拟route_stats构建（类似web_app.py）
        route_stats = {}
        for _, row in df.iterrows():
            route_key = f"{row['origin']}-{row['destination']}"
            if route_key not in route_stats:
                route_stats[route_key] = {'count': 0, 'airlines': set(), 'directions': set()}
            route_stats[route_key]['count'] += 1
            route_stats[route_key]['airlines'].add(row['airline'])
            route_stats[route_key]['directions'].add(row.get('direction', '出口'))
        
        # 构建3D地图数据（修复后的逻辑）
        route_data_3d = []
        routes_without_coords = 0
        
        for _, route in df.iterrows():
            start_coords = get_airport_coords(route.get('origin', ''))
            end_coords = get_airport_coords(route.get('destination', ''))
            
            if start_coords and end_coords:
                route_data_3d.append({
                    'start_airport': route.get('origin', ''),
                    'end_airport': route.get('destination', ''),
                    'start_airport_name': route.get('origin', ''),
                    'end_airport_name': route.get('destination', ''),
                    'start_lat': start_coords[0],
                    'start_lng': start_coords[1],
                    'end_lat': end_coords[0],
                    'end_lng': end_coords[1],
                    'frequency': route_stats.get(f"{route.get('origin', '')}-{route.get('destination', '')}", {}).get('count', 1),
                    'airline': route.get('airline', ''),
                    'aircraft_type': route.get('aircraft', ''),
                    'route_type': 'domestic'
                })
            else:
                routes_without_coords += 1
        
        print(f"3D地图数据记录数: {len(route_data_3d)}")
        print(f"缺失坐标航线数: {routes_without_coords}")
        
        if route_data_3d:
            print("\n前3条3D地图数据示例:")
            for i, route in enumerate(route_data_3d[:3]):
                print(f"  {i+1}. {route['start_airport']} -> {route['end_airport']}")
                print(f"     坐标: ({route['start_lat']:.4f}, {route['start_lng']:.4f}) -> ({route['end_lat']:.4f}, {route['end_lng']:.4f})")
                print(f"     频率: {route['frequency']}, 航司: {route['airline']}")
        
        print("\n✅ 3D地图数据构建验证完成！")
        print("修复后的逻辑使用正确的列名：origin和destination")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        return False

if __name__ == "__main__":
    verify_3d_data_building()