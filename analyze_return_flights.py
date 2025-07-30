#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析原始数据中的回程航线记录
"""

import pandas as pd
from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
from collections import defaultdict, Counter
import re

def analyze_return_flights():
    """分析原始数据中的回程航线记录"""
    print("🔍 分析原始数据中的回程航线记录")
    print("=" * 60)
    
    # 1. 首先查看原始Excel文件的结构
    print("📂 1. 原始Excel文件结构分析")
    
    try:
        # 读取原始Excel文件
        df_raw = pd.read_excel('data/大陆航司全货机航线.xlsx')
        print(f"原始数据形状: {df_raw.shape}")
        print(f"列名: {list(df_raw.columns)}")
        
        # 检查出口和进口航线列的内容
        export_routes_col = '出口航线'
        import_routes_col = '进口航线'
        
        if export_routes_col in df_raw.columns:
            export_non_null = df_raw[export_routes_col].notna().sum()
            print(f"\n出口航线非空记录: {export_non_null} 条")
            
            # 显示一些出口航线的示例
            export_samples = df_raw[df_raw[export_routes_col].notna()][export_routes_col].head(5)
            print("出口航线示例:")
            for i, route in enumerate(export_samples):
                print(f"  {i+1}. {route}")
        
        if import_routes_col in df_raw.columns:
            import_non_null = df_raw[import_routes_col].notna().sum()
            print(f"\n进口航线非空记录: {import_non_null} 条")
            
            # 显示一些进口航线的示例
            import_samples = df_raw[df_raw[import_routes_col].notna()][import_routes_col].head(5)
            print("进口航线示例:")
            for i, route in enumerate(import_samples):
                print(f"  {i+1}. {route}")
        
        # 2. 分析同一架飞机的出口和进口记录
        print("\n✈️ 2. 同一架飞机的出口和进口记录分析")
        
        aircraft_routes = defaultdict(lambda: {'出口': [], '进口': []})
        
        for idx, row in df_raw.iterrows():
            reg_no = str(row.get('注册号', '')).strip()
            airline = str(row.get('航司', '')).strip()
            aircraft_type = str(row.get('机型', '')).strip()
            
            export_route = row.get(export_routes_col, '')
            import_route = row.get(import_routes_col, '')
            
            # 使用注册号作为飞机标识
            if reg_no and reg_no != 'nan' and reg_no != '':
                aircraft_key = f"{airline}-{reg_no}"
                
                if pd.notna(export_route) and str(export_route).strip():
                    aircraft_routes[aircraft_key]['出口'].append(str(export_route).strip())
                
                if pd.notna(import_route) and str(import_route).strip():
                    aircraft_routes[aircraft_key]['进口'].append(str(import_route).strip())
        
        # 统计有出口和进口记录的飞机
        both_directions = 0
        export_only = 0
        import_only = 0
        
        print(f"\n分析的飞机数量: {len(aircraft_routes)}")
        
        for aircraft, routes in aircraft_routes.items():
            has_export = len(routes['出口']) > 0
            has_import = len(routes['进口']) > 0
            
            if has_export and has_import:
                both_directions += 1
            elif has_export:
                export_only += 1
            elif has_import:
                import_only += 1
        
        print(f"既有出口又有进口的飞机: {both_directions} 架")
        print(f"只有出口的飞机: {export_only} 架")
        print(f"只有进口的飞机: {import_only} 架")
        
        # 显示一些既有出口又有进口的飞机示例
        if both_directions > 0:
            print("\n🔄 既有出口又有进口的飞机示例:")
            count = 0
            for aircraft, routes in aircraft_routes.items():
                if len(routes['出口']) > 0 and len(routes['进口']) > 0 and count < 5:
                    print(f"\n  飞机: {aircraft}")
                    print(f"    出口航线: {routes['出口'][:2]}")
                    print(f"    进口航线: {routes['进口'][:2]}")
                    count += 1
        
        # 3. 分析航线模式
        print("\n🛣️ 3. 航线模式分析")
        
        # 解析后的数据分析
        routes_df = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
        routes_df = clean_route_data(routes_df, enable_deduplication=False)
        
        print(f"解析后总航线数: {len(routes_df)}")
        
        # 按航司分析出口和进口分布
        airline_analysis = defaultdict(lambda: {'出口': 0, '进口': 0, '城市对': set()})
        
        for idx, row in routes_df.iterrows():
            airline = row['airline']
            direction = row['direction']
            origin = row['origin']
            destination = row['destination']
            
            airline_analysis[airline][direction] += 1
            
            # 记录城市对（不区分方向）
            city_pair = tuple(sorted([origin, destination]))
            airline_analysis[airline]['城市对'].add(city_pair)
        
        print("\n各航司的出口/进口分布:")
        for airline, stats in airline_analysis.items():
            export_count = stats['出口']
            import_count = stats['进口']
            city_pairs = len(stats['城市对'])
            total = export_count + import_count
            
            print(f"  {airline}: 总计{total}条 (出口{export_count}, 进口{import_count}, 城市对{city_pairs})")
            
            # 分析是否可能存在往返
            if export_count > 0 and import_count > 0:
                print(f"    ✅ 有出口和进口记录")
            elif export_count > 0:
                print(f"    ⚠️  只有出口记录")
            elif import_count > 0:
                print(f"    ⚠️  只有进口记录")
        
        # 4. 分析可能的往返模式
        print("\n🔄 4. 往返模式分析")
        
        # 检查是否存在A->B的出口和B->A的进口
        route_pairs = defaultdict(lambda: {'出口': [], '进口': []})
        
        for idx, row in routes_df.iterrows():
            origin = row['origin']
            destination = row['destination']
            direction = row['direction']
            airline = row['airline']
            
            route_key = f"{origin}-{destination}"
            route_pairs[route_key][direction].append(airline)
        
        # 寻找往返航线
        potential_returns = []
        
        for route_key, directions in route_pairs.items():
            origin, destination = route_key.split('-', 1)
            reverse_key = f"{destination}-{origin}"
            
            if reverse_key in route_pairs:
                # 检查是否有出口和进口的组合
                forward_export = len(directions['出口']) > 0
                forward_import = len(directions['进口']) > 0
                reverse_export = len(route_pairs[reverse_key]['出口']) > 0
                reverse_import = len(route_pairs[reverse_key]['进口']) > 0
                
                # 理想的往返模式：A->B出口，B->A进口
                if forward_export and reverse_import:
                    potential_returns.append({
                        'forward': route_key,
                        'reverse': reverse_key,
                        'type': '标准往返',
                        'forward_airlines': directions['出口'],
                        'reverse_airlines': route_pairs[reverse_key]['进口']
                    })
                
                # 或者：A->B进口，B->A出口
                elif forward_import and reverse_export:
                    potential_returns.append({
                        'forward': route_key,
                        'reverse': reverse_key,
                        'type': '反向往返',
                        'forward_airlines': directions['进口'],
                        'reverse_airlines': route_pairs[reverse_key]['出口']
                    })
        
        print(f"发现的潜在往返航线: {len(potential_returns)} 对")
        
        if potential_returns:
            print("\n往返航线示例:")
            for i, return_route in enumerate(potential_returns[:5]):
                print(f"  {i+1}. {return_route['forward']} <-> {return_route['reverse']} ({return_route['type']})")
                print(f"     正向航司: {return_route['forward_airlines'][:3]}")
                print(f"     反向航司: {return_route['reverse_airlines'][:3]}")
        
        # 5. 分析数据逻辑
        print("\n🧐 5. 数据逻辑分析")
        
        # 统计各种情况
        total_routes = len(route_pairs)
        routes_with_returns = len(potential_returns)
        
        print(f"总航线数: {total_routes}")
        print(f"有往返的航线对: {routes_with_returns}")
        print(f"往返比例: {routes_with_returns/total_routes*100:.1f}%")
        
        # 6. 结论
        print("\n📋 6. 结论")
        
        conclusions = []
        
        if both_directions > 0:
            conclusions.append(f"✅ 原始数据中有{both_directions}架飞机既有出口又有进口记录")
        
        if len(potential_returns) > 0:
            conclusions.append(f"✅ 发现{len(potential_returns)}对潜在的往返航线")
        else:
            conclusions.append("❌ 没有发现明显的往返航线模式")
        
        if export_only > import_only * 2:
            conclusions.append("⚠️  出口航线明显多于进口航线")
        
        # 分析可能的原因
        print("\n可能的解释:")
        explanations = [
            "1. 货运航线通常是单向的，飞机可能空载返回或载其他货物",
            "2. 数据记录的是主要货运航线，回程可能是客运或其他用途",
            "3. 出口和进口可能在不同的时间段记录，不是同一次飞行",
            "4. 部分航线可能是中转航线，不直接返回起点"
        ]
        
        for conclusion in conclusions:
            print(f"  {conclusion}")
        
        print("\n💡 可能的解释:")
        for explanation in explanations:
            print(f"  {explanation}")
        
        return {
            'total_aircraft': len(aircraft_routes),
            'both_directions_aircraft': both_directions,
            'export_only_aircraft': export_only,
            'import_only_aircraft': import_only,
            'potential_returns': len(potential_returns),
            'total_routes': total_routes
        }
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        return None

if __name__ == "__main__":
    result = analyze_return_flights()
    if result:
        print(f"\n📊 分析完成")
        print(f"飞机往返情况: {result['both_directions_aircraft']}/{result['total_aircraft']}")
        print(f"航线往返情况: {result['potential_returns']}/{result['total_routes']}")