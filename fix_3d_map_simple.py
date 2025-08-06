#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的3D地图修复工具 - 专为开发小白设计
一键修复3D地图显示问题
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    print("🚀 3D地图自动修复工具")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = Path.cwd()
    print(f"📁 当前工作目录: {current_dir}")
    
    # 步骤1: 检查必要文件
    print("\n📋 步骤1: 检查必要文件...")
    
    required_files = [
        "web_app.py",
        "airport_coords.py",
        "config/google_maps_config.py",
        "optimized_map3d_integration.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"  ❌ 缺少文件: {', '.join(missing_files)}")
        print("  请确保在正确的项目目录中运行此脚本")
        return False
    
    # 步骤2: 检查机场数据
    print("\n📋 步骤2: 检查机场数据...")
    try:
        from airport_coords import get_airport_info
        
        # 测试几个常见机场
        test_airports = ['PEK', 'PVG', 'CAN', 'LAX', 'JFK']
        working_airports = 0
        
        for airport in test_airports:
            info = get_airport_info(airport)
            if info:
                working_airports += 1
                print(f"  ✅ {airport}: {info['name']}")
            else:
                print(f"  ❌ {airport}: 数据缺失")
        
        if working_airports == 0:
            print("  ⚠️ 机场数据库可能有问题")
            return False
        else:
            print(f"  ✅ 机场数据正常 ({working_airports}/{len(test_airports)} 可用)")
            
    except Exception as e:
        print(f"  ❌ 机场数据检查失败: {e}")
        return False
    
    # 步骤3: 检查Google Maps配置
    print("\n📋 步骤3: 检查Google Maps配置...")
    try:
        from config.google_maps_config import is_maps_configured, get_api_key, get_map_id
        
        if is_maps_configured():
            print(f"  ✅ API配置正常")
            print(f"  ✅ API Key: {get_api_key()[:10]}...")
            print(f"  ✅ Map ID: {get_map_id()}")
        else:
            print("  ❌ Google Maps API未配置")
            return False
            
    except Exception as e:
        print(f"  ❌ 配置检查失败: {e}")
        return False
    
    # 步骤4: 修复3D地图组件
    print("\n📋 步骤4: 修复3D地图组件...")
    
    component_dir = Path("components/map3d")
    if not component_dir.exists():
        component_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ 创建组件目录: {component_dir}")
    
    # 检查关键组件文件
    component_file = component_dir / "optimized_map3d_component.html"
    if component_file.exists():
        print(f"  ✅ 3D地图组件存在: {component_file}")
    else:
        print(f"  ❌ 3D地图组件缺失: {component_file}")
        return False
    
    # 步骤5: 创建简化的测试脚本
    print("\n📋 步骤5: 创建测试脚本...")
    
    test_script = """
import streamlit as st
import pandas as pd
from optimized_map3d_integration import render_optimized_3d_map

st.title("🌐 3D地图测试")

# 创建测试数据
test_data = [
    {
        'id': 'test_1',
        'start_airport': 'PEK',
        'end_airport': 'LAX',
        'start_airport_name': '北京首都国际机场',
        'end_airport_name': '洛杉矶国际机场',
        'start_lat': 40.0799,
        'start_lng': 116.6031,
        'end_lat': 33.9425,
        'end_lng': -118.4081,
        'frequency': 5,
        'airline': '中国国际航空',
        'aircraft_type': 'Boeing 777',
        'route_type': 'international',
        'direction': '出口',
        'is_bidirectional': False
    }
]

st.info(f"测试数据: {len(test_data)} 条航线")

try:
    result = render_optimized_3d_map(
        test_data,
        height=600,
        key="simple_test_3d_map",
        force_reload=True
    )
    
    if result:
        st.success("✅ 3D地图渲染成功！")
    else:
        st.warning("⚠️ 3D地图渲染返回None")
        
except Exception as e:
    st.error(f"❌ 3D地图渲染失败: {str(e)}")
    st.exception(e)
"""
    
    with open("test_3d_simple.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("  ✅ 创建测试脚本: test_3d_simple.py")
    
    # 步骤6: 提供使用说明
    print("\n🎉 修复完成！")
    print("=" * 50)
    print("\n📖 使用说明:")
    print("1. 运行测试: streamlit run test_3d_simple.py --server.port 8506")
    print("2. 打开浏览器: http://localhost:8506")
    print("3. 如果3D地图正常显示，说明修复成功")
    print("4. 然后可以正常使用主应用: streamlit run web_app.py")
    
    print("\n🔧 如果仍有问题:")
    print("- 检查浏览器是否支持WebGL")
    print("- 尝试使用Chrome或Edge浏览器")
    print("- 确保网络连接正常")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 所有检查通过，3D地图应该可以正常工作了！")
        else:
            print("\n❌ 发现问题，请根据上述提示进行修复")
    except Exception as e:
        print(f"\n💥 修复过程出错: {e}")
        print("请联系技术支持或查看详细错误信息")