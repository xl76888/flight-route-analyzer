import pandas as pd
import re
from typing import List, Dict, Any

def parse_excel_route_data(file_path: str) -> pd.DataFrame:
    """专门解析大陆航司全货机航线.xlsx文件的函数"""
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        print(f"原始数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        
        all_routes = []
        
        # 统计信息
        unique_airlines = df['航司'].dropna().unique()
        total_airlines = len(unique_airlines)
        airlines_with_routes_set = set()
        
        # 遍历每一行，处理分组数据结构
        current_airline = None
        current_reg_no = None
        current_aircraft = None
        current_age = None
        
        for idx, row in df.iterrows():
            airline = row.get('航司', '')
            reg_no = row.get('注册号', '')
            aircraft = row.get('机型', '')
            age = row.get('机龄', '')
            export_routes = row.get('出口航线', '')
            import_routes = row.get('进口航线', '')
            remarks = row.get('备注', '')
            
            # 如果航司不为空，更新当前航司信息
            if pd.notna(airline) and str(airline).strip() != '':
                current_airline = str(airline).strip()
                current_reg_no = str(reg_no).strip() if pd.notna(reg_no) else ''
                current_aircraft = str(aircraft).strip() if pd.notna(aircraft) else ''
                current_age = str(age).strip() if pd.notna(age) else ''
            
            # 如果没有当前航司信息，跳过
            if not current_airline:
                continue
            
            has_routes = False
            
            # 处理出口航线
            if pd.notna(export_routes) and str(export_routes).strip() and str(export_routes) != 'nan':
                export_route_str = str(export_routes).strip()
                if export_route_str and export_route_str not in ['无近一个月的飞行记录', '停场维修', '']:
                    # 解析航线字符串
                    routes = parse_route_string(export_route_str)
                    for route_info in routes:
                        if len(route_info) == 3:  # 多段航线
                            origin, destination, full_route = route_info
                            all_routes.append({
                                'airline': current_airline,
                                'reg': current_reg_no,
                                'aircraft': current_aircraft,
                                'age': current_age,
                                'origin': origin,
                                'destination': destination,
                                'full_route': full_route,  # 保存完整航线信息
                                'direction': '出口',
                                'remarks': str(remarks).strip() if pd.notna(remarks) else ''
                            })
                        else:  # 单段航线
                            origin, destination = route_info
                            all_routes.append({
                                'airline': current_airline,
                                'reg': current_reg_no,
                                'aircraft': current_aircraft,
                                'age': current_age,
                                'origin': origin,
                                'destination': destination,
                                'full_route': f"{origin}—{destination}",  # 单段航线也保存完整信息
                                'direction': '出口',
                                'remarks': str(remarks).strip() if pd.notna(remarks) else ''
                            })
                        has_routes = True
            
            # 处理进口航线
            if pd.notna(import_routes) and str(import_routes).strip() and str(import_routes) != 'nan':
                import_route_str = str(import_routes).strip()
                if import_route_str and import_route_str not in ['无近一个月的飞行记录', '停场维修', '']:
                    # 解析航线字符串
                    routes = parse_route_string(import_route_str)
                    for route_info in routes:
                        if len(route_info) == 3:  # 多段航线
                            origin, destination, full_route = route_info
                            all_routes.append({
                                'airline': current_airline,
                                'reg': current_reg_no,
                                'aircraft': current_aircraft,
                                'age': current_age,
                                'origin': origin,
                                'destination': destination,
                                'full_route': full_route,  # 保存完整航线信息
                                'direction': '进口',
                                'remarks': str(remarks).strip() if pd.notna(remarks) else ''
                            })
                        else:  # 单段航线
                            origin, destination = route_info
                            all_routes.append({
                                'airline': current_airline,
                                'reg': current_reg_no,
                                'aircraft': current_aircraft,
                                'age': current_age,
                                'origin': origin,
                                'destination': destination,
                                'full_route': f"{origin}—{destination}",  # 单段航线也保存完整信息
                                'direction': '进口',
                                'remarks': str(remarks).strip() if pd.notna(remarks) else ''
                            })
                        has_routes = True
            
            # 记录有航线的航司
            if has_routes:
                airlines_with_routes_set.add(current_airline)
        
        # 计算最终统计
        airlines_with_routes = len(airlines_with_routes_set)
        airlines_without_routes = total_airlines - airlines_with_routes
        
        result_df = pd.DataFrame(all_routes)
        
        print(f"\n=== 数据解析完整报告 ===")
        print(f"总记录数: {len(df)}")
        print(f"总航司数: {total_airlines}")
        print(f"有航线数据的航司: {airlines_with_routes}")
        print(f"无航线数据的航司: {airlines_without_routes}")
        print(f"解析出的航线总数: {len(result_df)}")
        
        if not result_df.empty:
            print(f"\n=== 有航线数据的航司统计 ===")
            airline_counts = result_df['airline'].value_counts()
            for airline, count in airline_counts.items():
                print(f"  {airline}: {count} 条航线")
            
            print(f"\n=== 按方向统计 ===")
            direction_counts = result_df['direction'].value_counts()
            for direction, count in direction_counts.items():
                print(f"  {direction}: {count} 条航线")
            
            print(f"\n=== 数据清理摘要 ===")
            print(f"总航线数: {len(result_df)}")
            
            # 统计起点和终点城市
            origins = result_df['origin'].unique()
            destinations = result_df['destination'].unique()
            
            print(f"\n始发地统计:")
            domestic_origins = [city for city in origins if is_domestic_city(city)]
            international_origins = [city for city in origins if not is_domestic_city(city)]
            print(f"  国内城市 ({len(domestic_origins)}): {', '.join(sorted(domestic_origins))}")
            print(f"  国际城市 ({len(international_origins)}): {', '.join(sorted(international_origins))}")
            
            print(f"\n目的地统计:")
            domestic_destinations = [city for city in destinations if is_domestic_city(city)]
            international_destinations = [city for city in destinations if not is_domestic_city(city)]
            print(f"  国内城市 ({len(domestic_destinations)}): {', '.join(sorted(domestic_destinations))}")
            print(f"  国际城市 ({len(international_destinations)}): {', '.join(sorted(international_destinations))}")
        
        print(f"\n=== 数据完整性检查 ===")
        print(f"数据覆盖率: {airlines_with_routes}/{total_airlines} ({airlines_with_routes/total_airlines*100:.1f}%)")
        
        return result_df
        
    except Exception as e:
        print(f"解析Excel文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def parse_route_string(route_str: str) -> List[tuple]:
    """解析航线字符串，保持多段航线的完整性"""
    routes = []
    
    # 清理字符串
    route_str = route_str.strip()
    
    # 常见的分隔符
    separators = ['—', '-', '→', '->', '至', '到']
    
    # 尝试用不同分隔符分割
    for sep in separators:
        if sep in route_str:
            parts = route_str.split(sep)
            if len(parts) >= 2:
                # 不管是两段还是多段，都保持完整的航线
                origin = clean_city_name(parts[0].strip())
                destination = clean_city_name(parts[-1].strip())  # 取最后一个作为终点
                
                # 如果是多段航线，保留完整的航线描述
                if len(parts) > 2:
                    # 构建完整的多段航线描述
                    cleaned_parts = [clean_city_name(part.strip()) for part in parts if clean_city_name(part.strip())]
                    if len(cleaned_parts) >= 2:
                        full_route = sep.join(cleaned_parts)
                        routes.append((origin, destination, full_route))  # 添加完整航线信息
                else:
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

def is_domestic_city(city_name: str) -> bool:
    """判断是否为国内城市"""
    domestic_cities = {
        '北京', '上海', '广州', '深圳', '成都', '重庆', '杭州', '南京', '武汉', '西安',
        '天津', '青岛', '大连', '厦门', '宁波', '郑州', '长沙', '哈尔滨', '沈阳', '济南',
        '福州', '石家庄', '太原', '合肥', '南昌', '昆明', '贵阳', '兰州', '银川', '西宁',
        '乌鲁木齐', '拉萨', '海口', '三亚', '呼和浩特', '长春', '大庆', '包头', '鄂州',
        '浦东', '首都', '双流', '桃仙', '白云', '宝安', '萧山', '禄口', '天河', '咸阳',
        '滨海', '流亭', '周水子', '高崎', '栎社', '新郑', '黄花', '太平', '桃仙', '遥墙',
        '长乐', '正定', '武宿', '骆岗', '昌北', '长水', '龙洞堡', '中川', '河东', '曹家堡',
        '地窝堡', '贡嘎', '美兰', '凤凰', '白塔', '二连浩特', '芜湖'
    }
    
    # 检查城市名称是否包含国内城市关键词
    for domestic_city in domestic_cities:
        if domestic_city in city_name:
            return True
    
    return False

if __name__ == "__main__":
    # 测试解析函数
    file_path = "D:\\flight_tool\\data\\大陆航司全货机航线.xlsx"
    result = parse_excel_route_data(file_path)
    
    if not result.empty:
        print(f"\n=== 前10条航线记录 ===")
        print(result.head(10))
        
        # 保存结果
        result.to_csv("parsed_routes.csv", index=False, encoding='utf-8-sig')
        print(f"\n解析结果已保存到 parsed_routes.csv")
    else:
        print("没有解析到任何航线数据")