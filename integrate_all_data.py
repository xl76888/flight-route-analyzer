#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合所有数据源的脚本
将所有已解析的CSV文件合并成一个完整的数据集
"""

import pandas as pd
import os
from datetime import datetime

def integrate_all_data_sources():
    """
    整合所有数据源
    """
    print("=== 开始整合所有数据源 ===")
    
    all_dataframes = []
    data_sources = []
    
    # 1. 中国十六家货航国际航线数据
    sixteen_airlines_file = "data/中国十六家货航国际航线_解析结果.csv"
    if os.path.exists(sixteen_airlines_file):
        try:
            df_sixteen = pd.read_csv(sixteen_airlines_file)
            df_sixteen['data_source'] = '中国十六家货航国际航线'
            all_dataframes.append(df_sixteen)
            data_sources.append(f"中国十六家货航国际航线: {len(df_sixteen)} 条记录")
            print(f"✓ 加载中国十六家货航数据: {len(df_sixteen)} 条记录")
        except Exception as e:
            print(f"✗ 加载中国十六家货航数据失败: {e}")
    else:
        print(f"✗ 文件不存在: {sixteen_airlines_file}")
    
    # 2. 大陆航司全货机航线数据（通过fix_parser解析的）
    mainland_airlines_file = "data/current_processed_data.csv"
    if os.path.exists(mainland_airlines_file):
        try:
            df_mainland = pd.read_csv(mainland_airlines_file)
            # 检查是否有data_source列，如果没有则添加
            if 'data_source' not in df_mainland.columns:
                df_mainland['data_source'] = '大陆航司全货机航线'
            all_dataframes.append(df_mainland)
            data_sources.append(f"大陆航司全货机航线: {len(df_mainland)} 条记录")
            print(f"✓ 加载大陆航司数据: {len(df_mainland)} 条记录")
        except Exception as e:
            print(f"✗ 加载大陆航司数据失败: {e}")
    else:
        print(f"✗ 文件不存在: {mainland_airlines_file}")
    
    # 3. 清理后的航线数据
    cleaned_file = "data/cleaned_route_data.csv"
    if os.path.exists(cleaned_file):
        try:
            df_cleaned = pd.read_csv(cleaned_file)
            # 检查是否有data_source列，如果没有则添加
            if 'data_source' not in df_cleaned.columns:
                df_cleaned['data_source'] = '清理后航线数据'
            # 检查是否与其他数据重复，避免重复添加
            if len(all_dataframes) == 0 or not any(df.equals(df_cleaned.drop('data_source', axis=1)) for df in all_dataframes):
                all_dataframes.append(df_cleaned)
                data_sources.append(f"清理后航线数据: {len(df_cleaned)} 条记录")
                print(f"✓ 加载清理后数据: {len(df_cleaned)} 条记录")
            else:
                print(f"⚠ 清理后数据与已有数据重复，跳过")
        except Exception as e:
            print(f"✗ 加载清理后数据失败: {e}")
    else:
        print(f"✗ 文件不存在: {cleaned_file}")
    
    if not all_dataframes:
        print("✗ 没有找到任何可用的数据源")
        return None
    
    # 合并所有数据
    print(f"\n=== 开始合并 {len(all_dataframes)} 个数据源 ===")
    
    # 统一列名格式
    standardized_dfs = []
    for i, df in enumerate(all_dataframes):
        print(f"处理数据源 {i+1}: {df.shape}")
        print(f"列名: {list(df.columns)}")
        
        # 确保所有必要的列都存在
        required_columns = ['airline', 'reg', 'aircraft', 'age', 'origin', 'destination', 'direction', 'remarks', 'data_source']
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        # 只保留标准列
        standardized_df = df[required_columns].copy()
        standardized_dfs.append(standardized_df)
    
    # 合并数据
    combined_df = pd.concat(standardized_dfs, ignore_index=True)
    
    # 数据清理
    print(f"\n=== 数据清理 ===")
    print(f"合并前总记录数: {len(combined_df)}")
    
    # 移除完全重复的记录
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates()
    after_dedup = len(combined_df)
    print(f"移除重复记录: {before_dedup - after_dedup} 条")
    
    # 移除关键字段为空的记录
    before_clean = len(combined_df)
    combined_df = combined_df[
        (combined_df['airline'].notna()) & 
        (combined_df['airline'].str.strip() != '') &
        (combined_df['origin'].notna()) & 
        (combined_df['origin'].str.strip() != '') &
        (combined_df['destination'].notna()) & 
        (combined_df['destination'].str.strip() != '')
    ]
    after_clean = len(combined_df)
    print(f"移除无效记录: {before_clean - after_clean} 条")
    
    print(f"最终记录数: {len(combined_df)}")
    
    # 统计报告
    print(f"\n=== 整合数据统计报告 ===")
    print(f"数据源统计:")
    for source in data_sources:
        print(f"  {source}")
    
    print(f"\n按数据源统计:")
    source_counts = combined_df['data_source'].value_counts()
    for source, count in source_counts.items():
        print(f"  {source}: {count} 条记录")
    
    print(f"\n按航司统计:")
    airline_counts = combined_df['airline'].value_counts().head(10)
    for airline, count in airline_counts.items():
        print(f"  {airline}: {count} 条记录")
    
    print(f"\n按方向统计:")
    direction_counts = combined_df['direction'].value_counts()
    for direction, count in direction_counts.items():
        print(f"  {direction}: {count} 条记录")
    
    # 统计城市
    origins = combined_df['origin'].unique()
    destinations = combined_df['destination'].unique()
    all_cities = set(origins) | set(destinations)
    
    print(f"\n城市统计:")
    print(f"  涉及城市总数: {len(all_cities)}")
    print(f"  起点城市数: {len(origins)}")
    print(f"  终点城市数: {len(destinations)}")
    
    # 保存整合后的数据
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/integrated_all_data_{timestamp}.csv"
    combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ 整合数据已保存到: {output_file}")
    
    # 也保存一个最新版本
    latest_file = "data/integrated_all_data_latest.csv"
    combined_df.to_csv(latest_file, index=False, encoding='utf-8-sig')
    print(f"✓ 最新版本已保存到: {latest_file}")
    
    return combined_df

def show_data_summary():
    """
    显示数据摘要
    """
    latest_file = "data/integrated_all_data_latest.csv"
    if os.path.exists(latest_file):
        df = pd.read_csv(latest_file)
        print(f"\n=== 最新整合数据摘要 ===")
        print(f"总记录数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        print(f"列名: {list(df.columns)}")
        print(f"\n前5条记录:")
        print(df.head())
    else:
        print(f"最新整合数据文件不存在: {latest_file}")

if __name__ == "__main__":
    # 整合所有数据
    result_df = integrate_all_data_sources()
    
    if result_df is not None:
        print(f"\n=== 整合完成 ===")
        show_data_summary()
    else:
        print(f"\n=== 整合失败 ===")