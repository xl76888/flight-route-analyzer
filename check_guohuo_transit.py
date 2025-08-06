#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国货航中转数据解析验证脚本
检查国货航的中转航线数据是否被正确解析和显示
"""

import pandas as pd
import os

def check_guohuo_transit_data():
    """检查国货航的中转数据解析情况"""
    
    print("=" * 60)
    print("🔍 国货航中转数据解析验证")
    print("=" * 60)
    
    # 检查数据文件
    data_dir = "d:/flight_tool/data"
    integrated_file = os.path.join(data_dir, "integrated_all_data_latest.csv")
    
    if not os.path.exists(integrated_file):
        print(f"❌ 数据文件不存在: {integrated_file}")
        return
    
    # 读取数据
    try:
        df = pd.read_csv(integrated_file, encoding='utf-8')
        print(f"✅ 成功读取数据文件，共 {len(df)} 条记录")
    except Exception as e:
        print(f"❌ 读取数据文件失败: {e}")
        return
    
    # 筛选国货航数据
    guohuo_data = df[df['airline'].str.contains('国货航', na=False)]
    print(f"\n📊 国货航总航线数: {len(guohuo_data)}")
    
    if len(guohuo_data) == 0:
        print("❌ 未找到国货航数据")
        return
    
    # 分析中转航线
    print("\n🔍 分析中转航线识别逻辑:")
    
    # 检查origin字段中的中转信息
    origin_with_transit = guohuo_data[guohuo_data['origin'].str.contains('-', na=False)]
    print(f"- origin字段包含'-'的航线: {len(origin_with_transit)} 条")
    
    # 检查destination字段中的中转信息
    dest_with_transit = guohuo_data[guohuo_data['destination'].str.contains('-', na=False)]
    print(f"- destination字段包含'-'的航线: {len(dest_with_transit)} 条")
    
    # 总的中转航线（按当前逻辑）
    transit_routes = guohuo_data[
        (guohuo_data['origin'].str.contains('-', na=False)) | 
        (guohuo_data['destination'].str.contains('-', na=False))
    ]
    print(f"- 按当前逻辑识别的中转航线: {len(transit_routes)} 条")
    
    # 直飞航线
    direct_routes = guohuo_data[
        (~guohuo_data['origin'].str.contains('-', na=False)) & 
        (~guohuo_data['destination'].str.contains('-', na=False))
    ]
    print(f"- 按当前逻辑识别的直飞航线: {len(direct_routes)} 条")
    
    # 详细分析中转航线
    if len(transit_routes) > 0:
        print("\n🔄 中转航线详细信息:")
        print("-" * 50)
        
        for idx, row in transit_routes.head(10).iterrows():
            origin = row['origin']
            destination = row['destination']
            airline = row['airline']
            
            # 提取中转站信息
            transit_stations = []
            
            # 从destination提取中转站
            if '-' in str(destination):
                parts = str(destination).split('-')
                if len(parts) > 1:
                    transit_stations.extend([p.strip() for p in parts[:-1] if p.strip()])
            
            # 从origin提取中转站
            if '-' in str(origin):
                parts = str(origin).split('-')
                if len(parts) > 1:
                    transit_stations.extend([p.strip() for p in parts[1:] if p.strip()])
            
            unique_transits = list(dict.fromkeys(transit_stations))  # 去重保序
            
            print(f"航线 {idx + 1}:")
            print(f"  航司: {airline}")
            print(f"  起点: {origin}")
            print(f"  终点: {destination}")
            print(f"  提取的中转站: {', '.join(unique_transits) if unique_transits else '无'}")
            print()
    
    # 检查可能被遗漏的中转信息
    print("\n🔍 检查可能遗漏的中转信息:")
    print("-" * 50)
    
    # 检查是否有其他分隔符
    other_separators = ['—', '→', '>', '至', '到']
    for sep in other_separators:
        origin_with_sep = guohuo_data[guohuo_data['origin'].str.contains(sep, na=False)]
        dest_with_sep = guohuo_data[guohuo_data['destination'].str.contains(sep, na=False)]
        if len(origin_with_sep) > 0 or len(dest_with_sep) > 0:
            print(f"- 使用分隔符'{sep}'的航线: origin={len(origin_with_sep)}, destination={len(dest_with_sep)}")
    
    # 显示一些样本数据
    print("\n📋 国货航航线样本数据:")
    print("-" * 50)
    sample_data = guohuo_data[['airline', 'origin', 'destination', 'aircraft']].head(10)
    for idx, row in sample_data.iterrows():
        print(f"{row['airline']}: {row['origin']} → {row['destination']} ({row['aircraft']})")
    
    # 统计总结
    print("\n📈 统计总结:")
    print("-" * 50)
    print(f"国货航总航线数: {len(guohuo_data)}")
    print(f"识别为中转航线: {len(transit_routes)} ({len(transit_routes)/len(guohuo_data)*100:.1f}%)")
    print(f"识别为直飞航线: {len(direct_routes)} ({len(direct_routes)/len(guohuo_data)*100:.1f}%)")
    
    # 检查web_app.py中的显示逻辑
    print("\n🖥️ Web应用显示逻辑分析:")
    print("-" * 50)
    print("当前web_app.py中的中转判断逻辑:")
    print("1. 检查origin或destination字段是否包含'-'")
    print("2. 如果包含'-'，则标记为'🔄 中转'")
    print("3. 否则标记为'✈️ 直飞'")
    print("\n建议改进:")
    print("1. 支持更多分隔符（如'—'、'→'等）")
    print("2. 改进中转站提取逻辑")
    print("3. 增加数据验证和错误处理")

if __name__ == "__main__":
    check_guohuo_transit_data()