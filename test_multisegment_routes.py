#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多段航线处理逻辑
验证修改后的解析器是否正确保持多段航线的完整性
"""

import pandas as pd
from fix_parser import parse_excel_route_data, parse_route_string
from data_cleaner import clean_route_data

def test_parse_route_string():
    """测试航线字符串解析函数"""
    print("=== 测试航线字符串解析 ===")
    
    test_cases = [
        "上海—北京",  # 单段航线
        "上海—安克雷奇—纽约",  # 多段航线
        "鄂州-安克雷奇-纽约-哈利法克斯",  # 多段航线
        "成都-乌鲁木齐-阿拉木图-布达佩斯",  # 多段航线
        "浦东→列日→马德里巴拉哈斯",  # 多段航线（不同分隔符）
    ]
    
    for route_str in test_cases:
        print(f"\n原始航线: {route_str}")
        routes = parse_route_string(route_str)
        for i, route_info in enumerate(routes):
            if len(route_info) == 3:
                origin, destination, full_route = route_info
                print(f"  解析结果 {i+1}: 起点={origin}, 终点={destination}, 完整航线={full_route}")
            else:
                origin, destination = route_info
                print(f"  解析结果 {i+1}: 起点={origin}, 终点={destination}")

def test_excel_parsing():
    """测试Excel数据解析"""
    print("\n=== 测试Excel数据解析 ===")
    
    try:
        # 解析原始数据
        raw_df = parse_excel_route_data('data/货运航空公司航线统计表.xlsx')
        print(f"解析后原始记录数: {len(raw_df)}")
        
        if not raw_df.empty:
            # 检查是否包含full_route列
            if 'full_route' in raw_df.columns:
                print("\n✅ 成功添加完整航线信息列")
                
                # 显示一些多段航线的例子
                print("\n=== 多段航线示例 ===")
                multi_segment = raw_df[raw_df['full_route'].str.contains('—.*—|—.*-|-.*—', na=False)]
                if not multi_segment.empty:
                    print(f"多段航线数量: {len(multi_segment)}")
                    for idx, row in multi_segment.head(10).iterrows():
                        print(f"  {row['airline']}: {row['full_route']} (起点: {row['origin']}, 终点: {row['destination']})")
                else:
                    print("未找到多段航线")
                
                # 显示一些单段航线的例子
                print("\n=== 单段航线示例 ===")
                single_segment = raw_df[~raw_df['full_route'].str.contains('—.*—|—.*-|-.*—', na=False)]
                if not single_segment.empty:
                    print(f"单段航线数量: {len(single_segment)}")
                    for idx, row in single_segment.head(5).iterrows():
                        print(f"  {row['airline']}: {row['full_route']} (起点: {row['origin']}, 终点: {row['destination']})")
            else:
                print("❌ 未找到完整航线信息列")
                print(f"可用列: {list(raw_df.columns)}")
        
        # 测试数据清理
        print("\n=== 测试数据清理 ===")
        cleaned_df = clean_route_data(raw_df, enable_deduplication=False)
        print(f"清理后记录数: {len(cleaned_df)}")
        
        if 'full_route' in cleaned_df.columns:
            print("✅ 数据清理后保留了完整航线信息")
        else:
            print("❌ 数据清理后丢失了完整航线信息")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🛫 多段航线处理逻辑测试")
    print("=" * 50)
    
    # 测试航线字符串解析
    test_parse_route_string()
    
    # 测试Excel数据解析
    test_excel_parsing()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()