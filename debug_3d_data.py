#!/usr/bin/env python3
"""
调试3D地图数据传递问题
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from airport_coords import get_airport_coords
from map3d_integration import Map3DIntegration
import pandas as pd

def test_3d_data_flow():
    """测试3D地图数据流程"""
    
    print("🔍 测试3D地图数据传递...")
    
    # 模拟一些测试数据
    test_routes = [
        {
            'start_airport': '北京',
            'end_airport': '上海',
            'start_airport_name': '北京首都国际机场',
            'end_airport_name': '上海浦东国际机场',
            'airline': '中国国航',
            'aircraft_type': 'A320',
            'frequency': 10
        },
        {
            'start_airport': '广州',
            'end_airport': '深圳',
            'start_airport_name': '广州白云国际机场',
            'end_airport_name': '深圳宝安国际机场',
            'airline': '南方航空',
            'aircraft_type': 'B737',
            'frequency': 8
        }
    ]
    
    print(f"原始数据: {len(test_routes)} 条航线")
    
    # 模拟web_app.py中的数据处理
    route_data_3d = []
    for route in test_routes:
        start_coords = get_airport_coords(route.get('start_airport', ''))
        end_coords = get_airport_coords(route.get('end_airport', ''))
        
        if start_coords and end_coords:
            route_data_3d.append({
                'start_airport': route.get('start_airport', ''),
                'end_airport': route.get('end_airport', ''),
                'start_airport_name': route.get('start_airport_name', ''),
                'end_airport_name': route.get('end_airport_name', ''),
                'start_lat': start_coords[0],
                'start_lng': start_coords[1],
                'end_lat': end_coords[0],
                'end_lng': end_coords[1],
                'frequency': route.get('frequency', 1),
                'airline': route.get('airline', ''),
                'aircraft_type': route.get('aircraft_type', ''),
                'route_type': 'domestic'
            })
            print(f"✅ 航线 {route.get('start_airport')} -> {route.get('end_airport')}: {start_coords} -> {end_coords}")
        else:
            print(f"❌ 航线 {route.get('start_airport')} -> {route.get('end_airport')}: 坐标缺失")
    
    print(f"处理后数据: {len(route_data_3d)} 条有效航线")
    
    if route_data_3d:
        # 测试Map3DIntegration
        integration = Map3DIntegration()
        processed = integration._preprocess_data(route_data_3d)
        print(f"预处理后数据: {len(processed)} 条航线")
        
        if processed:
            print("✅ 数据验证通过")
            print("第一条航线数据:")
            print(processed[0])
        else:
            print("❌ 数据验证失败")
    else:
        print("❌ 没有有效数据")
    
    return route_data_3d

if __name__ == "__main__":
    test_3d_data_flow()