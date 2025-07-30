#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Web应用数据处理流程
"""

from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data
from airport_coords import get_airport_coords
import pandas as pd
import os

def debug_web_data_processing():
    """调试Web应用的完整数据处理流程"""
    print("🔍 调试Web应用数据处理流程")
    print("=" * 50)
    
    # 步骤1：模拟Web应用的数据加载
    print("\n📊 步骤1: 模拟Web应用数据加载")
    excel_file = 'data/大陆航司全货机航线.xlsx'
    
    # 使用专用解析函数处理Excel文件
    routes_df = parse_excel_route_data(excel_file)
    print(f"解析后记录数: {len(routes_df)}")
    
    # 步骤2：重命名列以匹配系统期望的格式（模拟web_app.py第427-430行）
    print("\n🔄 步骤2: 列重命名")
    routes_df = routes_df.rename(columns={
        'reg': 'registration',
        'aircraft': 'aircraft',
        'age': 'age',
        'remarks': 'special'
    })
    
    # 添加缺失的列（模拟web_app.py第432-440行）
    if 'flight_number' not in routes_df.columns:
        routes_df['flight_number'] = ''
    if 'frequency' not in routes_df.columns:
        routes_df['frequency'] = '正常运营'
    if 'flight_time' not in routes_df.columns:
        routes_df['flight_time'] = ''
    if 'flight_distance' not in routes_df.columns:
        routes_df['flight_distance'] = ''
    
    print(f"列处理后记录数: {len(routes_df)}")
    
    # 步骤3：数据清理（模拟web_app.py第442行）
    print("\n🧹 步骤3: 数据清理")
    enable_deduplication = False  # 默认值
    routes_df = clean_route_data(routes_df, enable_deduplication=enable_deduplication)
    print(f"清理后记录数: {len(routes_df)}")
    print(f"清理后航司数: {len(routes_df['airline'].unique())}")
    
    # 步骤4：补充飞行距离和时间数据（模拟web_app.py第451-485行）
    print("\n📏 步骤4: 补充飞行距离和时间数据")
    
    # 统计有多少记录有坐标
    valid_coords_count = 0
    missing_origin_coords = []
    missing_dest_coords = []
    
    for idx, row in routes_df.iterrows():
        # 获取起点和终点坐标
        origin_coords = get_airport_coords(row['origin'])
        dest_coords = get_airport_coords(row['destination'])
        
        # 只有当两个坐标都存在时才计算距离
        if origin_coords and dest_coords:
            valid_coords_count += 1
        else:
            # 记录缺失坐标的城市
            if not origin_coords:
                missing_origin_coords.append(row['origin'])
            if not dest_coords:
                missing_dest_coords.append(row['destination'])
    
    print(f"有效坐标的记录数: {valid_coords_count}")
    print(f"缺失起点坐标的记录数: {len(missing_origin_coords)}")
    print(f"缺失终点坐标的记录数: {len(missing_dest_coords)}")
    
    if missing_origin_coords:
        unique_missing_origins = list(set(missing_origin_coords))
        print(f"缺失起点坐标的城市: {unique_missing_origins[:10]}...")  # 只显示前10个
    
    if missing_dest_coords:
        unique_missing_dests = list(set(missing_dest_coords))
        print(f"缺失终点坐标的城市: {unique_missing_dests[:10]}...")  # 只显示前10个
    
    # 步骤5：检查是否有记录在坐标处理过程中被过滤
    print("\n🔍 步骤5: 检查坐标过滤影响")
    
    # 模拟可能的过滤逻辑
    # 检查是否有记录因为缺失坐标而被隐式过滤
    records_with_both_coords = 0
    for idx, row in routes_df.iterrows():
        origin_coords = get_airport_coords(row['origin'])
        dest_coords = get_airport_coords(row['destination'])
        if origin_coords and dest_coords:
            records_with_both_coords += 1
    
    print(f"有完整坐标的记录数: {records_with_both_coords}")
    print(f"缺失坐标的记录数: {len(routes_df) - records_with_both_coords}")
    
    # 步骤6：检查Web应用可能的额外过滤
    print("\n🌐 步骤6: 检查可能的额外过滤")
    
    # 检查是否有空值或异常数据
    empty_airline = routes_df[routes_df['airline'].isna() | (routes_df['airline'] == '')]
    empty_origin = routes_df[routes_df['origin'].isna() | (routes_df['origin'] == '')]
    empty_destination = routes_df[routes_df['destination'].isna() | (routes_df['destination'] == '')]
    
    print(f"空航司记录数: {len(empty_airline)}")
    print(f"空起点记录数: {len(empty_origin)}")
    print(f"空终点记录数: {len(empty_destination)}")
    
    # 步骤7：最终统计
    print("\n📊 步骤7: 最终统计")
    print(f"最终记录数: {len(routes_df)}")
    print(f"最终航司数: {len(routes_df['airline'].unique())}")
    print(f"预期Web显示: {len(routes_df)} 条记录")
    print(f"实际Web显示: 611 条记录")
    print(f"差异: {len(routes_df) - 611} 条记录")
    
    if len(routes_df) != 611:
        print("\n❌ 发现数据差异！可能原因:")
        print("1. Web应用中有额外的过滤逻辑")
        print("2. 数据加载过程中的异步处理问题")
        print("3. 缓存或状态管理问题")
        print("4. 前端显示逻辑的过滤")
    
    # 保存调试数据
    routes_df.to_csv('data/debug_web_data.csv', index=False, encoding='utf-8-sig')
    print(f"\n💾 调试数据已保存到: data/debug_web_data.csv")
    
    return routes_df

if __name__ == "__main__":
    result = debug_web_data_processing()