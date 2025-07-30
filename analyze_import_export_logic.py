#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析进出口数据逻辑问题
"""

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
import pandas as pd
from collections import defaultdict

def analyze_import_export_logic():
    """分析进出口数据逻辑问题"""
    print("🔍 分析进出口数据逻辑问题")
    print("=" * 60)
    
    # 加载原始数据
    print("📂 加载原始数据...")
    routes_df = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    print(f"原始记录数: {len(routes_df)}")
    
    # 清理数据
    routes_df = clean_route_data(routes_df, enable_deduplication=False)
    print(f"清理后记录数: {len(routes_df)}")
    
    # 1. 检查原始数据中的进出口标记
    print("\n📊 1. 进出口数据分布")
    direction_counts = routes_df['direction'].value_counts()
    print("进出口统计:")
    for direction, count in direction_counts.items():
        print(f"  {direction}: {count} 条 ({count/len(routes_df)*100:.1f}%)")
    
    # 2. 分析具体的航线对
    print("\n🔄 2. 航线对分析")
    
    # 创建航线对字典
    route_pairs = defaultdict(lambda: {'出口': [], '进口': []})
    
    for idx, row in routes_df.iterrows():
        origin = row['origin']
        destination = row['destination']
        direction = row['direction']
        
        # 使用起点-终点作为键
        route_key = f"{origin}-{destination}"
        route_pairs[route_key][direction].append({
            'airline': row['airline'],
            'aircraft': row['aircraft'],
            'frequency': row.get('frequency', 1)
        })
    
    # 统计航线对情况
    total_routes = len(route_pairs)
    routes_with_both = 0
    routes_export_only = 0
    routes_import_only = 0
    
    print(f"\n总航线对数: {total_routes}")
    
    for route_key, directions in route_pairs.items():
        has_export = len(directions['出口']) > 0
        has_import = len(directions['进口']) > 0
        
        if has_export and has_import:
            routes_with_both += 1
        elif has_export:
            routes_export_only += 1
        elif has_import:
            routes_import_only += 1
    
    print(f"双向航线对: {routes_with_both} ({routes_with_both/total_routes*100:.1f}%)")
    print(f"仅出口航线: {routes_export_only} ({routes_export_only/total_routes*100:.1f}%)")
    print(f"仅进口航线: {routes_import_only} ({routes_import_only/total_routes*100:.1f}%)")
    
    # 3. 检查反向航线
    print("\n🔄 3. 反向航线检查")
    
    reverse_pairs = 0
    for route_key in route_pairs.keys():
        origin, destination = route_key.split('-', 1)
        reverse_key = f"{destination}-{origin}"
        
        if reverse_key in route_pairs:
            reverse_pairs += 1
    
    # 由于每对会被计算两次，所以除以2
    actual_reverse_pairs = reverse_pairs // 2
    print(f"有反向航线的航线对: {actual_reverse_pairs}")
    print(f"反向航线比例: {actual_reverse_pairs/total_routes*100:.1f}%")
    
    # 4. 详细分析几个典型案例
    print("\n🎯 4. 典型案例分析")
    
    # 找出一些有代表性的航线
    sample_routes = []
    
    # 找出口航线最多的几个
    export_routes = [(k, len(v['出口'])) for k, v in route_pairs.items() if len(v['出口']) > 0]
    export_routes.sort(key=lambda x: x[1], reverse=True)
    
    print("\n出口航线最多的路线:")
    for route_key, count in export_routes[:5]:
        origin, destination = route_key.split('-', 1)
        reverse_key = f"{destination}-{origin}"
        
        import_count = len(route_pairs[reverse_key]['进口']) if reverse_key in route_pairs else 0
        
        print(f"  {route_key}: {count} 条出口")
        if import_count > 0:
            print(f"    反向 {reverse_key}: {import_count} 条进口")
        else:
            print(f"    反向 {reverse_key}: 无进口航线")
    
    # 5. 检查数据逻辑合理性
    print("\n🧐 5. 数据逻辑合理性检查")
    
    # 检查是否存在逻辑错误
    logic_issues = []
    
    for route_key, directions in route_pairs.items():
        origin, destination = route_key.split('-', 1)
        
        # 检查出口航线的逻辑
        if len(directions['出口']) > 0:
            # 出口应该是从国内到国外，或者国内到国内
            # 这里需要检查城市分类
            pass
        
        # 检查进口航线的逻辑
        if len(directions['进口']) > 0:
            # 进口应该是从国外到国内
            pass
    
    # 6. 检查始发地的进出口分布
    print("\n🏙️ 6. 主要始发地的进出口分布")
    
    origin_stats = defaultdict(lambda: {'出口': 0, '进口': 0})
    
    for idx, row in routes_df.iterrows():
        origin = row['origin']
        direction = row['direction']
        origin_stats[origin][direction] += 1
    
    # 按总航线数排序
    origin_list = [(origin, stats['出口'] + stats['进口'], stats) 
                   for origin, stats in origin_stats.items()]
    origin_list.sort(key=lambda x: x[1], reverse=True)
    
    print("主要始发地的进出口分布:")
    for origin, total, stats in origin_list[:10]:
        export_count = stats['出口']
        import_count = stats['进口']
        print(f"  {origin}: 总计{total}条 (出口{export_count}, 进口{import_count})")
        
        if export_count > 0 and import_count == 0:
            print(f"    ⚠️  只有出口，无进口")
        elif import_count > 0 and export_count == 0:
            print(f"    ⚠️  只有进口，无出口")
    
    # 7. 检查目的地的进出口分布
    print("\n🎯 7. 主要目的地的进出口分布")
    
    dest_stats = defaultdict(lambda: {'出口': 0, '进口': 0})
    
    for idx, row in routes_df.iterrows():
        destination = row['destination']
        direction = row['direction']
        dest_stats[destination][direction] += 1
    
    # 按总航线数排序
    dest_list = [(dest, stats['出口'] + stats['进口'], stats) 
                 for dest, stats in dest_stats.items()]
    dest_list.sort(key=lambda x: x[1], reverse=True)
    
    print("主要目的地的进出口分布:")
    for dest, total, stats in dest_list[:10]:
        export_count = stats['出口']
        import_count = stats['进口']
        print(f"  {dest}: 总计{total}条 (出口{export_count}, 进口{import_count})")
        
        if export_count > 0 and import_count == 0:
            print(f"    ⚠️  只作为出口目的地")
        elif import_count > 0 and export_count == 0:
            print(f"    ⚠️  只作为进口起点")
    
    # 8. 生成问题总结
    print("\n📋 8. 问题总结")
    
    issues = []
    
    if routes_with_both == 0:
        issues.append("❌ 没有发现任何双向航线对")
    
    if actual_reverse_pairs == 0:
        issues.append("❌ 没有发现任何反向航线")
    
    if routes_export_only > routes_import_only * 2:
        issues.append("⚠️  出口航线数量远超进口航线")
    
    if len(issues) > 0:
        print("发现的问题:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n可能的原因:")
        print("  1. 数据源本身就是单向的（只记录出口或进口）")
        print("  2. 进出口标记逻辑有误")
        print("  3. 数据收集不完整")
        print("  4. 航线本身就是单向的（如货运专线）")
    else:
        print("✅ 数据逻辑正常")
    
    return {
        'total_routes': total_routes,
        'routes_with_both': routes_with_both,
        'routes_export_only': routes_export_only,
        'routes_import_only': routes_import_only,
        'reverse_pairs': actual_reverse_pairs
    }

if __name__ == "__main__":
    result = analyze_import_export_logic()
    print(f"\n📊 分析完成")