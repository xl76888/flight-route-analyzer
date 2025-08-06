#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D地图CDN资源修复工具
解决CDN加载失败导致的3D地图显示问题
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import List, Dict, Any, Optional
import json
import os
from config.google_maps_config import get_api_key, get_map_id, is_maps_configured, show_maps_config_status

def create_fixed_3d_map_html(route_data: List[Dict], api_key: str, map_id: str, height: int = 700) -> str:
    """
    创建修复CDN问题的3D地图HTML
    
    Args:
        route_data: 航线数据
        api_key: Google Maps API密钥
        map_id: 地图ID
        height: 地图高度
    
    Returns:
        HTML字符串
    """
    
    # 准备数据
    data_json = json.dumps(route_data, ensure_ascii=False, indent=2)
    
    # CSS样式（独立字符串，避免f-string冲突）
    css_styles = """
        body {
            margin: 0;
            padding: 0;
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: #f5f5f5;
        }
        
        #map-container {
            width: 100%;
            height: HEIGHT_PLACEHOLDERpx;
            position: relative;
            background: #e8f4fd;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        #loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            color: white;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-text {
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 10px;
        }
        
        .loading-subtitle {
            font-size: 14px;
            opacity: 0.8;
            margin-bottom: 20px;
        }
        
        .progress-container {
            width: 300px;
            height: 20px;
            background: rgba(255,255,255,0.3);
            border-radius: 10px;
            overflow: visible;
            margin-bottom: 15px;
            position: relative;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #2196F3, #03A9F4, #00BCD4);
            border-radius: 10px;
            transition: width 0.5s ease;
            width: 0%;
            position: relative;
        }
        
        .progress-airplane {
            position: absolute;
            top: -5px;
            right: -15px;
            font-size: 20px;
            color: #FFF;
            text-shadow: 0 0 10px rgba(33, 150, 243, 0.8);
            transition: transform 0.5s ease;
            z-index: 10;
        }
        
        .progress-airplane.flying {
            animation: fly 0.5s ease-in-out;
        }
        
        @keyframes fly {
            0% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-3px) rotate(5deg); }
            100% { transform: translateY(0px) rotate(0deg); }
        }
        
        .progress-track {
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.5) 50%, transparent 100%);
            transform: translateY(-50%);
            opacity: 0.6;
        }
        
        .progress-text {
            font-size: 12px;
            opacity: 0.9;
            margin-top: 8px;
        }
        
        #map3d {
            width: 100%;
            height: 100%;
            display: none;
        }
        
        .error-message {
            background: #ff5252;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 20px;
            text-align: center;
        }
        
        .success-message {
            background: #4caf50;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 14px;
            animation: slideIn 0.5s ease;
        }
        
        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .stats-container {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255,255,255,0.9);
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            z-index: 100;
        }
        
        .stats-item {
            margin-bottom: 5px;
        }
    """.replace('HEIGHT_PLACEHOLDER', str(height))
    
    # JavaScript代码
    javascript_code = f"""
        // 配置数据
        const CONFIG = {{
            apiKey: '{api_key}',
            mapId: '{map_id}',
            center: {{ lat: 39.9042, lng: 116.4074 }},
            zoom: 5,
            tilt: 45,
            heading: 0
        }};
        
        // 航线数据
        const ROUTE_DATA = {data_json};
        
        // 全局变量
        let map3d = null;
        let isMapLoaded = false;
        let loadStartTime = Date.now();
        
        // 更新状态显示
        function updateStatus(message) {{
            const statusElement = document.querySelector('.loading-text');
            if (statusElement) {{
                statusElement.textContent = message;
            }}
            console.log('状态更新:', message);
        }}
        
        // 更新API状态
        function updateApiStatus(message) {{
            const subtitleElement = document.querySelector('.loading-subtitle');
            if (subtitleElement) {{
                subtitleElement.textContent = message;
            }}
        }}
        
        // 初始化3D地图
        async function initMap3D() {{
            try {{
                console.log('开始初始化3D地图...');
                updateStatus('正在初始化3D地图...');
                
                // 检查API密钥
                if (!CONFIG.apiKey || CONFIG.apiKey === 'your-api-key-here') {{
                    throw new Error('Google Maps API密钥未配置');
                }}
                
                updateApiStatus('API密钥验证通过');
                
                // 动态加载Google Maps API
                await loadGoogleMapsAPI();
                
                // 获取地图元素
                map3d = document.getElementById('map3d');
                if (!map3d) {{
                    throw new Error('找不到地图容器元素');
                }}
                
                // 设置事件监听器
                map3d.addEventListener('gmp-load', onMapLoaded);
                map3d.addEventListener('gmp-error', onMapError);
                
                // 显示地图元素
                map3d.style.display = 'block';
                updateStatus('等待地图加载...');
                
            }} catch (error) {{
                console.error('3D地图初始化失败:', error);
                showError('3D地图初始化失败: ' + error.message);
            }}
        }}
        
        // 动态加载Google Maps API
        function loadGoogleMapsAPI() {{
            return new Promise((resolve, reject) => {{
                updateStatus('正在加载Google Maps API...');
                
                // 检查是否已经加载
                if (window.google && window.google.maps) {{
                    resolve();
                    return;
                }}
                
                // 创建script标签
                const script = document.createElement('script');
                script.src = `https://maps.googleapis.com/maps/api/js?key=${{CONFIG.apiKey}}&libraries=maps3d&v=alpha`;
                script.async = true;
                script.defer = true;
                
                script.onload = () => {{
                    console.log('Google Maps API加载成功');
                    updateApiStatus('Google Maps API加载完成');
                    resolve();
                }};
                
                script.onerror = () => {{
                    reject(new Error('Google Maps API加载失败'));
                }};
                
                document.head.appendChild(script);
            }});
        }}
        
        // 地图加载完成
        function onMapLoaded() {{
            console.log('3D地图加载完成');
            isMapLoaded = true;
            
            // 隐藏加载遮罩
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {{
                overlay.style.display = 'none';
            }}
            
            updateStatus('3D地图加载成功！');
            
            // 向父窗口发送就绪事件
            if (window.parent) {{
                window.parent.postMessage({{
                    type: 'map3d-ready',
                    timestamp: Date.now()
                }}, '*');
            }}
            
            // 加载航线数据
            setTimeout(() => {{
                loadRoutes();
            }}, 500);
        }}
        
        // 地图加载错误
        function onMapError(event) {{
            console.error('3D地图加载错误:', event);
            showError('3D地图加载失败，请检查API密钥和网络连接');
        }}
        
        // 加载航线数据
        function loadRoutes() {{
            console.log('开始加载航线数据...', ROUTE_DATA.length, '条航线');
            updateStatus('正在加载航线数据...');
            
            if (ROUTE_DATA && ROUTE_DATA.length > 0) {{
                // 设置地图视角
                if (map3d && map3d.flyCameraTo) {{
                    map3d.flyCameraTo({{
                        center: CONFIG.center,
                        zoom: CONFIG.zoom,
                        tilt: CONFIG.tilt,
                        heading: CONFIG.heading
                    }});
                }}
            }}
        }}
        
        // 显示错误信息
        function showError(message) {{
            const container = document.getElementById('map-container');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = message;
            container.appendChild(errorDiv);
            
            // 隐藏加载遮罩
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {{
                overlay.style.display = 'none';
            }}
        }}
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('开始初始化3D地图应用...');
            setTimeout(initMap3D, 1000);
        }});
    """
    
    # 组合HTML内容
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D航线地图</title>
    <style>
{css_styles}
    </style>
</head>
<body>
    <div id="map-container">
        <div id="loading-overlay">
            <div class="loading-spinner"></div>
            <div class="loading-text">正在初始化3D地图...</div>
            <div class="loading-subtitle">请稍候</div>
            <div class="progress-container">
                <div class="progress-bar" id="progress-bar">
                    <div class="progress-airplane">✈️</div>
                </div>
                <div class="progress-track"></div>
            </div>
            <div class="progress-text">加载中...</div>
        </div>
        
        <gmp-map-3d id="map3d" 
                    map-id="{map_id}"
                    center="{CONFIG['center']['lat']},{CONFIG['center']['lng']}"
                    zoom="{CONFIG['zoom']}"
                    tilt="{CONFIG['tilt']}"
                    heading="{CONFIG['heading']}">
        </gmp-map-3d>
        
        <div class="stats-container">
            <div class="stats-item">航线: <span id="route-count">0</span></div>
            <div class="stats-item">机场: <span id="airport-count">0</span></div>
            <div class="stats-item">航司: <span id="airline-count">0</span></div>
        </div>
    </div>
    
    <script>
{javascript_code}
    </script>
</body>
</html>
    """
    
    return html_content

def render_fixed_3d_map(route_data: List[Dict[str, Any]], height: int = 700) -> Optional[Dict]:
    """
    渲染修复版本的3D地图
    
    Args:
        route_data: 航线数据
        height: 地图高度
    
    Returns:
        组件返回的数据
    """
    
    # 检查配置
    if not is_maps_configured():
        st.warning("⚠️ Google Maps API未配置，无法使用3D地图功能")
        show_maps_config_status()
        return None
    
    # 获取配置
    api_key = get_api_key()
    map_id = get_map_id()
    
    if not api_key or not map_id:
        st.error("❌ API密钥或地图ID未配置")
        return None
    
    # 数据验证
    if not route_data:
        st.warning("📊 没有可显示的航线数据")
        return None
    
    try:
        # 生成HTML
        html_content = create_fixed_3d_map_html(route_data, api_key, map_id, height)
        
        # 渲染组件
        st.markdown("### 🌐 3D航线地图 (优化版)")
        st.info("💡 此版本已优化CDN资源加载，提供更稳定的3D地图体验")
        
        component_value = components.html(
            html_content,
            height=height + 50,
            scrolling=False
        )
        
        return component_value
        
    except Exception as e:
        st.error(f"❌ 3D地图渲染失败: {{str(e)}}")
        return None

if __name__ == "__main__":
    st.title("3D地图CDN修复测试")
    
    # 测试数据
    test_data = [
        {{
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
            'aircraft_type': 'B777-300ER',
            'route_type': 'international'
        }}
    ]
    
    render_fixed_3d_map(test_data)
