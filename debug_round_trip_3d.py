#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试往返航线视图的3D地图数据传递问题
"""

import pandas as pd
from parser import load_data
from airport_coords import get_airport_info
import json
import hashlib

def debug_round_trip_3d_data():
    """调试往返航线视图的3D地图数据传递"""
    
    print("🔍 开始调试往返航线视图的3D地图数据传递...")
    
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
        print(f"📊 往返航线对数量: {len(round_trip_pairs)}")
        
        if filtered.empty:
            print("❌ 筛选后数据为空，无法生成3D地图")
            return False
        
        # 模拟3D地图数据准备过程
        print("\n🎯 开始准备3D地图数据...")
        
        route_data_3d = []
        valid_count = 0
        invalid_count = 0
        
        for idx, row in filtered.iterrows():
            origin_code = row.get('origin', '')
            destination_code = row.get('destination', '')
            
            if not origin_code or not destination_code:
                invalid_count += 1
                continue
            
            # 获取机场坐标
            start_info = get_airport_info(origin_code)
            end_info = get_airport_info(destination_code)
            
            if not start_info or not end_info:
                invalid_count += 1
                continue
            
            # 验证坐标
            def is_valid_coordinate(coords):
                if not coords or len(coords) != 2:
                    return False
                lat, lon = coords
                return (isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and
                        -90 <= lat <= 90 and -180 <= lon <= 180)
            
            if not is_valid_coordinate(start_info['coords']) or not is_valid_coordinate(end_info['coords']):
                invalid_count += 1
                continue
            
            # 处理频率数据，确保为数字类型
            frequency = row.get('weekly_frequency', 1)
            if isinstance(frequency, str):
                try:
                    frequency = float(frequency) if frequency else 1
                except (ValueError, TypeError):
                    frequency = 1
            elif frequency is None:
                frequency = 1
            
            # 创建3D地图数据项
            route_3d = {
                'start_airport': start_info['name'],
                'end_airport': end_info['name'],
                'start_coords': start_info['coords'],
                'end_coords': end_info['coords'],
                'airline': row.get('airline', '未知'),
                'aircraft': row.get('aircraft', '未知'),
                'frequency': frequency,
                'direction': row.get('direction', ''),
                'flight_number': row.get('flight_number', ''),
                'route_key': f"{origin_code}-{destination_code}"
            }
            
            route_data_3d.append(route_3d)
            valid_count += 1
        
        print(f"📊 3D地图数据准备结果:")
        print(f"  ✅ 有效航线: {valid_count}")
        print(f"  ❌ 无效航线: {invalid_count}")
        print(f"  📈 有效率: {valid_count/(valid_count+invalid_count)*100:.1f}%")
        
        if valid_count == 0:
            print("\n❌ 没有有效的3D地图数据")
            return False
        
        # 模拟数据哈希生成（web_app.py中的逻辑）
        data_str = json.dumps(route_data_3d, sort_keys=True, default=str)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()[:8]
        
        print(f"\n🔑 数据哈希: {data_hash}")
        print(f"📦 3D地图组件key: 3d_map_{data_hash}")
        
        # 检查前5条3D数据
        print("\n📋 前5条3D地图数据:")
        for i, route in enumerate(route_data_3d[:5]):
            print(f"  {i+1}. {route['start_airport']} -> {route['end_airport']}")
            print(f"     坐标: {route['start_coords']} -> {route['end_coords']}")
            print(f"     航司: {route['airline']}, 频率: {route['frequency']}")
        
        # 统计信息
        unique_airports = len(set([r['start_airport'] for r in route_data_3d] + [r['end_airport'] for r in route_data_3d]))
        unique_airlines = len(set([r['airline'] for r in route_data_3d]))
        avg_frequency = sum([r['frequency'] for r in route_data_3d]) / len(route_data_3d) if route_data_3d else 0
        
        print(f"\n📊 3D地图统计信息:")
        print(f"  🗺️ 3D航线: {len(route_data_3d)} 条")
        print(f"  ✈️ 机场: {unique_airports} 个")
        print(f"  🏢 航司: {unique_airlines} 家")
        print(f"  📈 平均频率: {avg_frequency:.1f}")
        
        # 检查往返航线视图特有的数据特征
        print(f"\n🔄 往返航线视图特征分析:")
        direction_counts = {}
        for route in route_data_3d:
            direction = route['direction']
            direction_counts[direction] = direction_counts.get(direction, 0) + 1
        
        for direction, count in direction_counts.items():
            print(f"  {direction}: {count} 条")
        
        # 检查是否有配对的航线
        route_pairs_check = {}
        for route in route_data_3d:
            start = route['start_airport']
            end = route['end_airport']
            pair_key = tuple(sorted([start, end]))
            
            if pair_key not in route_pairs_check:
                route_pairs_check[pair_key] = {'出口': 0, '进口': 0}
            
            route_pairs_check[pair_key][route['direction']] += 1
        
        both_directions = 0
        one_way_only = 0
        
        for pair_key, directions in route_pairs_check.items():
            if directions['出口'] > 0 and directions['进口'] > 0:
                both_directions += 1
            else:
                one_way_only += 1
        
        print(f"\n🔄 航线配对分析:")
        print(f"  ↔️ 双向航线对: {both_directions}")
        print(f"  ➡️ 单向航线对: {one_way_only}")
        print(f"  📊 双向比例: {both_directions/(both_directions+one_way_only)*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_round_trip_3d_data()
    
    if success:
        print("\n✅ 往返航线视图的3D地图数据传递正常")
        print("💡 如果3D地图仍然显示为空，可能的原因:")
        print("  1. JavaScript组件接收数据时出现问题")
        print("  2. 3D地图组件的数据更新逻辑有bug")
        print("  3. Streamlit组件通信问题")
        print("  4. 浏览器缓存问题")
    else:
        print("\n❌ 往返航线视图的3D地图数据传递存在问题")