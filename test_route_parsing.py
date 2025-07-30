import pandas as pd
import re
from typing import List, Dict, Any

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
            elif len(parts) > 2:
                # 处理多段航线（如：A—B—C）
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
    suffixes_to_remove = ['机场', '国际机场', '空港', 'Airport', 'International']
    
    cleaned = city_name.strip()
    
    for suffix in suffixes_to_remove:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)].strip()
    
    # 移除括号及其内容
    cleaned = re.sub(r'\([^)]*\)', '', cleaned).strip()
    
    return cleaned

def test_route_parsing():
    """测试航线解析功能"""
    print("=== 测试航线解析功能 ===")
    
    # 测试用例
    test_routes = [
        "成都双流—阿姆斯特丹",
        "浦东—阿姆斯特丹", 
        "浦东—巴黎",
        "浦东—米兰",
        "浦东—纽约",
        "浦东—列日—马德里巴拉哈斯",
        "浦东—安克雷奇—芝加哥",
        "杭州—列日—马德里巴拉哈斯",
        "北京首都—马德里巴拉哈斯"
    ]
    
    for route_str in test_routes:
        parsed = parse_route_string(route_str)
        print(f"原始: {route_str}")
        print(f"解析: {parsed}")
        print()
    
    # 检查国货航的实际解析情况
    print("=== 检查国货航实际解析情况 ===")
    
    excel_df = pd.read_excel('D:\\flight_tool\\data\\大陆航司全货机航线.xlsx')
    
    # 找到国货航数据范围
    guohang_start = None
    for idx, row in excel_df.iterrows():
        if pd.notna(row.get('航司', '')) and str(row.get('航司', '')).strip() == '国货航':
            guohang_start = idx
            break
    
    if guohang_start is not None:
        # 找到下一个航司
        next_airline = None
        for idx in range(guohang_start + 1, len(excel_df)):
            if pd.notna(excel_df.iloc[idx].get('航司', '')) and str(excel_df.iloc[idx].get('航司', '')).strip() != '':
                next_airline = idx
                break
        
        if next_airline is None:
            next_airline = len(excel_df)
        
        guohang_data = excel_df.iloc[guohang_start:next_airline]
        
        total_routes = 0
        valid_routes = 0
        
        for idx, row in guohang_data.iterrows():
            export_route = row.get('出口航线', '')
            import_route = row.get('进口航线', '')
            
            if pd.notna(export_route) and str(export_route).strip():
                export_str = str(export_route).strip()
                if export_str not in ['无近一个月的飞行记录', '停场维修', '']:
                    parsed_export = parse_route_string(export_str)
                    total_routes += len(parsed_export)
                    if parsed_export:
                        valid_routes += len(parsed_export)
                        print(f"出口: {export_str} -> {parsed_export}")
            
            if pd.notna(import_route) and str(import_route).strip():
                import_str = str(import_route).strip()
                if import_str not in ['无近一个月的飞行记录', '停场维修', '']:
                    parsed_import = parse_route_string(import_str)
                    total_routes += len(parsed_import)
                    if parsed_import:
                        valid_routes += len(parsed_import)
                        print(f"进口: {import_str} -> {parsed_import}")
        
        print(f"\n总计应解析出 {total_routes} 条航线")
        print(f"有效解析 {valid_routes} 条航线")

if __name__ == "__main__":
    test_route_parsing()