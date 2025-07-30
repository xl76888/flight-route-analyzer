import pandas as pd
import re
from typing import List, Dict, Any

def debug_parse_excel_route_data(file_path: str):
    """调试版本的Excel解析函数"""
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        print(f"原始数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        
        all_routes = []
        processed_records = 0
        records_with_export = 0
        records_with_import = 0
        
        # 遍历每一行
        for idx, row in df.iterrows():
            airline = row.get('航司', '')
            reg_no = row.get('注册号', '')
            aircraft = row.get('机型', '')
            age = row.get('机龄', '')
            export_routes = row.get('出口航线', '')
            import_routes = row.get('进口航线', '')
            remarks = row.get('备注', '')
            
            # 跳过航司为空的行
            if pd.isna(airline) or str(airline).strip() == '':
                continue
            
            processed_records += 1
            
            # 处理出口航线
            if pd.notna(export_routes) and str(export_routes).strip() and str(export_routes) != 'nan':
                export_route_str = str(export_routes).strip()
                print(f"第{idx+1}行 {airline} 出口航线: {export_route_str}")
                
                if export_route_str and export_route_str not in ['无近一个月的飞行记录', '停场维修', '']:
                    records_with_export += 1
                    # 解析航线字符串
                    routes = parse_route_string(export_route_str)
                    print(f"  解析结果: {routes}")
                    for origin, destination in routes:
                        all_routes.append({
                            'airline': str(airline).strip(),
                            'reg': str(reg_no).strip() if pd.notna(reg_no) else '',
                            'aircraft': str(aircraft).strip() if pd.notna(aircraft) else '',
                            'age': str(age).strip() if pd.notna(age) else '',
                            'origin': origin,
                            'destination': destination,
                            'direction': '出口',
                            'remarks': str(remarks).strip() if pd.notna(remarks) else ''
                        })
            
            # 处理进口航线
            if pd.notna(import_routes) and str(import_routes).strip() and str(import_routes) != 'nan':
                import_route_str = str(import_routes).strip()
                print(f"第{idx+1}行 {airline} 进口航线: {import_route_str}")
                
                if import_route_str and import_route_str not in ['无近一个月的飞行记录', '停场维修', '']:
                    records_with_import += 1
                    # 解析航线字符串
                    routes = parse_route_string(import_route_str)
                    print(f"  解析结果: {routes}")
                    for origin, destination in routes:
                        all_routes.append({
                            'airline': str(airline).strip(),
                            'reg': str(reg_no).strip() if pd.notna(reg_no) else '',
                            'aircraft': str(aircraft).strip() if pd.notna(aircraft) else '',
                            'age': str(age).strip() if pd.notna(age) else '',
                            'origin': origin,
                            'destination': destination,
                            'direction': '进口',
                            'remarks': str(remarks).strip() if pd.notna(remarks) else ''
                        })
            
            # 只处理前20行进行调试
            if processed_records >= 20:
                break
        
        print(f"\n=== 调试统计 ===")
        print(f"处理的记录数: {processed_records}")
        print(f"有出口航线的记录: {records_with_export}")
        print(f"有进口航线的记录: {records_with_import}")
        print(f"解析出的航线总数: {len(all_routes)}")
        
        result_df = pd.DataFrame(all_routes)
        return result_df
        
    except Exception as e:
        print(f"解析Excel文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def parse_route_string(route_str: str) -> List[tuple]:
    """解析航线字符串，提取起点和终点"""
    routes = []
    
    # 清理字符串
    route_str = route_str.strip()
    
    # 常见的分隔符
    separators = ['—', '-', '→', '->', '至', '到']
    
    # 尝试用不同分隔符分割
    for sep in separators:
        if sep in route_str:
            parts = route_str.split(sep)
            if len(parts) == 2:
                origin = clean_city_name(parts[0].strip())
                destination = clean_city_name(parts[1].strip())
                if origin and destination:
                    routes.append((origin, destination))
                break
    
    # 如果没有找到分隔符，尝试其他方法
    if not routes:
        # 检查是否包含中转信息（如：A-B-C）
        for sep in separators:
            if route_str.count(sep) > 1:
                parts = route_str.split(sep)
                for i in range(len(parts) - 1):
                    origin = clean_city_name(parts[i].strip())
                    destination = clean_city_name(parts[i + 1].strip())
                    if origin and destination:
                        routes.append((origin, destination))
                break
    
    return routes

def clean_city_name(city_name: str) -> str:
    """清理城市名称"""
    if not city_name:
        return ''
    
    # 移除常见的后缀
    suffixes_to_remove = ['机场', '国际机场', '机场', '空港', 'Airport', 'International']
    
    cleaned = city_name.strip()
    
    for suffix in suffixes_to_remove:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)].strip()
    
    # 移除括号及其内容
    cleaned = re.sub(r'\([^)]*\)', '', cleaned).strip()
    
    return cleaned

if __name__ == "__main__":
    # 调试解析函数
    file_path = "D:\\flight_tool\\data\\大陆航司全货机航线.xlsx"
    result = debug_parse_excel_route_data(file_path)
    
    if not result.empty:
        print(f"\n=== 解析结果 ===")
        print(result)
    else:
        print("没有解析到任何航线数据")