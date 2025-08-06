#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试机场信息获取函数
"""

import pandas as pd
from airport_coords import get_airport_info

def test_airport_info():
    """测试机场信息获取函数"""
    print("🔍 测试机场信息获取函数...")
    
    # 测试一些常见的机场代码
    test_codes = ['深圳', 'SZX', '北京', 'PEK', '科伦坡', '昆明', '烟台', '大阪']
    
    for code in test_codes:
        print(f"\n测试: {code}")
        try:
            result = get_airport_info(code)
            print(f"  结果类型: {type(result)}")
            print(f"  结果内容: {result}")
            
            if result:
                print(f"  坐标类型: {type(result.get('coords', 'N/A'))}")
                print(f"  坐标内容: {result.get('coords', 'N/A')}")
                
                # 测试坐标访问
                coords = result.get('coords')
                if coords:
                    print(f"  纬度: {coords[0]}")
                    print(f"  经度: {coords[1]}")
            else:
                print("  ❌ 未找到机场信息")
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            print(f"  错误类型: {type(e)}")

def test_with_real_data():
    """使用真实数据测试"""
    print("\n🔍 使用真实数据测试...")
    
    # 尝试加载数据文件
    try:
        data_file = "data/大陆航司全货机航线.xlsx"
        df = pd.read_excel(data_file)
        print(f"✅ 成功加载数据文件，共 {len(df)} 行")
        
        # 获取前10行的起点和终点
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            origin = row.get('origin', '')
            destination = row.get('destination', '')
            
            print(f"\n第{i+1}行: {origin} -> {destination}")
            
            # 测试起点
            try:
                start_info = get_airport_info(origin)
                print(f"  起点信息: {start_info}")
            except Exception as e:
                print(f"  起点错误: {e}")
            
            # 测试终点
            try:
                end_info = get_airport_info(destination)
                print(f"  终点信息: {end_info}")
            except Exception as e:
                print(f"  终点错误: {e}")
                
    except Exception as e:
        print(f"❌ 无法加载数据文件: {e}")

if __name__ == "__main__":
    test_airport_info()
    test_with_real_data()
    print("\n🎯 调试完成！")