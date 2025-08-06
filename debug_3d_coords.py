#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试3D地图机场坐标问题
"""

import pandas as pd
from parser import load_data
from airport_coords import get_airport_info

def debug_3d_coordinates():
    """调试3D地图机场坐标获取问题"""
    
    print("🔍 开始调试3D地图机场坐标...")
    
    # 加载数据
    try:
        files_to_load = [
            'data/integrated_all_data_latest.csv',
            'data/中国十六家货航国际航线.xlsx',
            'data/大陆航司全货机航线.xlsx'
        ]
        routes_df = load_data(files_to_load)
        print(f"✅ 成功加载数据，总航线数: {len(routes_df)}")
        
        # 模拟往返航线视图处理
        filtered = routes_df.copy()
        
        # 往返航线视图处理
        round_trip_pairs = []
        route_pairs_dict = {}
        
        # 按航线对分组
        for _, row in filtered.iterrows():
            origin = row.get('origin', '')
            destination = row.get('destination', '')
            direction = row.get('direction', '')
            
            if not origin or not destination:
                continue
                
            # 创建航线对的键（不区分方向）
            route_key = tuple(sorted([origin, destination]))
            
            if route_key not in route_pairs_dict:
                route_pairs_dict[route_key] = {'出口': [], '进口': []}
            
            # 根据实际的起点终点和方向来分类
            if direction == '出口':
                route_pairs_dict[route_key]['出口'].append(row)
            elif direction == '进口':
                route_pairs_dict[route_key]['进口'].append(row)
        
        # 创建往返航线对
        for route_key, directions in route_pairs_dict.items():
            city1, city2 = route_key
            export_routes = directions['出口']
            import_routes = directions['进口']
            
            if export_routes or import_routes:
                round_trip_pairs.append({
                    'city_pair': f"{city1} ↔ {city2}",
                    'export_routes': export_routes,
                    'import_routes': import_routes,
                    'total_routes': len(export_routes) + len(import_routes),
                    'has_both_directions': len(export_routes) > 0 and len(import_routes) > 0
                })
        
        # 更新filtered为往返航线视图的数据
        filtered_for_display = []
        for pair in round_trip_pairs:
            filtered_for_display.extend(pair['export_routes'])
            filtered_for_display.extend(pair['import_routes'])
        
        if filtered_for_display:
            filtered = pd.DataFrame(filtered_for_display)
        else:
            filtered = pd.DataFrame()
        
        print(f"📊 往返航线视图筛选后数据量: {len(filtered)}")
        
        if filtered.empty:
            print("❌ 筛选后数据为空，无法生成3D地图")
            return False
        
        # 检查3D地图数据准备
        valid_routes_count = 0
        invalid_routes_count = 0
        coord_missing_count = 0
        coord_invalid_count = 0
        
        print("\n🔍 检查机场坐标获取情况...")
        
        # 取前20条记录进行详细检查
        sample_routes = filtered.head(20)
        
        for i, (_, route) in enumerate(sample_routes.iterrows()):
            origin_code = route.get('origin', '')
            destination_code = route.get('destination', '')
            
            print(f"\n📍 航线 {i+1}: {origin_code} -> {destination_code}")
            
            # 检查起点机场信息
            start_info = get_airport_info(origin_code)
            if start_info:
                print(f"  ✅ 起点: {start_info['name']} - {start_info['coords']}")
            else:
                print(f"  ❌ 起点: 无法获取机场信息")
                coord_missing_count += 1
                continue
            
            # 检查终点机场信息
            end_info = get_airport_info(destination_code)
            if end_info:
                print(f"  ✅ 终点: {end_info['name']} - {end_info['coords']}")
            else:
                print(f"  ❌ 终点: 无法获取机场信息")
                coord_missing_count += 1
                continue
            
            # 验证坐标有效性
            def is_valid_coordinate(coords):
                if not coords or len(coords) != 2:
                    return False
                lat, lon = coords
                return (isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and
                        -90 <= lat <= 90 and -180 <= lon <= 180)
            
            if not is_valid_coordinate(start_info['coords']):
                print(f"  ⚠️ 起点坐标无效: {start_info['coords']}")
                coord_invalid_count += 1
                continue
            
            if not is_valid_coordinate(end_info['coords']):
                print(f"  ⚠️ 终点坐标无效: {end_info['coords']}")
                coord_invalid_count += 1
                continue
            
            valid_routes_count += 1
            print(f"  ✅ 航线有效")
        
        print(f"\n📊 坐标检查结果:")
        print(f"  ✅ 有效航线: {valid_routes_count}")
        print(f"  ❌ 坐标缺失: {coord_missing_count}")
        print(f"  ⚠️ 坐标无效: {coord_invalid_count}")
        
        if valid_routes_count == 0:
            print("\n❌ 没有有效的航线可以显示在3D地图上")
            print("💡 可能原因:")
            print("  1. 机场代码在airport_coords.py中找不到对应信息")
            print("  2. 机场坐标数据格式错误")
            print("  3. 机场坐标超出有效范围")
            return False
        else:
            print(f"\n✅ 有 {valid_routes_count} 条有效航线可以显示在3D地图上")
            return True
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_3d_coordinates()
    
    if success:
        print("\n✅ 3D地图坐标数据正常")
    else:
        print("\n❌ 3D地图坐标数据存在问题，需要修复airport_coords.py")