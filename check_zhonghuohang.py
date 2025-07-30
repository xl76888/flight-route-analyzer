#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查中货航数据处理情况
"""

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
import pandas as pd

def check_zhonghuohang():
    """检查中货航数据处理情况"""
    print("🔍 检查中货航数据处理情况")
    print("=" * 40)
    
    # 1. 解析数据
    print("\n📊 步骤1: 解析Excel数据")
    df = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    
    # 检查中货航记录
    zhonghuohang = df[df['airline'] == '中货航']
    print(f"解析后中货航记录数: {len(zhonghuohang)}")
    
    if len(zhonghuohang) > 0:
        print("\n中货航记录详情:")
        for idx, row in zhonghuohang.head(10).iterrows():
            print(f"  {row['airline']}: {row['origin']} -> {row['destination']} ({row['direction']})")
    else:
        print("❌ 解析后没有找到中货航记录")
        return
    
    # 2. 数据清理
    print("\n🧹 步骤2: 数据清理")
    cleaned_df = clean_route_data(df, enable_deduplication=False)
    
    # 检查清理后的中货航记录
    cleaned_zhonghuohang = cleaned_df[cleaned_df['airline'] == '中货航']
    print(f"清理后中货航记录数: {len(cleaned_zhonghuohang)}")
    
    if len(cleaned_zhonghuohang) > 0:
        print("\n清理后中货航记录详情:")
        for idx, row in cleaned_zhonghuohang.head(10).iterrows():
            print(f"  {row['airline']}: {row['origin']} -> {row['destination']} ({row['direction']})")
    else:
        print("❌ 数据清理后中货航记录被过滤掉了")
        
        # 分析被过滤的原因
        print("\n🔍 分析被过滤的原因:")
        for idx, row in zhonghuohang.iterrows():
            origin = row['origin']
            destination = row['destination']
            
            # 检查城市坐标
            from airport_coords import get_airport_coords
            origin_coords = get_airport_coords(origin)
            dest_coords = get_airport_coords(destination)
            
            print(f"  航线: {origin} -> {destination}")
            print(f"    起点坐标: {origin_coords}")
            print(f"    终点坐标: {dest_coords}")
            
            if origin_coords is None:
                print(f"    ❌ 起点 '{origin}' 缺少坐标")
            if dest_coords is None:
                print(f"    ❌ 终点 '{destination}' 缺少坐标")
    
    # 3. 统计总体情况
    print("\n📈 总体统计:")
    print(f"解析后总记录数: {len(df)}")
    print(f"清理后总记录数: {len(cleaned_df)}")
    print(f"解析后航司数: {df['airline'].nunique()}")
    print(f"清理后航司数: {cleaned_df['airline'].nunique()}")
    
    # 检查哪些航司被过滤了
    parsed_airlines = set(df['airline'].unique())
    cleaned_airlines = set(cleaned_df['airline'].unique())
    filtered_airlines = parsed_airlines - cleaned_airlines
    
    if filtered_airlines:
        print(f"\n❌ 被过滤的航司: {list(filtered_airlines)}")
    else:
        print("\n✅ 所有航司都保留了")

if __name__ == "__main__":
    check_zhonghuohang()