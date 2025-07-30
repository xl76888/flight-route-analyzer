from fix_parser import parse_excel_route_data, parse_route_string
from data_cleaner import clean_route_data
import pandas as pd

def analyze_data_expansion():
    """分析数据从543条扩展到699条的详细过程"""
    
    print("=== 数据扩展分析报告 ===")
    
    # 1. 读取原始Excel数据
    file_path = 'data/大陆航司全货机航线.xlsx'
    original_df = pd.read_excel(file_path)
    print(f"\n1. 原始Excel数据：{len(original_df)} 行")
    
    # 2. 统计有航线数据的行数
    rows_with_routes = 0
    total_route_segments = 0
    
    for idx, row in original_df.iterrows():
        export_routes = row.get('出口航线', '')
        import_routes = row.get('进口航线', '')
        
        has_export = pd.notna(export_routes) and str(export_routes).strip() not in ['', 'nan', '无近一个月的飞行记录', '停场维修']
        has_import = pd.notna(import_routes) and str(import_routes).strip() not in ['', 'nan', '无近一个月的飞行记录', '停场维修']
        
        if has_export or has_import:
            rows_with_routes += 1
            
            # 统计每行产生的航线段数
            if has_export:
                export_segments = parse_route_string(str(export_routes))
                total_route_segments += len(export_segments)
                if len(export_segments) > 1:
                    print(f"  行{idx+1} 出口航线 '{export_routes}' 解析为 {len(export_segments)} 段")
            
            if has_import:
                import_segments = parse_route_string(str(import_routes))
                total_route_segments += len(import_segments)
                if len(import_segments) > 1:
                    print(f"  行{idx+1} 进口航线 '{import_routes}' 解析为 {len(import_segments)} 段")
    
    print(f"\n2. 有航线数据的行数：{rows_with_routes} 行")
    print(f"3. 解析后的航线段总数：{total_route_segments} 段")
    
    # 3. 使用解析器处理数据
    parsed_df = parse_excel_route_data(file_path)
    print(f"\n4. 解析器输出的记录数：{len(parsed_df)} 条")
    
    # 4. 数据清理后的记录数
    cleaned_df = clean_route_data(parsed_df, enable_deduplication=False)
    print(f"\n5. 清理后的记录数：{len(cleaned_df)} 条")
    
    # 5. 分析数据扩展的原因
    print(f"\n=== 数据扩展原因分析 ===")
    print(f"原始Excel行数：{len(original_df)}")
    print(f"有效航线行数：{rows_with_routes}")
    print(f"解析后航线数：{len(parsed_df)}")
    print(f"最终显示数：{len(cleaned_df)}")
    
    expansion_ratio = len(parsed_df) / rows_with_routes if rows_with_routes > 0 else 0
    print(f"\n扩展倍数：{expansion_ratio:.2f}x")
    
    print(f"\n=== 扩展原因说明 ===")
    print("1. 出口/进口分离：每行数据可能同时包含出口和进口航线，会被分别处理")
    print("2. 多段航线解析：如'A—B—C'会被解析为'A→B'和'B→C'两条记录")
    print("3. 数据清理：移除无效城市、添加坐标等处理可能影响最终数量")
    
    # 6. 详细分析多段航线
    print(f"\n=== 多段航线详细分析 ===")
    multi_segment_count = 0
    
    for idx, row in original_df.iterrows():
        export_routes = row.get('出口航线', '')
        import_routes = row.get('进口航线', '')
        
        if pd.notna(export_routes) and str(export_routes).strip():
            segments = parse_route_string(str(export_routes))
            if len(segments) > 1:
                multi_segment_count += 1
                print(f"  出口航线: '{export_routes}' → {len(segments)} 段")
        
        if pd.notna(import_routes) and str(import_routes).strip():
            segments = parse_route_string(str(import_routes))
            if len(segments) > 1:
                multi_segment_count += 1
                print(f"  进口航线: '{import_routes}' → {len(segments)} 段")
    
    print(f"\n包含多段航线的记录数：{multi_segment_count}")
    
    return {
        'original_rows': len(original_df),
        'rows_with_routes': rows_with_routes,
        'parsed_routes': len(parsed_df),
        'final_routes': len(cleaned_df),
        'expansion_ratio': expansion_ratio
    }

if __name__ == "__main__":
    analyze_data_expansion()