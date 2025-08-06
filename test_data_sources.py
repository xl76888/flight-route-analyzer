#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据源文件的可读性
"""

import pandas as pd
import os
from fix_parser import parse_excel_route_data

def test_data_sources():
    """测试所有数据源文件"""
    data_dir = "data"
    
    print("=== 数据源文件测试报告 ===")
    
    # 测试 Excel 文件
    excel_files = [
        "中国十六家货航国际航线.xlsx",
        "大陆航司全货机航线.xlsx"
    ]
    
    for file in excel_files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            print(f"\n📁 测试文件: {file}")
            try:
                # 直接读取 Excel
                df_raw = pd.read_excel(file_path)
                print(f"  ✅ 原始读取成功 - 行数: {len(df_raw)}, 列数: {len(df_raw.columns)}")
                print(f"  📋 列名: {df_raw.columns.tolist()[:5]}...")
                
                # 使用解析器
                df_parsed = parse_excel_route_data(file_path)
                print(f"  ✅ 解析器处理成功 - 行数: {len(df_parsed)}, 列数: {len(df_parsed.columns)}")
                if len(df_parsed) > 0:
                    print(f"  📋 解析后列名: {df_parsed.columns.tolist()}")
                    print(f"  📊 前3行数据:")
                    print(df_parsed.head(3))
                else:
                    print("  ⚠️ 解析后数据为空")
                    
            except Exception as e:
                print(f"  ❌ 读取失败: {str(e)}")
        else:
            print(f"\n❌ 文件不存在: {file}")
    
    # 测试 CSV 文件
    csv_files = [
        "cleaned_route_data.csv",
        "current_processed_data.csv"
    ]
    
    for file in csv_files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            print(f"\n📁 测试 CSV 文件: {file}")
            try:
                df = pd.read_csv(file_path)
                print(f"  ✅ 读取成功 - 行数: {len(df)}, 列数: {len(df.columns)}")
                print(f"  📋 列名: {df.columns.tolist()}")
                if len(df) > 0:
                    print(f"  📊 前3行数据:")
                    print(df.head(3))
            except Exception as e:
                print(f"  ❌ 读取失败: {str(e)}")
        else:
            print(f"\n❌ CSV 文件不存在: {file}")

if __name__ == "__main__":
    test_data_sources()