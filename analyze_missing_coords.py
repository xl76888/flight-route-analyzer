#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析缺失坐标的航线
"""

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
from airport_coords import get_airport_coords
import pandas as pd
from collections import Counter

def analyze_missing_coordinates():
    """分析缺失坐标的航线"""
    print("🔍 分析缺失坐标的航线")
    print("=" * 50)
    
    # 加载和清理数据
    routes_df = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    routes_df = clean_route_data(routes_df, enable_deduplication=False)
    
    print(f"总航线数: {len(routes_df)}")
    
    # 分析缺失坐标的城市
    missing_origins = []
    missing_destinations = []
    missing_routes = []
    
    for idx, row in routes_df.iterrows():
        origin_coords = get_airport_coords(row['origin'])
        dest_coords = get_airport_coords(row['destination'])
        
        if not origin_coords:
            missing_origins.append(row['origin'])
        if not dest_coords:
            missing_destinations.append(row['destination'])
        
        if not origin_coords or not dest_coords:
            missing_routes.append({
                'airline': row['airline'],
                'origin': row['origin'],
                'destination': row['destination'],
                'missing_origin': not origin_coords,
                'missing_dest': not dest_coords
            })
    
    print(f"\n❌ 缺失坐标的航线数: {len(missing_routes)}")
    print(f"❌ 缺失起点坐标的记录数: {len(missing_origins)}")
    print(f"❌ 缺失终点坐标的记录数: {len(missing_destinations)}")
    
    # 统计缺失最多的城市
    print("\n🏙️ 缺失坐标最多的起点城市:")
    origin_counts = Counter(missing_origins)
    for city, count in origin_counts.most_common(10):
        print(f"  {city}: {count} 次")
    
    print("\n🏙️ 缺失坐标最多的终点城市:")
    dest_counts = Counter(missing_destinations)
    for city, count in dest_counts.most_common(10):
        print(f"  {city}: {count} 次")
    
    # 找出所有唯一的缺失城市
    all_missing_cities = set(missing_origins + missing_destinations)
    print(f"\n📍 需要补充坐标的城市总数: {len(all_missing_cities)}")
    
    # 按频率排序
    all_missing_counts = Counter(missing_origins + missing_destinations)
    print("\n🎯 按影响航线数排序的缺失城市:")
    for city, count in all_missing_counts.most_common(20):
        print(f"  {city}: 影响 {count} 条航线")
    
    # 分析这些城市的特征
    print("\n🔍 缺失城市分析:")
    chinese_cities = [city for city in all_missing_cities if any('\u4e00' <= char <= '\u9fff' for char in city)]
    english_cities = [city for city in all_missing_cities if not any('\u4e00' <= char <= '\u9fff' for char in city)]
    
    print(f"  中文城市名: {len(chinese_cities)} 个")
    print(f"  英文城市名: {len(english_cities)} 个")
    
    # 显示一些示例
    print("\n📝 中文城市示例:")
    for city in sorted(chinese_cities)[:10]:
        print(f"  {city}")
    
    print("\n📝 英文城市示例:")
    for city in sorted(english_cities)[:10]:
        print(f"  {city}")
    
    # 保存详细分析结果
    missing_df = pd.DataFrame(missing_routes)
    missing_df.to_csv('data/missing_coordinates_analysis.csv', index=False, encoding='utf-8-sig')
    print(f"\n💾 详细分析结果已保存到: data/missing_coordinates_analysis.csv")
    
    # 生成坐标补充建议
    print("\n💡 坐标补充建议:")
    print("1. 优先补充影响航线数最多的城市坐标")
    print("2. 对于机场全名，可以映射到对应的城市坐标")
    print("3. 对于英文城市名，需要查找对应的经纬度")
    print("4. 补充后预计可增加显示航线数:", len(missing_routes))
    
    return all_missing_counts

if __name__ == "__main__":
    result = analyze_missing_coordinates()