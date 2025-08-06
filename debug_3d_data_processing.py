#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试3D地图数据处理过程
"""

import streamlit as st
import pandas as pd
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_3d_data_processing():
    st.title("🔍 3D地图数据处理调试")
    
    # 检查配置
    st.subheader("1. 配置检查")
    from config.google_maps_config import is_maps_configured
    if is_maps_configured():
        st.success("✅ Google Maps API已配置")
    else:
        st.error("❌ Google Maps API未配置")
        return
    
    # 模拟数据加载
    st.subheader("2. 模拟数据处理")
    
    # 创建测试数据
    test_data = pd.DataFrame([
        {'origin': 'PEK', 'destination': 'LAX', 'airline': '中国国际航空', 'aircraft': 'Boeing 777', 'direction': '出口'},
        {'origin': 'PVG', 'destination': 'JFK', 'airline': '中国东方航空', 'aircraft': 'Airbus A350', 'direction': '出口'},
        {'origin': 'CAN', 'destination': 'LHR', 'airline': '中国南方航空', 'aircraft': 'Boeing 787', 'direction': '出口'},
        {'origin': 'CTU', 'destination': 'SFO', 'airline': '四川航空', 'aircraft': 'Airbus A330', 'direction': '出口'},
        {'origin': 'XIY', 'destination': 'CDG', 'airline': '海南航空', 'aircraft': 'Boeing 787', 'direction': '出口'}
    ])
    
    st.info(f"测试数据: {len(test_data)} 条航线")
    st.dataframe(test_data)
    
    # 测试机场坐标获取
    st.subheader("3. 机场坐标获取测试")
    
    try:
        from airport_coords import get_airport_info
        
        route_data_3d = []
        valid_routes_count = 0
        invalid_routes_count = 0
        
        for _, route in test_data.iterrows():
            st.write(f"\n处理航线: {route['origin']} -> {route['destination']}")
            
            start_info = get_airport_info(route['origin'])
            end_info = get_airport_info(route['destination'])
            
            if start_info:
                st.success(f"✅ 起始机场 {route['origin']}: {start_info['name']} ({start_info['coords']})")
            else:
                st.error(f"❌ 起始机场 {route['origin']}: 坐标获取失败")
            
            if end_info:
                st.success(f"✅ 目标机场 {route['destination']}: {end_info['name']} ({end_info['coords']})")
            else:
                st.error(f"❌ 目标机场 {route['destination']}: 坐标获取失败")
            
            if start_info and end_info:
                try:
                    route_data_3d.append({
                        'id': f"route_{valid_routes_count}",
                        'start_airport': str(route['origin']),
                        'end_airport': str(route['destination']),
                        'start_airport_name': start_info['name'],
                        'end_airport_name': end_info['name'],
                        'origin': str(route['origin']),
                        'destination': str(route['destination']),
                        'start_lat': float(start_info['coords'][0]),
                        'start_lng': float(start_info['coords'][1]),
                        'end_lat': float(end_info['coords'][0]),
                        'end_lng': float(end_info['coords'][1]),
                        'frequency': 1,
                        'airline': str(route['airline']),
                        'aircraft_type': str(route['aircraft']),
                        'route_type': 'international',
                        'direction': str(route['direction']),
                        'is_bidirectional': False,
                        'bidirectional': False
                    })
                    valid_routes_count += 1
                    st.success(f"✅ 航线数据构建成功")
                except Exception as e:
                    st.error(f"❌ 航线数据构建失败: {str(e)}")
                    invalid_routes_count += 1
            else:
                invalid_routes_count += 1
        
        # 显示处理结果
        st.subheader("4. 数据处理结果")
        st.info(f"有效航线: {valid_routes_count} 条")
        st.info(f"无效航线: {invalid_routes_count} 条")
        st.info(f"3D地图数据总数: {len(route_data_3d)} 条")
        
        if len(route_data_3d) > 0:
            st.success("✅ 3D地图数据准备成功！")
            st.json(route_data_3d[0])  # 显示第一条数据作为示例
            
            # 尝试渲染3D地图
            st.subheader("5. 3D地图渲染测试")
            try:
                from optimized_map3d_integration import render_optimized_3d_map
                
                with st.spinner("正在渲染3D地图..."):
                    result = render_optimized_3d_map(
                        route_data_3d,
                        height=600,
                        key="debug_3d_map",
                        force_reload=True
                    )
                
                if result:
                    st.success("✅ 3D地图渲染成功！")
                else:
                    st.warning("⚠️ 3D地图渲染返回None")
                    
            except Exception as e:
                st.error(f"❌ 3D地图渲染失败: {str(e)}")
                st.exception(e)
        else:
            st.error("❌ 没有有效的3D地图数据，这就是为什么显示2D地图的原因！")
            
    except Exception as e:
        st.error(f"❌ 数据处理过程出错: {str(e)}")
        st.exception(e)
    
    # 显示解决方案
    st.subheader("6. 问题解决方案")
    st.write("如果3D地图数据为空，可能的原因和解决方案：")
    st.write("• **机场坐标缺失**: 检查airport_coords.py中的机场数据库")
    st.write("• **数据格式错误**: 确保CSV文件包含正确的origin和destination列")
    st.write("• **导入错误**: 检查airport_coords模块是否正确导入")
    st.write("• **异常处理**: 查看控制台是否有错误信息")

if __name__ == "__main__":
    debug_3d_data_processing()