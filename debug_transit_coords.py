#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试中转站坐标问题
"""

import pandas as pd
from airport_coords import get_airport_coords

def debug_transit_coordinates():
    """调试包含中转站信息的坐标获取问题"""
    print("🔍 调试中转站坐标问题")
    print("=" * 50)
    
    # 读取数据
    df = pd.read_csv('data/integrated_all_data_latest.csv')
    print(f"📊 总记录数: {len(df)}")
    
    # 分析包含中转站的城市名称
    transit_origins = []
    transit_destinations = []
    
    for _, row in df.iterrows():
        origin = str(row['origin']).strip()
        destination = str(row['destination']).strip()
        
        # 检查是否包含中转站信息（包含"-"符号）
        if '-' in origin:
            transit_origins.append(origin)
        if '-' in destination:
            transit_destinations.append(destination)
    
    print(f"\n🔄 包含中转站的起点: {len(set(transit_origins))} 个唯一值")
    print(f"🔄 包含中转站的终点: {len(set(transit_destinations))} 个唯一值")
    
    # 显示示例
    unique_transit_origins = list(set(transit_origins))[:10]
    unique_transit_destinations = list(set(transit_destinations))[:10]
    
    print("\n📍 中转起点示例:")
    for origin in unique_transit_origins:
        coords = get_airport_coords(origin)
        print(f"  {origin} -> {coords}")
    
    print("\n📍 中转终点示例:")
    for dest in unique_transit_destinations:
        coords = get_airport_coords(dest)
        print(f"  {dest} -> {coords}")
    
    # 统计无法获取坐标的记录
    missing_coords_count = 0
    total_records = len(df)
    
    print("\n🔍 逐条检查坐标获取情况:")
    for i, row in df.iterrows():
        origin = str(row['origin']).strip()
        destination = str(row['destination']).strip()
        
        origin_coords = get_airport_coords(origin)
        dest_coords = get_airport_coords(destination)
        
        if not origin_coords or not dest_coords:
            missing_coords_count += 1
            if missing_coords_count <= 5:  # 只显示前5个示例
                print(f"  ❌ 记录 {i+1}: {origin} -> {destination}")
                print(f"     起点坐标: {origin_coords}, 终点坐标: {dest_coords}")
    
    print(f"\n📊 统计结果:")
    print(f"  总记录数: {total_records}")
    print(f"  缺失坐标记录数: {missing_coords_count}")
    print(f"  缺失比例: {missing_coords_count/total_records*100:.1f}%")
    
    # 分析中转站解析逻辑
    print("\n🔧 中转站解析测试:")
    test_cases = [
        "美国安克雷奇-美国芝加哥",
        "加拿大温哥华-加拿大多伦多",
        "越南河内-浦东",
        "新西兰奥克兰-广州"
    ]
    
    for case in test_cases:
        print(f"\n  测试: {case}")
        # 尝试分割并获取各部分坐标
        if '-' in case:
            parts = case.split('-')
            print(f"    分割结果: {parts}")
            for i, part in enumerate(parts):
                part = part.strip()
                coords = get_airport_coords(part)
                print(f"    部分 {i+1} '{part}': {coords}")
        else:
            coords = get_airport_coords(case)
            print(f"    直接查询: {coords}")

if __name__ == "__main__":
    debug_transit_coordinates()