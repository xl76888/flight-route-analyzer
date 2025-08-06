#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门解析中国十六家货航国际航线.xlsx文件的解析器
"""

import pandas as pd
import re
import os
from typing import List, Dict, Any

def parse_sixteen_airlines_excel(file_path: str) -> pd.DataFrame:
    """
    专门解析中国十六家货航国际航线.xlsx文件
    该文件格式特点：
    - 每行包含一个航班的完整信息
    - 有出口航线和进口航线两个方向的数据
    - 包含详细的飞行时长、速度、距离等信息
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        print(f"原始数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        
        all_routes = []
        
        # 遍历每一行数据
        for idx, row in df.iterrows():
            airline = row.get('航司', '')
            reg_no = row.get('注册号', '')
            aircraft = row.get('机型', '')
            age = row.get('机龄', '')
            
            # 跳过空行或无效数据
            if pd.isna(airline) or str(airline).strip() == '':
                continue
                
            airline = str(airline).strip()
            reg_no = str(reg_no).strip() if pd.notna(reg_no) else ''
            aircraft = str(aircraft).strip() if pd.notna(aircraft) else ''
            age = str(age).strip() if pd.notna(age) else ''
            
            # 处理出口航线
            export_city_route = row.get('出口航线（城市—城市）', '')
            export_airport_route = row.get('出口航线（机场—机场）', '')
            export_iata_route = row.get('出口航线（机场—机场）.1', '')
            export_flight_time = row.get('飞行时长', '')
            export_speed = row.get('速度（单位：公里/小时）', '')
            export_distance = row.get('飞行距离（单位：公里）', '')
            export_frequency = row.get('每周班次', '')
            
            if pd.notna(export_city_route) and str(export_city_route).strip():
                origin, destination = parse_city_route(str(export_city_route))
                if origin and destination:
                    all_routes.append({
                        'airline': airline,
                        'reg': reg_no,
                        'aircraft': aircraft,
                        'age': age,
                        'origin': origin,
                        'destination': destination,
                        'direction': '出口',
                        'city_route': str(export_city_route).strip(),
                        'airport_route': str(export_airport_route).strip() if pd.notna(export_airport_route) else '',
                        'iata_route': str(export_iata_route).strip() if pd.notna(export_iata_route) else '',
                        'flight_time': str(export_flight_time).strip() if pd.notna(export_flight_time) else '',
                        'speed': export_speed if pd.notna(export_speed) else '',
                        'distance': export_distance if pd.notna(export_distance) else '',
                        'weekly_frequency': export_frequency if pd.notna(export_frequency) else '',
                        'remarks': ''
                    })
            
            # 处理进口航线
            import_city_route = row.get('进口航线（城市—城市）', '')
            import_airport_route = row.get('进口航线（机场—机场）', '')
            import_iata_route = row.get('进口航线（机场—机场）.1', '')
            import_flight_time = row.get('飞行时长.1', '')
            import_speed = row.get('速度（单位：公里/小时）.1', '')
            import_distance = row.get('飞行距离（单位：公里）.1', '')
            import_frequency = row.get('每周班次.1', '')
            
            if pd.notna(import_city_route) and str(import_city_route).strip():
                origin, destination = parse_city_route(str(import_city_route))
                if origin and destination:
                    all_routes.append({
                        'airline': airline,
                        'reg': reg_no,
                        'aircraft': aircraft,
                        'age': age,
                        'origin': origin,
                        'destination': destination,
                        'direction': '进口',
                        'city_route': str(import_city_route).strip(),
                        'airport_route': str(import_airport_route).strip() if pd.notna(import_airport_route) else '',
                        'iata_route': str(import_iata_route).strip() if pd.notna(import_iata_route) else '',
                        'flight_time': str(import_flight_time).strip() if pd.notna(import_flight_time) else '',
                        'speed': import_speed if pd.notna(import_speed) else '',
                        'distance': import_distance if pd.notna(import_distance) else '',
                        'weekly_frequency': import_frequency if pd.notna(import_frequency) else '',
                        'remarks': ''
                    })
        
        result_df = pd.DataFrame(all_routes)
        
        print(f"\n=== 中国十六家货航数据解析报告 ===")
        print(f"原始记录数: {len(df)}")
        print(f"解析出的航线总数: {len(result_df)}")
        
        if not result_df.empty:
            print(f"\n=== 航司统计 ===")
            airline_counts = result_df['airline'].value_counts()
            for airline, count in airline_counts.items():
                print(f"  {airline}: {count} 条航线")
            
            print(f"\n=== 方向统计 ===")
            direction_counts = result_df['direction'].value_counts()
            for direction, count in direction_counts.items():
                print(f"  {direction}: {count} 条航线")
            
            # 统计城市
            origins = result_df['origin'].unique()
            destinations = result_df['destination'].unique()
            all_cities = set(origins) | set(destinations)
            
            print(f"\n=== 城市统计 ===")
            print(f"涉及城市总数: {len(all_cities)}")
            print(f"起点城市: {', '.join(sorted(origins))}")
            print(f"终点城市: {', '.join(sorted(destinations))}")
        
        return result_df
        
    except Exception as e:
        print(f"解析Excel文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def parse_city_route(route_str: str) -> tuple:
    """
    解析城市航线字符串
    例如: "重庆-德国法兰克福" -> ("重庆", "德国法兰克福")
    """
    if not route_str or pd.isna(route_str):
        return '', ''
    
    route_str = str(route_str).strip()
    
    # 常见分隔符
    separators = ['-', '—', '→', '->', '至', '到']
    
    for sep in separators:
        if sep in route_str:
            parts = route_str.split(sep, 1)  # 只分割一次
            if len(parts) == 2:
                origin = clean_city_name(parts[0].strip())
                destination = clean_city_name(parts[1].strip())
                return origin, destination
    
    return '', ''

def clean_city_name(city_name: str) -> str:
    """
    清理城市名称
    """
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

def convert_to_standard_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    将解析结果转换为标准格式，与其他解析器保持一致
    """
    if df.empty:
        return df
    
    # 创建标准格式的DataFrame
    standard_df = pd.DataFrame({
        'airline': df['airline'],
        'reg': df['reg'],
        'aircraft': df['aircraft'],
        'age': df['age'],
        'origin': df['origin'],
        'destination': df['destination'],
        'direction': df['direction'],
        'remarks': df['remarks']
    })
    
    return standard_df

if __name__ == "__main__":
    # 测试解析函数
    file_path = "data/中国十六家货航国际航线.xlsx"
    
    if os.path.exists(file_path):
        print("开始解析中国十六家货航国际航线.xlsx...")
        result = parse_sixteen_airlines_excel(file_path)
        
        if not result.empty:
            print(f"\n=== 前10条航线记录 ===")
            print(result.head(10))
            
            # 转换为标准格式
            standard_result = convert_to_standard_format(result)
            
            # 保存结果
            output_file = "data/中国十六家货航国际航线_解析结果.csv"
            standard_result.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n解析结果已保存到 {output_file}")
            
            # 也保存详细版本
            detailed_output_file = "data/中国十六家货航国际航线_详细解析结果.csv"
            result.to_csv(detailed_output_file, index=False, encoding='utf-8-sig')
            print(f"详细解析结果已保存到 {detailed_output_file}")
        else:
            print("没有解析到任何航线数据")
    else:
        print(f"文件不存在: {file_path}")