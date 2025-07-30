#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查缺失的城市
"""

from fix_parser import parse_excel_route_data
from data_cleaner import DOMESTIC_CITIES, INTERNATIONAL_CITIES, normalize_city_name, is_valid_city

def check_missing_cities():
    """检查哪些城市缺失"""
    print("🔍 检查缺失的城市")
    print("=" * 40)
    
    # 解析数据
    df = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    
    # 获取所有城市
    all_origins = df['origin'].dropna().unique()
    all_destinations = df['destination'].dropna().unique()
    all_cities = set(list(all_origins) + list(all_destinations))
    
    print(f"总共发现 {len(all_cities)} 个不同的城市")
    
    # 检查缺失的城市
    missing_cities = []
    valid_cities = []
    
    for city in all_cities:
        normalized = normalize_city_name(city)
        if not is_valid_city(city):
            missing_cities.append((city, normalized))
        else:
            valid_cities.append((city, normalized))
    
    print(f"\n✅ 有效城市数量: {len(valid_cities)}")
    print(f"❌ 缺失城市数量: {len(missing_cities)}")
    
    if missing_cities:
        print("\n❌ 缺失的城市列表:")
        for original, normalized in missing_cities:
            print(f"  原始: '{original}' -> 标准化: '{normalized}'")
            
            # 检查是否在国内或国际城市列表中
            in_domestic = normalized in DOMESTIC_CITIES
            in_international = normalized in INTERNATIONAL_CITIES
            print(f"    国内城市列表: {in_domestic}, 国际城市列表: {in_international}")
    
    # 特别检查中货航的城市
    print("\n🔍 中货航城市检查:")
    zhonghuohang = df[df['airline'] == '中货航']
    zhh_cities = set(list(zhonghuohang['origin'].dropna()) + list(zhonghuohang['destination'].dropna()))
    
    print(f"中货航涉及城市: {sorted(zhh_cities)}")
    
    zhh_missing = []
    for city in zhh_cities:
        if not is_valid_city(city):
            zhh_missing.append(city)
    
    if zhh_missing:
        print(f"❌ 中货航缺失的城市: {zhh_missing}")
    else:
        print("✅ 中货航所有城市都有效")
    
    # 生成需要添加的城市代码
    if missing_cities:
        print("\n📝 需要添加到INTERNATIONAL_CITIES的城市:")
        international_to_add = []
        for original, normalized in missing_cities:
            # 判断是否为国际城市（简单判断：非中文字符较多的可能是国际城市）
            if any(ord(char) > 127 for char in normalized) or len(normalized) > 6:
                continue  # 跳过包含特殊字符的
            international_to_add.append(f"    '{normalized}',  # {original}")
        
        if international_to_add:
            print("\n可以添加的城市:")
            for line in international_to_add[:20]:  # 只显示前20个
                print(line)

if __name__ == "__main__":
    check_missing_cities()