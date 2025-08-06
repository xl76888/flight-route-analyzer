#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查使用'—'分隔符的航线数据
"""

import pandas as pd
import os

def check_dash_separator():
    """检查使用'—'分隔符的航线数据"""
    
    print("=" * 60)
    print("🔍 检查使用'—'分隔符的航线数据")
    print("=" * 60)
    
    # 读取数据
    data_dir = "d:/flight_tool/data"
    integrated_file = os.path.join(data_dir, "integrated_all_data_latest.csv")
    
    try:
        df = pd.read_csv(integrated_file, encoding='utf-8')
        print(f"✅ 成功读取数据文件，共 {len(df)} 条记录")
    except Exception as e:
        print(f"❌ 读取数据文件失败: {e}")
        return
    
    # 检查所有使用'—'分隔符的航线
    dash_in_origin = df[df['origin'].str.contains('—', na=False)]
    dash_in_dest = df[df['destination'].str.contains('—', na=False)]
    
    print(f"\n📊 使用'—'分隔符的航线统计:")
    print(f"- origin字段包含'—': {len(dash_in_origin)} 条")
    print(f"- destination字段包含'—': {len(dash_in_dest)} 条")
    
    # 显示国货航使用'—'的航线
    guohuo_dash = df[
        (df['airline'].str.contains('国货航', na=False)) & 
        (df['destination'].str.contains('—', na=False))
    ]
    
    print(f"\n🔄 国货航使用'—'分隔符的航线 ({len(guohuo_dash)} 条):")
    print("-" * 80)
    
    for idx, row in guohuo_dash.iterrows():
        origin = row['origin']
        destination = row['destination']
        airline = row['airline']
        aircraft = row['aircraft']
        
        # 分析destination中的中转信息
        if '—' in str(destination):
            parts = str(destination).split('—')
            if len(parts) > 1:
                transit_stations = [p.strip() for p in parts[:-1] if p.strip()]
                final_dest = parts[-1].strip()
                print(f"航线: {origin} → {destination}")
                print(f"  航司: {airline}")
                print(f"  机型: {aircraft}")
                print(f"  中转站: {', '.join(transit_stations)}")
                print(f"  最终目的地: {final_dest}")
                print()
    
    # 检查其他航司使用'—'的情况
    other_airlines_dash = df[
        (~df['airline'].str.contains('国货航', na=False)) & 
        (df['destination'].str.contains('—', na=False))
    ]
    
    if len(other_airlines_dash) > 0:
        print(f"\n🔄 其他航司使用'—'分隔符的航线 (前10条):")
        print("-" * 80)
        
        airline_counts = other_airlines_dash['airline'].value_counts()
        print(f"涉及航司: {dict(airline_counts)}")
        
        for idx, row in other_airlines_dash.head(10).iterrows():
            print(f"{row['airline']}: {row['origin']} → {row['destination']}")
    
    # 检查所有可能的分隔符
    print(f"\n🔍 检查所有可能的分隔符:")
    print("-" * 50)
    
    separators = ['-', '—', '→', '>', '至', '到', '经', '转']
    for sep in separators:
        origin_count = len(df[df['origin'].str.contains(sep, na=False, regex=False)])
        dest_count = len(df[df['destination'].str.contains(sep, na=False, regex=False)])
        total_count = origin_count + dest_count
        if total_count > 0:
            print(f"分隔符 '{sep}': origin={origin_count}, destination={dest_count}, 总计={total_count}")

if __name__ == "__main__":
    check_dash_separator()