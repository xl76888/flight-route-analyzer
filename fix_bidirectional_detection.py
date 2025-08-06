import pandas as pd
from fix_parser import parse_excel_route_data

def analyze_bidirectional_routes():
    """分析并修复双向航线检测逻辑"""
    
    # 加载数据
    file_path = "data/大陆航司全货机航线.xlsx"
    routes_df = parse_excel_route_data(file_path)
    
    print(f"总数据量: {len(routes_df)}")
    print(f"列名: {list(routes_df.columns)}")
    
    # 构建route_stats（模拟web_app.py中的逻辑）
    route_stats = {}
    
    print("\n=== 构建route_stats ===")
    for idx, row in routes_df.iterrows():
        route_key = f"{row['origin']}-{row['destination']}"
        if route_key not in route_stats:
            route_stats[route_key] = {'count': 0, 'airlines': set(), 'directions': set()}
        route_stats[route_key]['count'] += 1
        route_stats[route_key]['airlines'].add(row['airline'])
        route_stats[route_key]['directions'].add(row.get('direction', '出口'))
    
    print(f"route_stats中的航线数量: {len(route_stats)}")
    
    # 检测双向航线
    bidirectional_routes = []
    all_route_keys = list(route_stats.keys())
    
    print("\n=== 检测双向航线 ===")
    for route_key in all_route_keys:
        # 安全地分割航线键，只分割第一个'-'
        parts = route_key.split('-', 1)
        if len(parts) != 2:
            print(f"警告：无法解析航线键: {route_key}")
            continue
        origin, destination = parts
        reverse_route_key = f"{destination}-{origin}"
        
        if reverse_route_key in route_stats:
            # 找到双向航线
            bidirectional_routes.append({
                'forward': route_key,
                'reverse': reverse_route_key,
                'forward_count': route_stats[route_key]['count'],
                'reverse_count': route_stats[reverse_route_key]['count'],
                'forward_airlines': list(route_stats[route_key]['airlines']),
                'reverse_airlines': list(route_stats[reverse_route_key]['airlines']),
                'forward_directions': list(route_stats[route_key]['directions']),
                'reverse_directions': list(route_stats[reverse_route_key]['directions'])
            })
    
    # 去重（因为A-B和B-A会被重复计算）
    unique_bidirectional = []
    processed_pairs = set()
    
    for route in bidirectional_routes:
        forward = route['forward']
        reverse = route['reverse']
        pair = tuple(sorted([forward, reverse]))
        
        if pair not in processed_pairs:
            unique_bidirectional.append(route)
            processed_pairs.add(pair)
    
    print(f"发现双向航线对数量: {len(unique_bidirectional)}")
    
    # 打印双向航线详情
    print("\n=== 双向航线详情 ===")
    for i, route in enumerate(unique_bidirectional, 1):
        print(f"{i}. {route['forward']} <-> {route['reverse']}")
        print(f"   正向: {route['forward_count']}班, 航司: {route['forward_airlines']}, 方向: {route['forward_directions']}")
        print(f"   反向: {route['reverse_count']}班, 航司: {route['reverse_airlines']}, 方向: {route['reverse_directions']}")
        print()
    
    # 验证web_app.py中的检测逻辑
    print("\n=== 验证web_app.py检测逻辑 ===")
    detected_count = 0
    
    for idx, row in routes_df.iterrows():
        route_key = f"{row['origin']}-{row['destination']}"
        reverse_route_key = f"{row['destination']}-{row['origin']}"
        is_bidirectional = reverse_route_key in route_stats
        
        if is_bidirectional:
            detected_count += 1
            if detected_count <= 5:  # 只打印前5个
                print(f"检测到双向航线: {route_key} (反向: {reverse_route_key})")
    
    print(f"web_app.py逻辑检测到的双向航线记录数: {detected_count}")
    print(f"实际双向航线对数: {len(unique_bidirectional)}")
    
    # 分析为什么可能检测不到
    print("\n=== 问题分析 ===")
    
    # 检查数据中的方向分布
    direction_counts = routes_df['direction'].value_counts()
    print(f"方向分布: {dict(direction_counts)}")
    
    # 检查是否有相同origin-destination但不同方向的记录
    route_direction_stats = {}
    for idx, row in routes_df.iterrows():
        route_key = f"{row['origin']}-{row['destination']}"
        direction = row.get('direction', '出口')
        
        if route_key not in route_direction_stats:
            route_direction_stats[route_key] = set()
        route_direction_stats[route_key].add(direction)
    
    # 找出同一航线有多个方向的情况
    multi_direction_routes = {k: v for k, v in route_direction_stats.items() if len(v) > 1}
    print(f"\n同一航线有多个方向的情况: {len(multi_direction_routes)}")
    for route, directions in list(multi_direction_routes.items())[:5]:
        print(f"  {route}: {directions}")
    
    return {
        'total_routes': len(routes_df),
        'unique_route_keys': len(route_stats),
        'bidirectional_pairs': len(unique_bidirectional),
        'detected_by_webapp': detected_count,
        'bidirectional_details': unique_bidirectional
    }

if __name__ == "__main__":
    result = analyze_bidirectional_routes()
    print(f"\n=== 总结 ===")
    print(f"总航线记录数: {result['total_routes']}")
    print(f"唯一航线数: {result['unique_route_keys']}")
    print(f"双向航线对数: {result['bidirectional_pairs']}")
    print(f"web_app检测到的双向记录数: {result['detected_by_webapp']}")