#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查当前数据处理结果
"""

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
import pandas as pd

def check_current_data():
    """检查当前数据处理的完整流程"""
    print("🔍 检查当前数据处理流程")
    print("=" * 50)
    
    # 步骤1：解析Excel数据
    print("\n📊 步骤1: 解析Excel数据")
    routes_df = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    print(f"解析后记录数: {len(routes_df)}")
    print(f"解析后航司数: {len(routes_df['airline'].unique())}")
    print(f"解析后航司列表: {sorted(routes_df['airline'].unique())}")
    
    # 步骤2：数据清理（不去重）
    print("\n🧹 步骤2: 数据清理（不去重）")
    cleaned_no_dedup = clean_route_data(routes_df.copy(), enable_deduplication=False)
    print(f"清理后记录数（不去重）: {len(cleaned_no_dedup)}")
    print(f"清理后航司数（不去重）: {len(cleaned_no_dedup['airline'].unique())}")
    print(f"清理后航司列表（不去重）: {sorted(cleaned_no_dedup['airline'].unique())}")
    
    # 步骤3：数据清理（去重）
    print("\n🧹 步骤3: 数据清理（去重）")
    cleaned_dedup = clean_route_data(routes_df.copy(), enable_deduplication=True)
    print(f"清理后记录数（去重）: {len(cleaned_dedup)}")
    print(f"清理后航司数（去重）: {len(cleaned_dedup['airline'].unique())}")
    print(f"清理后航司列表（去重）: {sorted(cleaned_dedup['airline'].unique())}")
    
    # 步骤4：检查Web应用默认设置
    print("\n🌐 步骤4: Web应用默认设置分析")
    print("根据web_app.py第408行，默认enable_deduplication=False")
    print(f"因此Web应用应该显示: {len(cleaned_no_dedup)} 条记录")
    
    # 步骤5：检查数据完整性
    print("\n✅ 步骤5: 数据完整性检查")
    
    # 检查是否有空值或无效记录
    invalid_origins = cleaned_no_dedup[cleaned_no_dedup['origin'].isna() | (cleaned_no_dedup['origin'] == '')]
    invalid_destinations = cleaned_no_dedup[cleaned_no_dedup['destination'].isna() | (cleaned_no_dedup['destination'] == '')]
    
    print(f"无效起点记录数: {len(invalid_origins)}")
    print(f"无效终点记录数: {len(invalid_destinations)}")
    
    # 检查各航司记录数
    print("\n📈 各航司记录数统计（不去重）:")
    airline_counts = cleaned_no_dedup['airline'].value_counts()
    for airline, count in airline_counts.items():
        print(f"  {airline}: {count} 条")
    
    # 检查可能的过滤原因
    print("\n🔍 可能的数据差异原因分析:")
    print(f"1. 解析后原始记录: {len(routes_df)}")
    print(f"2. 清理后记录（不去重）: {len(cleaned_no_dedup)}")
    print(f"3. 被过滤的记录数: {len(routes_df) - len(cleaned_no_dedup)}")
    
    if len(routes_df) != len(cleaned_no_dedup):
        print("\n❌ 数据在清理过程中被过滤，可能原因:")
        print("   - 城市名称无效或不在城市列表中")
        print("   - 起点和终点相同")
        print("   - 其他数据质量问题")
    
    # 保存当前数据到CSV以便检查
    cleaned_no_dedup.to_csv('data/current_processed_data.csv', index=False, encoding='utf-8-sig')
    print(f"\n💾 当前处理后的数据已保存到: data/current_processed_data.csv")
    
    return cleaned_no_dedup

if __name__ == "__main__":
    result = check_current_data()