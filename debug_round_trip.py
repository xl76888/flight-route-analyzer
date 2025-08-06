#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试往返航线视图数据问题
"""

import pandas as pd
import streamlit as st
from parser import load_data

def debug_round_trip_data():
    """调试往返航线视图的数据处理逻辑"""
    
    print("🔍 开始调试往返航线视图数据...")
    
    # 加载数据
    try:
        # 使用与web_app.py相同的数据加载方式
        files_to_load = [
            'data/integrated_all_data_latest.csv',
            'data/中国十六家货航国际航线.xlsx',
            'data/大陆航司全货机航线.xlsx'
        ]
        routes_df = load_data(files_to_load)
        print(f"✅ 成功加载数据，总航线数: {len(routes_df)}")
        print(f"📊 数据列: {list(routes_df.columns)}")
        
        # 显示前几行数据
        print("\n📋 前5行数据:")
        print(routes_df.head())
        
        # 检查方向字段
        if 'direction' in routes_df.columns:
            direction_counts = routes_df['direction'].value_counts()
            print(f"\n📈 方向分布: {direction_counts.to_dict()}")
        else:
            print("\n⚠️ 缺少direction字段")
        
        # 模拟往返航线视图的数据处理
        print("\n🔄 模拟往返航线视图处理...")
        
        # 应用基本筛选（模拟web_app.py中的筛选逻辑）
        filtered = routes_df.copy()
        
        # 往返航线视图处理
        round_trip_pairs = []
        route_pairs_dict = {}
        
        print(f"📊 筛选后数据量: {len(filtered)}")
        
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
            else:
                print(f"⚠️ 未知方向: {direction}, 航线: {origin} -> {destination}")
        
        print(f"📊 发现航线对数量: {len(route_pairs_dict)}")
        
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
        
        print(f"📊 往返航线对数量: {len(round_trip_pairs)}")
        
        # 统计双向和单向航线对
        both_directions = [p for p in round_trip_pairs if p['has_both_directions']]
        one_way = [p for p in round_trip_pairs if not p['has_both_directions']]
        
        print(f"🔄 双向航线对: {len(both_directions)}")
        print(f"➡️ 单向航线对: {len(one_way)}")
        
        # 检查filtered_for_display
        filtered_for_display = []
        for pair in round_trip_pairs:
            filtered_for_display.extend(pair['export_routes'])
            filtered_for_display.extend(pair['import_routes'])
        
        print(f"📊 用于显示的航线数量: {len(filtered_for_display)}")
        
        if filtered_for_display:
            print("✅ 有数据可以显示")
            # 显示前几个航线对的详细信息
            print("\n📋 前5个航线对详情:")
            for i, pair in enumerate(round_trip_pairs[:5]):
                print(f"  {i+1}. {pair['city_pair']} - 出口:{len(pair['export_routes'])}, 进口:{len(pair['import_routes'])}, 双向:{pair['has_both_directions']}")
        else:
            print("❌ 没有数据可以显示")
            print("\n🔍 可能的原因:")
            print("  1. 数据中没有有效的出口/进口航线")
            print("  2. origin/destination字段为空")
            print("  3. direction字段值不是'出口'或'进口'")
            
            # 检查原始数据的direction字段值
            if 'direction' in routes_df.columns:
                unique_directions = routes_df['direction'].unique()
                print(f"  4. 实际direction值: {list(unique_directions)}")
        
        return len(filtered_for_display) > 0
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_round_trip_data()
    
    if success:
        print("\n✅ 往返航线视图数据处理正常")
    else:
        print("\n❌ 往返航线视图数据处理存在问题，需要进一步检查")