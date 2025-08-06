#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试3D地图显示问题
"""

import streamlit as st
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.google_maps_config import is_maps_configured, get_api_key, get_map_id
from optimized_map3d_integration import render_optimized_3d_map

def main():
    st.title("🔍 3D地图问题诊断")
    
    # 检查配置
    st.subheader("1. 配置检查")
    if is_maps_configured():
        st.success("✅ Google Maps API已配置")
        st.info(f"API Key: {get_api_key()[:10]}...")
        st.info(f"Map ID: {get_map_id()}")
    else:
        st.error("❌ Google Maps API未配置")
        return
    
    # 检查组件文件
    st.subheader("2. 组件文件检查")
    component_path = "components/map3d/optimized_map3d_component.html"
    if os.path.exists(component_path):
        st.success(f"✅ 3D地图组件文件存在: {component_path}")
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
        st.info(f"文件大小: {len(content)} 字符")
    else:
        st.error(f"❌ 3D地图组件文件不存在: {component_path}")
        return
    
    # 测试数据
    st.subheader("3. 测试3D地图渲染")
    test_data = [
        {
            'id': 'test_route_1',
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
    
    # 尝试渲染3D地图
    try:
        st.write("正在尝试渲染3D地图...")
        result = render_optimized_3d_map(
            test_data,
            height=600,
            key="test_3d_map",
            force_reload=True
        )
        
        if result:
            st.success("✅ 3D地图渲染成功！")
            st.json(result)
        else:
            st.warning("⚠️ 3D地图渲染返回None")
            
    except Exception as e:
        st.error(f"❌ 3D地图渲染失败: {str(e)}")
        st.exception(e)
    
    # 显示调试信息
    st.subheader("4. 调试信息")
    st.write("如果3D地图仍然显示为2D，可能的原因：")
    st.write("• 浏览器不支持WebGL")
    st.write("• Google Maps API密钥权限不足")
    st.write("• 网络连接问题")
    st.write("• 地图ID配置错误")
    st.write("• Streamlit组件渲染问题")

if __name__ == "__main__":
    main()