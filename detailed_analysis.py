import pandas as pd

def detailed_analysis():
    """详细分析Excel文件中的航线数据分布"""
    file_path = "D:\\flight_tool\\data\\大陆航司全货机航线.xlsx"
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        print(f"=== 详细数据分析 ===")
        print(f"总行数: {len(df)}")
        
        # 分析出口航线
        print(f"\n=== 出口航线分析 ===")
        export_routes = df['出口航线'].dropna()
        print(f"非空出口航线记录数: {len(export_routes)}")
        
        # 统计出口航线的唯一值
        export_unique = export_routes.unique()
        print(f"出口航线唯一值数量: {len(export_unique)}")
        
        # 分类统计
        valid_export = []
        invalid_export = []
        
        for route in export_unique:
            route_str = str(route).strip()
            if route_str in ['无近一个月的飞行记录', '停场维修', '']:
                invalid_export.append(route_str)
            else:
                valid_export.append(route_str)
        
        print(f"有效出口航线数: {len(valid_export)}")
        print(f"无效出口航线数: {len(invalid_export)}")
        print(f"无效航线类型: {invalid_export}")
        
        # 显示前20个有效出口航线
        print(f"\n前20个有效出口航线:")
        for i, route in enumerate(valid_export[:20]):
            print(f"  {i+1}: {route}")
        
        # 分析进口航线
        print(f"\n=== 进口航线分析 ===")
        import_routes = df['进口航线'].dropna()
        print(f"非空进口航线记录数: {len(import_routes)}")
        
        # 统计进口航线的唯一值
        import_unique = import_routes.unique()
        print(f"进口航线唯一值数量: {len(import_unique)}")
        
        # 分类统计
        valid_import = []
        invalid_import = []
        
        for route in import_unique:
            route_str = str(route).strip()
            if route_str in ['无近一个月的飞行记录', '停场维修', '']:
                invalid_import.append(route_str)
            else:
                valid_import.append(route_str)
        
        print(f"有效进口航线数: {len(valid_import)}")
        print(f"无效进口航线数: {len(invalid_import)}")
        print(f"无效航线类型: {invalid_import}")
        
        # 显示前20个有效进口航线
        print(f"\n前20个有效进口航线:")
        for i, route in enumerate(valid_import[:20]):
            print(f"  {i+1}: {route}")
        
        # 分析每个航司的数据分布
        print(f"\n=== 航司数据分布分析 ===")
        airline_stats = {}
        
        for airline in df['航司'].dropna().unique():
            airline_data = df[df['航司'] == airline]
            total_records = len(airline_data)
            
            # 统计该航司的有效航线
            valid_export_count = 0
            valid_import_count = 0
            
            for _, row in airline_data.iterrows():
                export_route = str(row.get('出口航线', '')).strip()
                import_route = str(row.get('进口航线', '')).strip()
                
                if export_route and export_route not in ['无近一个月的飞行记录', '停场维修', '', 'nan']:
                    valid_export_count += 1
                
                if import_route and import_route not in ['无近一个月的飞行记录', '停场维修', '', 'nan']:
                    valid_import_count += 1
            
            airline_stats[airline] = {
                'total_records': total_records,
                'valid_export': valid_export_count,
                'valid_import': valid_import_count
            }
        
        for airline, stats in airline_stats.items():
            print(f"  {airline}:")
            print(f"    总记录数: {stats['total_records']}")
            print(f"    有效出口航线记录: {stats['valid_export']}")
            print(f"    有效进口航线记录: {stats['valid_import']}")
            print()
        
        # 计算理论上应该解析出的航线数
        total_valid_routes = sum(stats['valid_export'] + stats['valid_import'] for stats in airline_stats.values())
        print(f"=== 总结 ===")
        print(f"理论上应该解析出的航线记录数: {total_valid_routes}")
        print(f"有效出口航线唯一值: {len(valid_export)}")
        print(f"有效进口航线唯一值: {len(valid_import)}")
        print(f"总有效航线唯一值: {len(valid_export) + len(valid_import)}")
        
    except Exception as e:
        print(f"分析时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    detailed_analysis()