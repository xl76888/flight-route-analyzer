#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复3D地图数据处理问题
"""

import pandas as pd
from airport_coords import get_airport_info
from fix_parser import parse_excel_route_data

def safe_get_airport_info(airport_code):
    """安全获取机场信息，确保返回正确格式"""
    try:
        result = get_airport_info(airport_code)
        if result and isinstance(result, dict) and 'coords' in result:
            coords = result['coords']
            if isinstance(coords, list) and len(coords) == 2:
                return result
        return None
    except Exception as e:
        print(f"获取机场信息时出错 {airport_code}: {e}")
        return None

def test_3d_data_processing():
    """测试3D地图数据处理"""
    print("🔍 测试3D地图数据处理...")
    
    try:
        # 加载数据
        data_file = "data/大陆航司全货机航线.xlsx"
        routes_df = parse_excel_route_data(data_file)
        print(f"✅ 成功加载数据，共 {len(routes_df)} 条记录")
        
        # 测试前10条记录
        route_data_3d = []
        valid_count = 0
        invalid_count = 0
        
        for i, (_, route) in enumerate(routes_df.head(20).iterrows()):
            origin_code = route.get('origin', '')
            destination_code = route.get('destination', '')
            
            print(f"\n第{i+1}条: {origin_code} -> {destination_code}")
            
            start_info = safe_get_airport_info(origin_code)
            end_info = safe_get_airport_info(destination_code)
            
            if start_info and end_info:
                try:
                    route_data = {
                        'id': f"route_{valid_count}",
                        'start_airport': origin_code,
                        'end_airport': destination_code,
                        'start_airport_name': start_info['name'],
                        'end_airport_name': end_info['name'],
                        'start_lat': float(start_info['coords'][0]),
                        'start_lng': float(start_info['coords'][1]),
                        'end_lat': float(end_info['coords'][0]),
                        'end_lng': float(end_info['coords'][1]),
                        'airline': str(route.get('airline', '')),
                        'aircraft_type': str(route.get('aircraft', '')),
                        'direction': str(route.get('direction', '出口'))
                    }
                    route_data_3d.append(route_data)
                    valid_count += 1
                    print(f"  ✅ 成功处理: {start_info['name']} -> {end_info['name']}")
                    
                except Exception as e:
                    print(f"  ❌ 处理错误: {e}")
                    invalid_count += 1
            else:
                print(f"  ❌ 机场信息缺失: start_info={start_info}, end_info={end_info}")
                invalid_count += 1
        
        print(f"\n📊 处理结果:")
        print(f"  有效航线: {valid_count} 条")
        print(f"  无效航线: {invalid_count} 条")
        print(f"  成功率: {valid_count/(valid_count+invalid_count)*100:.1f}%")
        
        if route_data_3d:
            print(f"\n✅ 3D地图数据准备完成，共 {len(route_data_3d)} 条航线")
            # 显示第一条数据作为示例
            print(f"\n示例数据:")
            first_route = route_data_3d[0]
            for key, value in first_route.items():
                print(f"  {key}: {value}")
        else:
            print(f"\n❌ 没有有效的3D地图数据")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_3d_data_processing()
    print("\n🎯 测试完成！")