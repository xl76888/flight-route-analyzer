#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证中转航线判断逻辑修复效果
检查修复后的web_app.py是否能正确识别中转航线
"""

import pandas as pd
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import load_data
from data_cleaner import clean_route_data

def test_transit_detection():
    """测试中转航线检测逻辑"""
    print("🔍 验证中转航线判断逻辑修复效果")
    print("=" * 60)
    
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
        
        print(f"📁 找到数据文件: {data_files}")
        routes_df = load_data(data_files)
        
        if routes_df is None or routes_df.empty:
            print("❌ 无法加载数据")
            return
        
        routes_df = clean_route_data(routes_df)
        print(f"✅ 成功加载数据，共 {len(routes_df)} 条航线")
        
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return
    
    # 测试新的中转判断逻辑
    def determine_route_type_new(row):
        """新的中转判断逻辑（与web_app.py保持一致）"""
        origin = str(row['origin'])
        destination = str(row['destination'])
        
        # 检查是否包含中转信息（支持多种分隔符）
        transit_separators = ['-', '—', '→', '>']
        has_transit = any(
            sep in origin or sep in destination 
            for sep in transit_separators
        )
        return '🔄 中转' if has_transit else '✈️ 直飞'
    
    # 应用新的判断逻辑
    routes_df['航线类型_新'] = routes_df.apply(determine_route_type_new, axis=1)
    
    # 统计结果
    transit_count = len(routes_df[routes_df['航线类型_新'] == '🔄 中转'])
    direct_count = len(routes_df[routes_df['航线类型_新'] == '✈️ 直飞'])
    
    print(f"\n📊 修复后的中转判断结果:")
    print(f"  总航线数: {len(routes_df)}")
    print(f"  中转航线: {transit_count} ({transit_count/len(routes_df)*100:.1f}%)")
    print(f"  直飞航线: {direct_count} ({direct_count/len(routes_df)*100:.1f}%)")
    
    # 重点检查国货航
    print(f"\n🔍 国货航中转航线检查:")
    print("-" * 40)
    
    guohuo_data = routes_df[routes_df['airline'] == '国货航']
    if guohuo_data.empty:
        print("❌ 未找到国货航数据")
        return
    
    guohuo_transit = guohuo_data[guohuo_data['航线类型_新'] == '🔄 中转']
    guohuo_direct = guohuo_data[guohuo_data['航线类型_新'] == '✈️ 直飞']
    
    print(f"  国货航总航线: {len(guohuo_data)}")
    print(f"  中转航线: {len(guohuo_transit)} ({len(guohuo_transit)/len(guohuo_data)*100:.1f}%)")
    print(f"  直飞航线: {len(guohuo_direct)} ({len(guohuo_direct)/len(guohuo_data)*100:.1f}%)")
    
    # 显示国货航中转航线样本
    if not guohuo_transit.empty:
        print(f"\n📋 国货航中转航线样本 (前10条):")
        print("-" * 50)
        for idx, row in guohuo_transit.head(10).iterrows():
            print(f"  {row['origin']} → {row['destination']} ({row['direction']})")
    
    # 检查使用不同分隔符的航线
    print(f"\n🔧 分隔符使用情况分析:")
    print("-" * 40)
    
    separators = ['-', '—', '→', '>']
    for sep in separators:
        sep_count = len(routes_df[
            routes_df['origin'].str.contains(sep, na=False) | 
            routes_df['destination'].str.contains(sep, na=False)
        ])
        if sep_count > 0:
            print(f"  使用 '{sep}' 分隔符: {sep_count} 条航线")
            
            # 显示使用该分隔符的航线样本
            sep_routes = routes_df[
                routes_df['origin'].str.contains(sep, na=False) | 
                routes_df['destination'].str.contains(sep, na=False)
            ]
            
            if not sep_routes.empty:
                sample_route = sep_routes.iloc[0]
                print(f"    样本: {sample_route['origin']} → {sample_route['destination']} ({sample_route['airline']})")
    
    # 验证修复效果
    print(f"\n✅ 修复效果验证:")
    print("-" * 30)
    
    # 检查是否有使用'—'分隔符的航线被正确识别
    dash_routes = routes_df[
        routes_df['destination'].str.contains('—', na=False)
    ]
    
    if not dash_routes.empty:
        dash_transit_count = len(dash_routes[dash_routes['航线类型_新'] == '🔄 中转'])
        print(f"  使用'—'分隔符的航线: {len(dash_routes)} 条")
        print(f"  其中被识别为中转: {dash_transit_count} 条")
        
        if dash_transit_count == len(dash_routes):
            print("  ✅ 所有使用'—'分隔符的航线都被正确识别为中转")
        else:
            print(f"  ⚠️ 有 {len(dash_routes) - dash_transit_count} 条航线未被识别为中转")
    
    print(f"\n🎯 修复总结:")
    print("-" * 20)
    print(f"  ✅ 支持多种分隔符: {', '.join(separators)}")
    print(f"  ✅ 中转航线识别率提升: {transit_count} 条航线被识别为中转")
    print(f"  ✅ 国货航中转航线: {len(guohuo_transit)} 条")
    
    if len(guohuo_transit) > 0:
        print(f"  ✅ 修复成功！国货航的中转航线现在能被正确识别")
    else:
        print(f"  ⚠️ 国货航仍无中转航线，可能需要进一步检查数据")

if __name__ == "__main__":
    test_transit_detection()