#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试坐标修复效果
"""

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
from airport_coords import get_airport_coords
import pandas as pd

def test_coordinates_fix():
    """测试坐标修复效果"""
    print("🔧 测试坐标修复效果")
    print("=" * 50)
    
    # 加载和清理数据
    routes_df = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    routes_df = clean_route_data(routes_df, enable_deduplication=False)
    
    print(f"总航线数: {len(routes_df)}")
    
    # 统计修复前后的情况
    routes_with_coords = 0
    routes_without_coords = 0
    fixed_routes = []
    still_missing = []
    
    for idx, row in routes_df.iterrows():
        origin_coords = get_airport_coords(row['origin'])
        dest_coords = get_airport_coords(row['destination'])
        
        if origin_coords and dest_coords:
            routes_with_coords += 1
            # 检查是否是新修复的航线
            if row['origin'] in ['浦东', '斯坦斯特德', '克拉克', '普雷斯蒂克', '菲利普安吉利斯', '义乌', '阿斯塔纳', '东米德兰兹', '瓦茨拉夫哈维尔'] or \
               row['destination'] in ['浦东', '斯坦斯特德', '克拉克', '普雷斯蒂克', '菲利普安吉利斯', '义乌', '阿斯塔纳', '东米德兰兹', '瓦茨拉夫哈维尔']:
                fixed_routes.append({
                    'airline': row['airline'],
                    'origin': row['origin'],
                    'destination': row['destination']
                })
        else:
            routes_without_coords += 1
            missing_cities = []
            if not origin_coords:
                missing_cities.append(row['origin'])
            if not dest_coords:
                missing_cities.append(row['destination'])
            still_missing.extend(missing_cities)
    
    print(f"\n✅ 修复后统计:")
    print(f"  有坐标的航线: {routes_with_coords} 条")
    print(f"  缺失坐标的航线: {routes_without_coords} 条")
    print(f"  地图显示率: {routes_with_coords/len(routes_df)*100:.1f}%")
    
    print(f"\n🎯 修复效果:")
    print(f"  新增可显示航线: {len(fixed_routes)} 条")
    
    if fixed_routes:
        print(f"\n📈 修复的航线示例:")
        for i, route in enumerate(fixed_routes[:10]):
            print(f"  {i+1}. {route['airline']}: {route['origin']} → {route['destination']}")
        if len(fixed_routes) > 10:
            print(f"  ... 还有 {len(fixed_routes)-10} 条航线")
    
    # 检查仍然缺失的城市
    if still_missing:
        from collections import Counter
        missing_counts = Counter(still_missing)
        print(f"\n❌ 仍然缺失坐标的城市:")
        for city, count in missing_counts.most_common(10):
            print(f"  {city}: {count} 次")
    else:
        print(f"\n🎉 所有城市坐标都已补充完整！")
    
    # 验证特定城市的坐标
    print(f"\n🔍 验证补充的坐标:")
    test_cities = ['浦东', '斯坦斯特德', '克拉克', '普雷斯蒂克', '义乌']
    for city in test_cities:
        coords = get_airport_coords(city)
        if coords:
            print(f"  ✅ {city}: {coords}")
        else:
            print(f"  ❌ {city}: 坐标缺失")
    
    return routes_with_coords, routes_without_coords, len(fixed_routes)

if __name__ == "__main__":
    with_coords, without_coords, fixed_count = test_coordinates_fix()
    print(f"\n📊 最终结果:")
    print(f"  修复前地图显示: ~611 条航线")
    print(f"  修复后地图显示: {with_coords} 条航线")
    print(f"  新增显示航线: {fixed_count} 条")
    print(f"  提升幅度: {(with_coords-611)/611*100:.1f}%")