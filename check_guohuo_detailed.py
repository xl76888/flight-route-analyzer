#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细检查国货航数据
查看国货航的具体航线数据，分析为什么没有中转航线
"""

import pandas as pd
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import load_data
from data_cleaner import clean_route_data

def check_guohuo_detailed():
    """详细检查国货航数据"""
    print("🔍 详细检查国货航数据")
    print("=" * 50)
    
    # 加载数据
    try:
        # 查找数据文件
        data_dir = "data"
        data_files = []
        
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith(('.xlsx', '.csv')):
                    data_files.append(os.path.join(data_dir, file))
        
        if not data_files:
            print("❌ 未找到数据文件")
            return
        
        routes_df = load_data(data_files)
        routes_df = clean_route_data(routes_df)
        print(f"✅ 成功加载数据，共 {len(routes_df)} 条航线")
        
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return
    
    # 检查国货航数据
    print(f"\n🔍 国货航数据详细分析:")
    print("-" * 40)
    
    guohuo_data = routes_df[routes_df['airline'] == '国货航']
    if guohuo_data.empty:
        print("❌ 未找到国货航数据")
        
        # 检查所有航司名称
        print("\n📋 所有航司列表:")
        airlines = routes_df['airline'].unique()
        for airline in sorted(airlines):
            count = len(routes_df[routes_df['airline'] == airline])
            print(f"  {airline}: {count} 条航线")
        
        # 检查是否有包含"国货"的航司
        guohuo_like = [a for a in airlines if '国货' in str(a)]
        if guohuo_like:
            print(f"\n🔍 包含'国货'的航司: {guohuo_like}")
        
        return
    
    print(f"  国货航总航线: {len(guohuo_data)}")
    
    # 显示国货航的所有航线
    print(f"\n📋 国货航所有航线 (前20条):")
    print("-" * 60)
    for idx, row in guohuo_data.head(20).iterrows():
        origin = str(row['origin'])
        destination = str(row['destination'])
        direction = row.get('direction', 'N/A')
        
        # 检查是否包含分隔符
        separators = ['-', '—', '→', '>']
        has_sep = any(sep in origin or sep in destination for sep in separators)
        sep_indicator = "🔄" if has_sep else "✈️"
        
        print(f"  {sep_indicator} {origin} → {destination} ({direction})")
    
    # 检查国货航是否有包含分隔符的航线
    print(f"\n🔧 国货航分隔符检查:")
    print("-" * 30)
    
    separators = ['-', '—', '→', '>']
    total_with_sep = 0
    
    for sep in separators:
        sep_routes = guohuo_data[
            guohuo_data['origin'].str.contains(sep, na=False) | 
            guohuo_data['destination'].str.contains(sep, na=False)
        ]
        
        if not sep_routes.empty:
            print(f"  使用 '{sep}' 分隔符: {len(sep_routes)} 条航线")
            total_with_sep += len(sep_routes)
            
            # 显示样本
            for idx, row in sep_routes.head(3).iterrows():
                print(f"    样本: {row['origin']} → {row['destination']}")
        else:
            print(f"  使用 '{sep}' 分隔符: 0 条航线")
    
    print(f"\n📊 国货航中转航线统计:")
    print(f"  包含分隔符的航线: {total_with_sep} 条")
    print(f"  直飞航线: {len(guohuo_data) - total_with_sep} 条")
    
    if total_with_sep == 0:
        print(f"\n✅ 结论: 国货航确实没有包含中转信息的航线")
        print(f"  所有 {len(guohuo_data)} 条航线都是直飞航线")
    else:
        print(f"\n⚠️ 发现问题: 国货航有 {total_with_sep} 条包含分隔符的航线")
        print(f"  这些航线应该被识别为中转航线")
    
    # 检查国货航的航线格式
    print(f"\n📋 国货航航线格式分析:")
    print("-" * 30)
    
    # 分析origin和destination的格式
    origin_formats = {}
    dest_formats = {}
    
    for idx, row in guohuo_data.iterrows():
        origin = str(row['origin'])
        destination = str(row['destination'])
        
        # 分析格式模式
        origin_pattern = "包含分隔符" if any(sep in origin for sep in separators) else "简单格式"
        dest_pattern = "包含分隔符" if any(sep in destination for sep in separators) else "简单格式"
        
        origin_formats[origin_pattern] = origin_formats.get(origin_pattern, 0) + 1
        dest_formats[dest_pattern] = dest_formats.get(dest_pattern, 0) + 1
    
    print(f"  起点格式分布:")
    for pattern, count in origin_formats.items():
        print(f"    {pattern}: {count} 条")
    
    print(f"  终点格式分布:")
    for pattern, count in dest_formats.items():
        print(f"    {pattern}: {count} 条")
    
    # 显示一些典型的国货航航线样本
    print(f"\n📋 国货航典型航线样本:")
    print("-" * 40)
    
    # 按方向分组显示
    directions = guohuo_data['direction'].unique()
    for direction in directions:
        dir_data = guohuo_data[guohuo_data['direction'] == direction]
        print(f"\n  {direction}方向 ({len(dir_data)} 条):")
        for idx, row in dir_data.head(5).iterrows():
            print(f"    {row['origin']} → {row['destination']}")

if __name__ == "__main__":
    check_guohuo_detailed()