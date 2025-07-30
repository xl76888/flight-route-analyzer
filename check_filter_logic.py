#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查筛选逻辑和数据统计一致性
"""

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
from airport_coords import get_airport_coords
import pandas as pd
from collections import Counter

def check_filter_logic():
    """检查筛选逻辑和数据统计一致性"""
    print("🔍 检查筛选逻辑和数据统计一致性")
    print("=" * 60)
    
    # 加载和清理数据
    routes_df = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    routes_df = clean_route_data(routes_df, enable_deduplication=False)
    
    print(f"总航线数: {len(routes_df)}")
    
    # 1. 检查进出口数据分布
    print("\n📊 1. 进出口数据分布检查")
    direction_counts = routes_df['direction'].value_counts()
    print(f"进出口统计:")
    for direction, count in direction_counts.items():
        print(f"  {direction}: {count} 条 ({count/len(routes_df)*100:.1f}%)")
    
    # 检查是否有空值
    null_directions = routes_df['direction'].isna().sum()
    print(f"  空值: {null_directions} 条")
    
    # 2. 检查始发地筛选逻辑
    print("\n🏙️ 2. 始发地筛选逻辑检查")
    
    # 获取前10个最常见的始发地
    top_origins = routes_df['origin'].value_counts().head(10)
    print(f"\n最常见的始发地:")
    for origin, count in top_origins.items():
        print(f"  {origin}: {count} 条航线")
    
    # 选择一个具体的始发地进行详细分析
    test_origin = top_origins.index[0]  # 选择最常见的始发地
    print(f"\n🎯 详细分析始发地: {test_origin}")
    
    # 筛选该始发地的所有航线
    origin_filtered = routes_df[routes_df['origin'] == test_origin]
    print(f"筛选后航线数: {len(origin_filtered)}")
    
    # 检查这些航线的坐标情况
    routes_with_coords = 0
    routes_without_coords = 0
    
    for idx, row in origin_filtered.iterrows():
        origin_coords = get_airport_coords(row['origin'])
        dest_coords = get_airport_coords(row['destination'])
        
        if origin_coords and dest_coords:
            routes_with_coords += 1
        else:
            routes_without_coords += 1
    
    print(f"  有坐标的航线: {routes_with_coords} 条")
    print(f"  缺失坐标的航线: {routes_without_coords} 条")
    print(f"  地图显示率: {routes_with_coords/len(origin_filtered)*100:.1f}%")
    
    # 检查进出口分布
    origin_directions = origin_filtered['direction'].value_counts()
    print(f"  进出口分布:")
    for direction, count in origin_directions.items():
        print(f"    {direction}: {count} 条")
    
    # 3. 检查目的地分布
    print(f"\n🎯 {test_origin} 的目的地分布:")
    destinations = origin_filtered['destination'].value_counts().head(10)
    for dest, count in destinations.items():
        dest_coords = get_airport_coords(dest)
        coord_status = "✅" if dest_coords else "❌"
        print(f"  {dest}: {count} 条 {coord_status}")
    
    # 4. 检查航司分布
    print(f"\n✈️ {test_origin} 的航司分布:")
    airlines = origin_filtered['airline'].value_counts()
    for airline, count in airlines.items():
        print(f"  {airline}: {count} 条")
    
    # 5. 模拟Web应用的筛选逻辑
    print("\n🌐 5. 模拟Web应用筛选逻辑")
    
    # 模拟选择始发地筛选
    filtered = routes_df.copy()
    filtered = filtered[filtered['origin'] == test_origin]
    
    print(f"筛选条件: 始发地 = {test_origin}")
    print(f"筛选后总记录数: {len(filtered)}")
    
    # 模拟地图显示逻辑（只显示有坐标的）
    map_displayable = 0
    for idx, row in filtered.iterrows():
        origin_coords = get_airport_coords(row['origin'])
        dest_coords = get_airport_coords(row['destination'])
        if origin_coords and dest_coords:
            map_displayable += 1
    
    print(f"地图可显示航线数: {map_displayable}")
    print(f"列表显示航线数: {len(filtered)}")
    print(f"数量是否一致: {'✅ 是' if map_displayable == len(filtered) else '❌ 否'}")
    
    if map_displayable != len(filtered):
        print(f"差异: {len(filtered) - map_displayable} 条航线无法在地图显示")
    
    # 6. 检查所有始发地的情况
    print("\n📈 6. 所有始发地统计")
    
    all_origins = routes_df['origin'].unique()
    print(f"总始发地数量: {len(all_origins)}")
    
    # 统计每个始发地的坐标情况
    origins_with_issues = []
    for origin in all_origins:
        origin_routes = routes_df[routes_df['origin'] == origin]
        total_routes = len(origin_routes)
        
        displayable = 0
        for idx, row in origin_routes.iterrows():
            origin_coords = get_airport_coords(row['origin'])
            dest_coords = get_airport_coords(row['destination'])
            if origin_coords and dest_coords:
                displayable += 1
        
        if displayable != total_routes:
            origins_with_issues.append({
                'origin': origin,
                'total': total_routes,
                'displayable': displayable,
                'missing': total_routes - displayable
            })
    
    if origins_with_issues:
        print(f"\n❌ 有坐标问题的始发地 ({len(origins_with_issues)} 个):")
        for issue in sorted(origins_with_issues, key=lambda x: x['missing'], reverse=True)[:10]:
            print(f"  {issue['origin']}: {issue['displayable']}/{issue['total']} 可显示 (缺失{issue['missing']}条)")
    else:
        print(f"\n✅ 所有始发地的航线都能完整显示在地图上")
    
    # 7. 检查进出口数据的合理性
    print("\n🔄 7. 进出口数据合理性检查")
    
    # 检查是否有往返航线
    route_pairs = {}
    for idx, row in routes_df.iterrows():
        route_key = f"{row['origin']}-{row['destination']}"
        reverse_key = f"{row['destination']}-{row['origin']}"
        
        if route_key not in route_pairs:
            route_pairs[route_key] = {'出口': 0, '进口': 0}
        route_pairs[route_key][row['direction']] += 1
    
    # 统计往返航线
    round_trip_routes = 0
    one_way_routes = 0
    
    for route_key, directions in route_pairs.items():
        if directions['出口'] > 0 and directions['进口'] > 0:
            round_trip_routes += 1
        else:
            one_way_routes += 1
    
    print(f"往返航线: {round_trip_routes} 条")
    print(f"单向航线: {one_way_routes} 条")
    print(f"往返比例: {round_trip_routes/(round_trip_routes+one_way_routes)*100:.1f}%")
    
    return {
        'total_routes': len(routes_df),
        'test_origin': test_origin,
        'origin_routes': len(origin_filtered),
        'origin_displayable': routes_with_coords,
        'directions': dict(direction_counts),
        'round_trip_routes': round_trip_routes,
        'one_way_routes': one_way_routes
    }

if __name__ == "__main__":
    result = check_filter_logic()
    print(f"\n📋 检查完成")
    print(f"建议: 确保Web界面的统计数字与实际筛选结果一致")