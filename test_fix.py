#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复效果
"""

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
from airport_coords import get_airport_coords

def test_fix():
    print("🔍 测试修复效果")
    print("=" * 50)
    
    # 加载和清理数据
    routes_df = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    routes_df = clean_route_data(routes_df, enable_deduplication=False)
    
    print(f"总航线数: {len(routes_df)}")
    print(f"航司数量: {routes_df['airline'].nunique()}")
    
    # 测试坐标获取
    print("\n🧪 测试坐标获取:")
    test_cities = ['素万那普', '芜湖', '深圳', '曼谷']
    for city in test_cities:
        coords = get_airport_coords(city)
        if coords:
            print(f"✅ {city}: {coords}")
        else:
            print(f"❌ {city}: 未找到坐标")
    
    # 统计缺失坐标的航线
    missing_count = 0
    for idx, row in routes_df.iterrows():
        origin_coords = get_airport_coords(row['origin'])
        dest_coords = get_airport_coords(row['destination'])
        if not origin_coords or not dest_coords:
            missing_count += 1
    
    print(f"\n📊 缺失坐标的航线数: {missing_count}")
    print(f"📊 有坐标的航线数: {len(routes_df) - missing_count}")
    print(f"📊 坐标覆盖率: {((len(routes_df) - missing_count) / len(routes_df) * 100):.1f}%")
    
    print("\n✅ 修复测试完成！")

if __name__ == "__main__":
    test_fix()