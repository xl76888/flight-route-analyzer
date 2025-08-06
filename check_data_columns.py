#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据文件的列名
"""

import pandas as pd

def check_data_file():
    """检查数据文件的列名和内容"""
    print("🔍 检查数据文件...")
    
    try:
        data_file = "data/大陆航司全货机航线.xlsx"
        df = pd.read_excel(data_file)
        
        print(f"✅ 成功加载数据文件，共 {len(df)} 行")
        print(f"📋 列名: {list(df.columns)}")
        
        # 显示前5行数据
        print("\n📊 前5行数据:")
        print(df.head())
        
        # 检查是否有包含起点终点信息的列
        for col in df.columns:
            print(f"\n列 '{col}' 的前5个值:")
            print(df[col].head().tolist())
            
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    check_data_file()