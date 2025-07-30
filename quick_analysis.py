#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速分析航线数据
"""

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
import pandas as pd

def quick_analysis():
    """快速分析数据扩展过程"""
    
    # 1. 读取原始Excel数据
    file_path = 'data/大陆航司全货机航线.xlsx'
    original_df = pd.read_excel(file_path)
    print(f"原始数据: {len(original_df)} 条记录")
    
    # 2. 解析和扩展数据
    print("\n=== 解析Excel数据 ===")
    parsed_df = parse_excel_route_data(file_path)
    print(f"解析后数据: {len(parsed_df)} 条记录")
    
    # 3. 清洗数据
    print("\n=== 清洗数据 ===")
    cleaned_df = clean_route_data(parsed_df)
    print(f"清洗后数据: {len(cleaned_df)} 条记录")
    
    # 4. 保存清洗后的数据
    output_file = 'data/cleaned_route_data.csv'
    cleaned_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n数据已保存到: {output_file}")
    
    # 5. 显示数据样本
    print("\n=== 数据样本 ===")
    print(cleaned_df.head(10))
    
    # 6. 统计信息
    print("\n=== 统计信息 ===")
    print(f"总航线数: {len(cleaned_df)}")
    print(f"涉及城市数: {len(set(cleaned_df['origin']) | set(cleaned_df['destination']))}")
    print(f"航空公司数: {cleaned_df['airline'].nunique()}")
    
    # 按航空公司统计
    airline_stats = cleaned_df.groupby('airline').size().sort_values(ascending=False)
    print("\n各航空公司航线数:")
    for airline, count in airline_stats.items():
        print(f"  {airline}: {count} 条")

if __name__ == '__main__':
    quick_analysis()