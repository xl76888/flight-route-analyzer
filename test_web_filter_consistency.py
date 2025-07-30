#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web界面筛选逻辑的一致性
"""

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
from airport_coords import get_airport_coords
import pandas as pd
from collections import defaultdict

def test_web_filter_consistency():
    """测试Web界面筛选逻辑的一致性"""
    print("🔍 测试Web界面筛选逻辑的一致性")
    print("=" * 60)
    
    # 加载和清理数据
    routes_df = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    routes_df = clean_route_data(routes_df, enable_deduplication=False)
    
    print(f"总航线数: {len(routes_df)}")
    print(f"航司数量: {len(routes_df['airline'].unique())}")
    
    # 1. 测试始发地筛选的一致性
    print("\n🏙️ 1. 始发地筛选一致性测试")
    
    # 选择几个主要始发地进行测试
    test_origins = ['广州', '深圳', '鄂州', '首尔', '东京']
    
    for origin in test_origins:
        print(f"\n📍 测试始发地: {origin}")
        
        # 筛选该始发地的航线
        filtered = routes_df[routes_df['origin'] == origin]
        list_count = len(filtered)
        
        # 计算地图可显示的航线数
        map_displayable = 0
        missing_coords = []
        
        for idx, row in filtered.iterrows():
            origin_coords = get_airport_coords(row['origin'])
            dest_coords = get_airport_coords(row['destination'])
            
            if origin_coords and dest_coords:
                map_displayable += 1
            else:
                missing_info = {
                    'origin': row['origin'],
                    'destination': row['destination'],
                    'origin_coords': origin_coords,
                    'dest_coords': dest_coords
                }
                missing_coords.append(missing_info)
        
        print(f"  列表显示: {list_count} 条")
        print(f"  地图显示: {map_displayable} 条")
        print(f"  一致性: {'✅' if list_count == map_displayable else '❌'}")
        
        if missing_coords:
            print(f"  缺失坐标: {len(missing_coords)} 条")
            for missing in missing_coords[:3]:  # 只显示前3个
                print(f"    {missing['origin']} -> {missing['destination']}")
        
        # 检查进出口分布
        direction_dist = filtered['direction'].value_counts()
        print(f"  进出口分布: {dict(direction_dist)}")
    
    # 2. 测试进出口筛选的一致性
    print("\n🔄 2. 进出口筛选一致性测试")
    
    for direction in ['出口', '进口']:
        print(f"\n📊 测试方向: {direction}")
        
        # 筛选该方向的航线
        filtered = routes_df[routes_df['direction'] == direction]
        list_count = len(filtered)
        
        # 计算地图可显示的航线数
        map_displayable = 0
        for idx, row in filtered.iterrows():
            origin_coords = get_airport_coords(row['origin'])
            dest_coords = get_airport_coords(row['destination'])
            if origin_coords and dest_coords:
                map_displayable += 1
        
        print(f"  列表显示: {list_count} 条")
        print(f"  地图显示: {map_displayable} 条")
        print(f"  一致性: {'✅' if list_count == map_displayable else '❌'}")
        
        # 统计主要始发地
        top_origins = filtered['origin'].value_counts().head(5)
        print(f"  主要始发地: {dict(top_origins)}")
    
    # 3. 测试组合筛选的一致性
    print("\n🎯 3. 组合筛选一致性测试")
    
    # 测试：广州 + 出口
    test_origin = '广州'
    test_direction = '出口'
    
    print(f"\n测试组合: {test_origin} + {test_direction}")
    
    filtered = routes_df[
        (routes_df['origin'] == test_origin) & 
        (routes_df['direction'] == test_direction)
    ]
    
    list_count = len(filtered)
    
    # 计算地图可显示的航线数
    map_displayable = 0
    for idx, row in filtered.iterrows():
        origin_coords = get_airport_coords(row['origin'])
        dest_coords = get_airport_coords(row['destination'])
        if origin_coords and dest_coords:
            map_displayable += 1
    
    print(f"  列表显示: {list_count} 条")
    print(f"  地图显示: {map_displayable} 条")
    print(f"  一致性: {'✅' if list_count == map_displayable else '❌'}")
    
    # 显示具体航线
    if len(filtered) <= 10:
        print(f"  具体航线:")
        for idx, row in filtered.iterrows():
            print(f"    {row['origin']} -> {row['destination']} ({row['airline']})")
    
    # 4. 检查数据逻辑的合理性
    print("\n🧐 4. 数据逻辑合理性检查")
    
    # 检查是否存在同一航线既是出口又是进口的情况
    route_directions = defaultdict(set)
    
    for idx, row in routes_df.iterrows():
        route_key = f"{row['origin']}-{row['destination']}"
        route_directions[route_key].add(row['direction'])
    
    both_directions = [route for route, dirs in route_directions.items() if len(dirs) > 1]
    
    print(f"同时有出口和进口的航线: {len(both_directions)} 条")
    if both_directions:
        print("示例:")
        for route in both_directions[:5]:
            print(f"  {route}")
    
    # 5. 检查反向航线的存在
    print("\n🔄 5. 反向航线检查")
    
    reverse_routes = 0
    for route_key in route_directions.keys():
        origin, destination = route_key.split('-', 1)
        reverse_key = f"{destination}-{origin}"
        if reverse_key in route_directions:
            reverse_routes += 1
    
    # 每对会被计算两次
    actual_reverse_pairs = reverse_routes // 2
    total_unique_routes = len(route_directions)
    
    print(f"有反向航线的航线对: {actual_reverse_pairs}")
    print(f"总航线数: {total_unique_routes}")
    print(f"反向航线比例: {actual_reverse_pairs/total_unique_routes*100:.1f}%")
    
    # 6. 数据完整性总结
    print("\n📋 6. 数据完整性总结")
    
    # 统计所有航线的坐标情况
    total_with_coords = 0
    total_without_coords = 0
    
    for idx, row in routes_df.iterrows():
        origin_coords = get_airport_coords(row['origin'])
        dest_coords = get_airport_coords(row['destination'])
        
        if origin_coords and dest_coords:
            total_with_coords += 1
        else:
            total_without_coords += 1
    
    print(f"总航线数: {len(routes_df)}")
    print(f"有完整坐标: {total_with_coords} 条 ({total_with_coords/len(routes_df)*100:.1f}%)")
    print(f"缺失坐标: {total_without_coords} 条 ({total_without_coords/len(routes_df)*100:.1f}%)")
    
    # 7. Web界面显示建议
    print("\n💡 7. Web界面显示建议")
    
    suggestions = []
    
    if total_without_coords > 0:
        suggestions.append(f"⚠️  有{total_without_coords}条航线缺失坐标，建议在界面上明确说明")
    
    if actual_reverse_pairs == 0:
        suggestions.append("ℹ️  数据中没有往返航线对，这是正常的（出口和进口是单独记录的）")
    
    if len(both_directions) > 0:
        suggestions.append(f"ℹ️  有{len(both_directions)}条航线同时标记为出口和进口，需要确认数据逻辑")
    
    if total_with_coords == len(routes_df):
        suggestions.append("✅ 所有航线都有完整坐标，地图显示数量应该与列表一致")
    
    if suggestions:
        for suggestion in suggestions:
            print(f"  {suggestion}")
    else:
        print("  ✅ 数据逻辑正常，Web界面显示应该一致")
    
    return {
        'total_routes': len(routes_df),
        'routes_with_coords': total_with_coords,
        'routes_without_coords': total_without_coords,
        'reverse_pairs': actual_reverse_pairs,
        'both_direction_routes': len(both_directions)
    }

if __name__ == "__main__":
    result = test_web_filter_consistency()
    print(f"\n🎯 测试完成")
    print(f"结论: Web界面的筛选逻辑应该保持列表和地图显示的一致性")