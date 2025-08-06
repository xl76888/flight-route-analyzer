#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查当前数据状态
"""

import pandas as pd
import os

def check_data_status():
    """检查当前数据状态"""
    data_file = 'data/integrated_all_data_latest.csv'
    
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        return
    
    print(f"📊 正在检查数据文件: {data_file}")
    
    # 读取数据
    df = pd.read_csv(data_file)
    
    print(f"\n📈 数据概览:")
    print(f"总航线数: {len(df):,}")
    print(f"航司数量: {df['airline'].nunique()}")
    
    # 检查中转航线
    transit_mask = (
        df['origin'].str.contains(r'[-—→>]', na=False) | 
        df['destination'].str.contains(r'[-—→>]', na=False)
    )
    transit_count = transit_mask.sum()
    
    print(f"中转航线数: {transit_count:,}")
    print(f"中转航线比例: {transit_count/len(df)*100:.1f}%")
    
    print(f"\n🏢 各航司航线数量 (前10):")
    airline_counts = df['airline'].value_counts().head(10)
    for airline, count in airline_counts.items():
        print(f"  {airline}: {count:,}")
    
    # 检查国货航数据
    guohuo_data = df[df['airline'] == '国货航']
    if len(guohuo_data) > 0:
        guohuo_transit = guohuo_data[
            (guohuo_data['origin'].str.contains(r'[-—→>]', na=False)) | 
            (guohuo_data['destination'].str.contains(r'[-—→>]', na=False))
        ]
        print(f"\n✈️ 国货航数据:")
        print(f"  总航线数: {len(guohuo_data):,}")
        print(f"  中转航线数: {len(guohuo_transit):,}")
        
        if len(guohuo_transit) > 0:
            print(f"  中转航线样本:")
            for i, row in guohuo_transit.head(3).iterrows():
                print(f"    {row['origin']} → {row['destination']}")
    
    # 检查文件修改时间
    import datetime
    mtime = os.path.getmtime(data_file)
    mod_time = datetime.datetime.fromtimestamp(mtime)
    print(f"\n🕒 数据文件最后修改时间: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n✅ 数据检查完成")

if __name__ == '__main__':
    check_data_status()