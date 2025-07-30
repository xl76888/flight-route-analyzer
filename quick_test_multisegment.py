#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试多段航线解析功能
"""

from fix_parser import parse_route_string

def test_multisegment_parsing():
    """测试多段航线解析"""
    print("🛫 多段航线解析测试")
    print("=" * 40)
    
    test_cases = [
        "上海—北京",  # 单段
        "上海—安克雷奇—纽约",  # 三段
        "鄂州-安克雷奇-纽约-哈利法克斯",  # 四段
        "成都-乌鲁木齐-阿拉木图-布达佩斯",  # 四段
        "浦东→列日→马德里巴拉哈斯",  # 三段，不同分隔符
        "深圳-杭州-洛杉矶",  # 三段
    ]
    
    for route_str in test_cases:
        print(f"\n📍 原始航线: {route_str}")
        routes = parse_route_string(route_str)
        
        if not routes:
            print("  ❌ 解析失败")
            continue
            
        for i, route_info in enumerate(routes):
            if len(route_info) == 3:
                origin, destination, full_route = route_info
                print(f"  ✅ 多段航线: 起点={origin}, 终点={destination}")
                print(f"     完整航线: {full_route}")
            elif len(route_info) == 2:
                origin, destination = route_info
                print(f"  ✅ 单段航线: {origin} → {destination}")
            else:
                print(f"  ❓ 未知格式: {route_info}")

if __name__ == "__main__":
    test_multisegment_parsing()
    print("\n✨ 测试完成")