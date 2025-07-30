#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断数据问题：航线数量和航司数量分析
"""

import pandas as pd
from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data

def diagnose_data_issues():
    """诊断数据处理中的问题"""
    print("🔍 数据问题诊断分析")
    print("=" * 50)
    
    try:
        # 1. 读取原始Excel文件
        print("\n📊 步骤1: 读取原始Excel文件")
        excel_file = 'data/大陆航司全货机航线.xlsx'
        raw_excel = pd.read_excel(excel_file)
        print(f"Excel原始行数: {len(raw_excel)}")
        
        # 统计有航线数据的行数
        has_export = raw_excel['出口航线'].notna() & (raw_excel['出口航线'] != '') & (raw_excel['出口航线'] != '无近一个月的飞行记录')
        has_import = raw_excel['进口航线'].notna() & (raw_excel['进口航线'] != '') & (raw_excel['进口航线'] != '无近一个月的飞行记录')
        has_routes = has_export | has_import
        
        print(f"有出口航线的行数: {has_export.sum()}")
        print(f"有进口航线的行数: {has_import.sum()}")
        print(f"有航线数据的行数: {has_routes.sum()}")
        
        # 统计航司数量
        airlines_in_excel = raw_excel['航司'].dropna().unique()
        print(f"Excel中的航司数量: {len(airlines_in_excel)}")
        print(f"Excel中的航司列表: {list(airlines_in_excel)}")
        
        # 2. 解析数据
        print("\n🔄 步骤2: 解析Excel数据")
        parsed_df = parse_excel_route_data(excel_file)
        print(f"解析后记录数: {len(parsed_df)}")
        
        if not parsed_df.empty:
            parsed_airlines = parsed_df['airline'].unique()
            print(f"解析后航司数量: {len(parsed_airlines)}")
            print(f"解析后航司列表: {list(parsed_airlines)}")
            
            # 检查是否有航司丢失
            missing_airlines = set(airlines_in_excel) - set(parsed_airlines)
            if missing_airlines:
                print(f"❌ 丢失的航司: {list(missing_airlines)}")
            else:
                print("✅ 所有航司都已解析")
        
        # 3. 数据清理（不去重）
        print("\n🧹 步骤3: 数据清理（不去重）")
        cleaned_df = clean_route_data(parsed_df, enable_deduplication=False)
        print(f"清理后记录数: {len(cleaned_df)}")
        
        if not cleaned_df.empty:
            cleaned_airlines = cleaned_df['airline'].unique()
            print(f"清理后航司数量: {len(cleaned_airlines)}")
            print(f"清理后航司列表: {list(cleaned_airlines)}")
            
            # 按航司统计航线数量
            print("\n📈 各航司航线数量统计:")
            airline_counts = cleaned_df['airline'].value_counts()
            for airline, count in airline_counts.items():
                print(f"  {airline}: {count} 条")
        
        # 4. 数据清理（去重）
        print("\n🧹 步骤4: 数据清理（去重）")
        deduped_df = clean_route_data(parsed_df, enable_deduplication=True)
        print(f"去重后记录数: {len(deduped_df)}")
        
        if not deduped_df.empty:
            deduped_airlines = deduped_df['airline'].unique()
            print(f"去重后航司数量: {len(deduped_airlines)}")
            print(f"去重后航司列表: {list(deduped_airlines)}")
        
        # 5. 问题分析
        print("\n🎯 问题分析:")
        print(f"预期航线数: 543条")
        print(f"实际显示: 611条")
        print(f"差异: +{611-543}条")
        
        if len(cleaned_df) == 611:
            print("✅ 当前显示的611条与清理后数据一致")
        else:
            print(f"❌ 数据不一致，清理后实际为{len(cleaned_df)}条")
        
        # 分析可能的原因
        print("\n🔍 可能原因分析:")
        print("1. 多段航线处理：虽然不再拆分，但可能仍有其他因素")
        print("2. 数据清理逻辑：可能过滤条件不够严格")
        print("3. 重复数据：可能存在未被识别的重复记录")
        
    except Exception as e:
        print(f"❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_data_issues()