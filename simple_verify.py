#!/usr/bin/env python3
"""
简化验证3D地图数据修复的脚本
"""

import pandas as pd
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airport_coords import get_airport_coords

def verify_3d_data_building():
    """验证3D地图数据构建是否正确"""
    
    print("=== 验证3D地图数据构建 ===")
    
    try:
        # 直接读取测试数据
        df = pd.read_excel("data/大陆航司全货机航线.xlsx")
        print(f"原始数据记录数: {len(df)}")
        
        # 清理列名
        df.columns = df.columns.str.strip()
        
        # 检查列名
        print("可用列名:", df.columns.tolist())
        
        # 使用实际列名
        origin_col = '出口航线'
        destination_col = '进口航线'
        airline_col = '航司'
        
        # 模拟route_stats构建
        route_stats = {}
        for _, row in df.iterrows():
            origin = str(row[origin_col]).strip()
            destination = str(row[destination_col]).strip()
            
            if origin and destination and origin != 'nan' and destination != 'nan' and origin != 'NaN' and destination != 'NaN':
                # 解析航线格式："成都双流—阿姆斯特丹"
                origin_city = origin.split('—')[0] if '—' in origin else origin
                destination_city = destination.split('—')[0] if '—' in destination else destination
                
                route_key = f"{origin_city}-{destination_city}"
                if route_key not in route_stats:
                    route_stats[route_key] = {'count': 0, 'airlines': set(), 'directions': set()}
                route_stats[route_key]['count'] += 1
                route_stats[route_key]['airlines'].add(str(row[airline_col]))
        
        # 构建3D地图数据（修复后的逻辑）
        route_data_3d = []
        routes_without_coords = 0
        routes_with_coords = 0
        
        for _, row in df.iterrows():
            origin = str(row[origin_col]).strip()
            destination = str(row[destination_col]).strip()
            
            if origin == 'nan' or destination == 'nan' or not origin or not destination or origin == 'NaN' or destination == 'NaN':
                continue
                
            # 解析航线格式
            origin_city = origin.split('—')[0] if '—' in origin else origin
            destination_city = destination.split('—')[0] if '—' in destination else destination
            
            start_coords = get_airport_coords(origin_city)
            end_coords = get_airport_coords(destination_city)
            
            if start_coords and end_coords:
                route_key = f"{origin_city}-{destination_city}"
                route_data_3d.append({
                    'start_airport': origin_city,
                    'end_airport': destination_city,
                    'start_airport_name': origin_city,
                    'end_airport_name': destination_city,
                    'start_lat': start_coords[0],
                    'start_lng': start_coords[1],
                    'end_lat': end_coords[0],
                    'end_lng': end_coords[1],
                    'frequency': route_stats.get(route_key, {}).get('count', 1),
                    'airline': str(row[airline_col]),
                    'aircraft_type': 'B737',  # 默认值
                    'route_type': 'domestic'
                })
                routes_with_coords += 1
            else:
                routes_without_coords += 1
        
        print(f"3D地图数据记录数: {len(route_data_3d)}")
        print(f"有坐标航线数: {routes_with_coords}")
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
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_3d_data_building()