#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中转分析逻辑问题诊断脚本
分析为什么有些有中转信息的航线被标记为直飞，以及直飞航线在中转分析中显示上海的问题
"""

import pandas as pd
import re
from collections import defaultdict

def analyze_transit_logic_issues():
    """分析中转判断逻辑的问题"""
    print("🔍 分析中转判断逻辑问题")
    print("=" * 60)
    
    # 读取数据
    try:
        df = pd.read_csv('data/integrated_all_data_latest.csv')
        print(f"✅ 成功读取数据: {len(df)} 条记录")
    except Exception as e:
        print(f"❌ 读取数据失败: {e}")
        return
    
    print("\n📊 数据基本信息:")
    print(f"  总记录数: {len(df)}")
    print(f"  列名: {list(df.columns)}")
    
    # 分析问题1: 有中转信息但被标记为直飞的航线
    print("\n🔍 问题1: 有中转信息但被标记为直飞的航线")
    print("-" * 40)
    
    # 识别包含中转信息的航线（destination或origin包含"-"符号）
    transit_routes = df[
        (df['destination'].str.contains('-', na=False)) | 
        (df['origin'].str.contains('-', na=False))
    ].copy()
    
    print(f"包含中转信息的航线总数: {len(transit_routes)}")
    
    if len(transit_routes) > 0:
        print("\n📋 包含中转信息的航线示例:")
        for i, (idx, row) in enumerate(transit_routes.head(10).iterrows()):
            origin = row['origin']
            destination = row['destination']
            direction = row['direction']
            print(f"  {i+1:2d}. {origin} → {destination} (标记为: {direction})")
            
            # 分析中转站
            transit_stations = []
            if '-' in str(destination):
                parts = str(destination).split('-')
                if len(parts) > 1:
                    transit_stations.extend(parts[:-1])  # 除了最后一个（真正目的地）
            if '-' in str(origin):
                parts = str(origin).split('-')
                if len(parts) > 1:
                    transit_stations.extend(parts[1:])   # 除了第一个（真正起点）
            
            if transit_stations:
                print(f"      🔄 中转站: {', '.join([s.strip() for s in transit_stations if s.strip()])}")
    
    # 分析问题2: 直飞航线在中转分析中显示上海
    print("\n🔍 问题2: 直飞航线在中转分析中显示上海")
    print("-" * 40)
    
    # 找出不包含中转信息的航线（真正的直飞）
    direct_routes = df[
        (~df['destination'].str.contains('-', na=False)) & 
        (~df['origin'].str.contains('-', na=False))
    ].copy()
    
    print(f"真正直飞航线总数: {len(direct_routes)}")
    
    # 模拟当前的中转地分析逻辑
    def analyze_transit_hubs_current(df_subset):
        """当前的中转地分析逻辑（有问题的版本）"""
        transit_info = []
        
        for idx, row in df_subset.iterrows():
            origin = row['origin']
            destination = row['destination']
            
            # 查找可能的中转地（同时连接起点和终点的城市）
            potential_transits = []
            
            # 查找从起点出发的其他航线的目的地
            origin_destinations = df[df['origin'] == origin]['destination'].unique()
            # 查找到达终点的其他航线的起点
            dest_origins = df[df['destination'] == destination]['origin'].unique()
            
            # 找到交集，即可能的中转地
            common_cities = set(origin_destinations) & set(dest_origins)
            # 排除起点和终点本身
            common_cities.discard(origin)
            common_cities.discard(destination)
            
            if common_cities:
                # 按照该中转地的航班频次排序
                transit_counts = {}
                for city in common_cities:
                    count = len(df[(df['origin'] == origin) & (df['destination'] == city)]) + \
                           len(df[(df['origin'] == city) & (df['destination'] == destination)])
                    transit_counts[city] = count
                
                # 选择频次最高的前3个中转地
                sorted_transits = sorted(transit_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                potential_transits = [city for city, count in sorted_transits]
            
            # 如果没有找到中转地，检查是否为直飞
            if not potential_transits:
                # 检查是否存在直接的往返航线
                reverse_exists = len(df[(df['origin'] == destination) & (df['destination'] == origin)]) > 0
                if reverse_exists:
                    transit_info.append('🔄 直飞往返')
                else:
                    transit_info.append('✈️ 直飞')
            else:
                transit_info.append('🔀 ' + ', '.join(potential_transits[:2]))
        
        return transit_info
    
    # 分析一些直飞航线的中转地分析结果
    sample_direct = direct_routes.head(20)
    transit_analysis = analyze_transit_hubs_current(sample_direct)
    
    print("\n📋 直飞航线的中转地分析结果示例:")
    for i, (idx, row) in enumerate(sample_direct.iterrows()):
        origin = row['origin']
        destination = row['destination']
        analysis = transit_analysis[i]
        print(f"  {i+1:2d}. {origin} → {destination} | 分析结果: {analysis}")
        
        # 如果分析结果显示有中转地，详细分析原因
        if '🔀' in analysis:
            print(f"      ⚠️  问题: 直飞航线被识别为有中转地")
            
            # 查找从起点出发的其他航线
            origin_routes = df[df['origin'] == origin]
            dest_routes = df[df['destination'] == destination]
            
            print(f"      📍 从{origin}出发的航线数: {len(origin_routes)}")
            print(f"      📍 到达{destination}的航线数: {len(dest_routes)}")
            
            # 找交集
            origin_destinations = set(origin_routes['destination'].unique())
            dest_origins = set(dest_routes['origin'].unique())
            common = origin_destinations & dest_origins
            common.discard(origin)
            common.discard(destination)
            
            if common:
                print(f"      🔄 被识别为中转地的城市: {list(common)}")
    
    # 提供修复建议
    print("\n💡 问题分析和修复建议")
    print("=" * 60)
    
    print("\n🔧 问题1修复: 中转航线类型判断")
    print("当前问题:")
    print("  - 包含中转信息的航线（如'浦东 → 美国安克雷奇-美国芝加哥'）被标记为'出口'")
    print("  - 应该被标记为'中转'或在显示时明确标识为中转航线")
    
    print("\n建议修复方案:")
    print("  1. 在数据处理时增加航线类型字段（直飞/中转）")
    print("  2. 修改方向判断逻辑，区分直飞和中转")
    print("  3. 在UI显示时明确标识中转航线")
    
    print("\n🔧 问题2修复: 中转地分析逻辑")
    print("当前问题:")
    print("  - 中转地分析逻辑基于航线网络连接性，而非实际中转站信息")
    print("  - 导致直飞航线被错误识别为有中转地")
    
    print("\n建议修复方案:")
    print("  1. 优先使用原始数据中的中转站信息（从destination/origin字段解析）")
    print("  2. 网络分析作为补充，仅用于没有明确中转信息的航线")
    print("  3. 区分'实际中转站'和'潜在中转枢纽'")
    
    return {
        'total_routes': len(df),
        'transit_routes_count': len(transit_routes),
        'direct_routes_count': len(direct_routes),
        'transit_routes_sample': transit_routes.head(10).to_dict('records'),
        'direct_routes_sample': sample_direct.to_dict('records')
    }

def propose_fixes():
    """提出具体的修复方案"""
    print("\n🛠️  具体修复方案")
    print("=" * 60)
    
    print("\n1️⃣ 修复航线类型判断逻辑")
    print("""
    def determine_route_type_and_direction(origin: str, destination: str) -> tuple:
        \"\"\"判断航线类型（直飞/中转）和方向（出口/进口）\"\"\"
        # 检查是否包含中转信息
        has_transit = '-' in str(origin) or '-' in str(destination)
        
        # 提取真实的起点和终点
        real_origin = str(origin).split('-')[0].strip() if '-' in str(origin) else str(origin).strip()
        real_destination = str(destination).split('-')[-1].strip() if '-' in str(destination) else str(destination).strip()
        
        # 判断方向
        origin_type = categorize_city_for_direction(real_origin)
        dest_type = categorize_city_for_direction(real_destination)
        
        if origin_type == '国内' and dest_type == '国外':
            direction = '出口'
        elif origin_type == '国外' and dest_type == '国内':
            direction = '进口'
        else:
            direction = '出口'  # 默认
        
        # 判断类型
        route_type = '中转' if has_transit else '直飞'
        
        return route_type, direction
    """)
    
    print("\n2️⃣ 修复中转地分析逻辑")
    print("""
    def analyze_transit_hubs_improved(df):
        \"\"\"改进的中转地分析逻辑\"\"\"
        transit_info = []
        
        for idx, row in df.iterrows():
            origin = str(row['origin'])
            destination = str(row['destination'])
            
            # 首先检查是否有明确的中转站信息
            actual_transits = []
            
            # 从destination字段提取中转站
            if '-' in destination:
                parts = destination.split('-')
                if len(parts) > 1:
                    actual_transits.extend([p.strip() for p in parts[:-1] if p.strip()])
            
            # 从origin字段提取中转站
            if '-' in origin:
                parts = origin.split('-')
                if len(parts) > 1:
                    actual_transits.extend([p.strip() for p in parts[1:] if p.strip()])
            
            if actual_transits:
                # 有明确的中转站信息
                unique_transits = list(dict.fromkeys(actual_transits))  # 去重保序
                transit_info.append('🔄 ' + ', '.join(unique_transits[:2]))
            else:
                # 没有明确中转站，进行网络分析（仅作为补充）
                real_origin = origin.split('-')[0].strip() if '-' in origin else origin.strip()
                real_destination = destination.split('-')[-1].strip() if '-' in destination else destination.strip()
                
                # 检查是否为往返航线
                reverse_exists = len(df[
                    (df['origin'].str.contains(real_destination, na=False)) & 
                    (df['destination'].str.contains(real_origin, na=False))
                ]) > 0
                
                if reverse_exists:
                    transit_info.append('✈️ 直飞往返')
                else:
                    transit_info.append('✈️ 直飞')
        
        return transit_info
    """)
    
    print("\n3️⃣ 修复数据显示逻辑")
    print("""
    # 在web_app.py中添加航线类型列
    display_df['航线类型'] = display_df.apply(
        lambda row: '🔄 中转' if ('-' in str(row['origin']) or '-' in str(row['destination'])) else '✈️ 直飞',
        axis=1
    )
    
    # 修改进出口类型显示
    display_df['进出口类型'] = display_df.apply(
        lambda row: f\"{row['direction']} ({row['航线类型'].replace('🔄 ', '').replace('✈️ ', '')})\",
        axis=1
    )
    """)

if __name__ == "__main__":
    result = analyze_transit_logic_issues()
    propose_fixes()
    
    print("\n📋 分析完成")
    print(f"  总航线数: {result['total_routes']}")
    print(f"  中转航线数: {result['transit_routes_count']}")
    print(f"  直飞航线数: {result['direct_routes_count']}")