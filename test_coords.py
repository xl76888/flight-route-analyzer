#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from airport_coords import get_airport_coords

# 测试坐标获取
test_cities = ['鄂州', '金奈', '拉合尔', '深圳', '上海']

print("测试城市坐标获取：")
for city in test_cities:
    coords = get_airport_coords(city)
    print(f"{city}: {coords}")

# 测试航线坐标
print("\n测试航线坐标：")
routes = [
    ('上海', '鄂州'),
    ('深圳', '金奈'),
    ('北京', '拉合尔')
]

for origin, dest in routes:
    origin_coords = get_airport_coords(origin)
    dest_coords = get_airport_coords(dest)
    print(f"航线: {origin} -> {dest}")
    print(f"起点坐标: {origin_coords}, 终点坐标: {dest_coords}")
    if origin_coords != dest_coords:
        print("✓ 坐标不同，航线有效")
    else:
        print("✗ 坐标相同，可能使用了默认坐标")
    print()