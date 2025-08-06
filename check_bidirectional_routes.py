#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据中的双向航线
"""

import pandas as pd
import streamlit as st
from collections import defaultdict

def check_bidirectional_routes():
    """检查数据中的双向航线"""
    try:
        # 读取数据
        df = pd.read_excel('data/大陆航司全货机航线.xlsx')
        print(f"总数据量: {len(df)} 条")
        print(f"数据列名: {list(df.columns)}")
        
        # 显示前5条数据
        print("\n前5条数据:")
        for i, (_, row) in enumerate(df.head().iterrows()):
            print(f"  {i+1}: {dict(row)}")
        
        # 统计航线 - 处理出口航线和进口航线
        export_routes = set()
        import_routes = set()
        
        for _, row in df.iterrows():
            export_route = str(row.get('出口航线', '')).strip()
            import_route = str(row.get('进口航线', '')).strip()
            
            if export_route and export_route != 'nan':
                export_routes.add(export_route)
            if import_route and import_route != 'nan':
                import_routes.add(import_route)
        
        print(f"\n出口航线数: {len(export_routes)}")
        print(f"进口航线数: {len(import_routes)}")
        
        # 显示一些出口和进口航线示例
        print(f"\n出口航线示例 (前10个):")
        for i, route in enumerate(list(export_routes)[:10]):
            print(f"  {i+1}: {route}")
            
        print(f"\n进口航线示例 (前10个):")
        for i, route in enumerate(list(import_routes)[:10]):
            print(f"  {i+1}: {route}")
        
        # 检查双向航线 - 基于出口和进口航线的对应关系
        bidirectional_pairs = []
        
        # 遍历每一行数据，检查出口航线和进口航线是否构成双向
        for _, row in df.iterrows():
            export_route = str(row.get('出口航线', '')).strip()
            import_route = str(row.get('进口航线', '')).strip()
            
            if export_route and import_route and export_route != 'nan' and import_route != 'nan':
                # 解析航线的起点和终点
                if '—' in export_route and '—' in import_route:
                    export_parts = export_route.split('—')
                    import_parts = import_route.split('—')
                    
                    if len(export_parts) == 2 and len(import_parts) == 2:
                        export_origin, export_dest = export_parts[0].strip(), export_parts[1].strip()
                        import_origin, import_dest = import_parts[0].strip(), import_parts[1].strip()
                        
                        # 检查是否为真正的双向航线（起点终点互换）
                        if export_origin == import_dest and export_dest == import_origin:
                            bidirectional_pairs.append({
                                'export_route': export_route,
                                'import_route': import_route,
                                'city_pair': f"{export_origin} ↔ {export_dest}"
                            })
        
        print(f"\n双向航线对数: {len(bidirectional_pairs)}")
        
        # 显示前10个双向航线
        for i, pair in enumerate(bidirectional_pairs[:10]):
            print(f"\n双向航线 {i + 1}:")
            print(f"  出口: {pair['export_route']}")
            print(f"  进口: {pair['import_route']}")
            print(f"  城市对: {pair['city_pair']}")
        
        return len(bidirectional_pairs)
        
    except Exception as e:
        print(f"错误: {e}")
        return 0

if __name__ == "__main__":
    bidirectional_count = check_bidirectional_routes()
    print(f"\n总结: 发现 {bidirectional_count} 对双向航线")