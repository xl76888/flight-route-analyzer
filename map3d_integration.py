# -*- coding: utf-8 -*-
"""
3D地图集成模块
负责在Streamlit应用中集成3D地图功能
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
from typing import List, Dict, Any, Optional
import pandas as pd
from config.google_maps_config import get_api_key, get_map_id, is_maps_configured, show_maps_config_status

class Map3DIntegration:
    """3D地图集成类"""
    
    def __init__(self):
        self.component_path = os.path.join(os.path.dirname(__file__), 'components', 'map3d')
        self.is_initialized = False
        self.current_data = None
        
        # 确保组件目录存在
        os.makedirs(self.component_path, exist_ok=True)
    
    def render_map3d(self, 
                     route_data: List[Dict[str, Any]], 
                     height: int = 600,
                     api_key: str = None,
                     map_id: str = None,
                     **kwargs) -> Optional[Dict]:
        """
        渲染3D地图组件
        
        Args:
            route_data: 航线数据列表
            height: 地图高度
            api_key: Google Maps API密钥
            map_id: Google Maps地图ID
            **kwargs: 其他配置参数
            
        Returns:
            组件返回的数据
        """
        
        # 检查配置状态
        if not is_maps_configured():
            st.warning("⚠️ Google Maps API未配置，无法使用3D地图功能")
            show_maps_config_status()
            return None
        
        # 使用配置的API密钥和地图ID
        if not api_key:
            api_key = get_api_key()
        if not map_id:
            map_id = get_map_id()
        
        # 数据预处理
        processed_data = self._preprocess_data(route_data)
        
        # 生成HTML内容
        html_content = self._generate_html(
            processed_data, 
            api_key=api_key,
            map_id=map_id,
            **kwargs
        )
        
        # 渲染组件
        component_value = components.html(
            html_content,
            height=height,
            scrolling=False
        )
        
        self.current_data = processed_data
        self.is_initialized = True
        
        return component_value
    
    def _preprocess_data(self, route_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        预处理航线数据
        
        Args:
            route_data: 原始航线数据
            
        Returns:
            处理后的数据
        """
        if not route_data:
            return []
        
        processed = []
        
        for i, route in enumerate(route_data):
            # 验证必需字段
            if not self._validate_route(route):
                continue
            
            # 标准化数据格式
            standardized = {
                'id': f'route_{i}',
                'start_airport': str(route.get('start_airport', '')),
                'end_airport': str(route.get('end_airport', '')),
                'start_lat': float(route.get('start_lat', 0)),
                'start_lng': float(route.get('start_lng', 0)),
                'end_lat': float(route.get('end_lat', 0)),
                'end_lng': float(route.get('end_lng', 0)),
                'frequency': int(route.get('frequency', 1)),
                'airline': str(route.get('airline', '')),
                'aircraft_type': str(route.get('aircraft_type', '')),
                'route_type': str(route.get('route_type', 'domestic'))
            }
            
            # 添加扩展信息
            standardized.update({
                'start_airport_name': str(route.get('start_airport_name', '')),
                'end_airport_name': str(route.get('end_airport_name', '')),
                'distance': self._calculate_distance(
                    standardized['start_lat'], standardized['start_lng'],
                    standardized['end_lat'], standardized['end_lng']
                )
            })
            
            processed.append(standardized)
        
        return processed
    
    def _validate_route(self, route: Dict[str, Any]) -> bool:
        """
        验证航线数据有效性
        
        Args:
            route: 航线数据
            
        Returns:
            是否有效
        """
        required_fields = ['start_lat', 'start_lng', 'end_lat', 'end_lng']
        
        for field in required_fields:
            if field not in route:
                return False
            
            try:
                value = float(route[field])
                if field.endswith('_lat') and (value < -90 or value > 90):
                    return False
                if field.endswith('_lng') and (value < -180 or value > 180):
                    return False
            except (ValueError, TypeError):
                return False
        
        return True
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        计算两点间距离（公里）
        
        Args:
            lat1, lng1: 起点坐标
            lat2, lng2: 终点坐标
            
        Returns:
            距离（公里）
        """
        import math
        
        R = 6371  # 地球半径（公里）
        
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _generate_html(self, 
                      route_data: List[Dict[str, Any]], 
                      api_key: str = None,
                      map_id: str = None,
                      **kwargs) -> str:
        """
        生成3D地图HTML内容
        
        Args:
            route_data: 航线数据
            api_key: Google Maps API密钥
            map_id: 地图ID
            **kwargs: 其他配置
            
        Returns:
            HTML字符串
        """
        
        # 读取HTML模板
        template_path = os.path.join(self.component_path, 'map3d_component.html')
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
        else:
            # 如果模板文件不存在，使用内嵌模板
            html_template = self._get_default_template()
        
        # 准备数据
        data_json = json.dumps(route_data, ensure_ascii=False, indent=2)
        
        # 配置参数
        config = {
            'apiKey': api_key or get_api_key(),
            'mapId': map_id or get_map_id(),
            'center': kwargs.get('center', {'lat': 39.9042, 'lng': 116.4074}),
            'zoom': kwargs.get('zoom', 5),
            'tilt': kwargs.get('tilt', 45),
            'heading': kwargs.get('heading', 0)
        }
        
        config_json = json.dumps(config, ensure_ascii=False, indent=2)
        
        # 替换模板中的占位符
        html_content = html_template.replace('{{ROUTE_DATA}}', data_json)
        html_content = html_content.replace('{{CONFIG}}', config_json)
        html_content = html_content.replace('{{API_KEY}}', config['apiKey'])
        html_content = html_content.replace('{{MAP_ID}}', config['mapId'])
        
        return html_content
    
    def _get_default_template(self) -> str:
        """
        获取默认HTML模板 - 修复版本，移除有问题的3D地图元素
        
        Returns:
            HTML模板字符串
        """
        return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>航线地图</title>
    <style>
        body { 
            margin: 0; 
            padding: 0; 
            font-family: 'Microsoft YaHei', sans-serif;
            background: #f5f5f5;
        }
        #map-container { 
            width: 100%; 
            height: 100%; 
            position: relative;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        #map { 
            width: 100%; 
            height: 100%;
            border-radius: 8px;
        }
        .info-panel {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            max-width: 300px;
            z-index: 1000;
        }
        .route-count {
            font-size: 14px;
            color: #333;
            margin-bottom: 10px;
        }
        .legend {
            font-size: 12px;
            color: #666;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
        }
        .legend-color {
            width: 20px;
            height: 3px;
            margin-right: 8px;
            border-radius: 2px;
        }
    </style>
</head>
<body>
    <div id="map-container">
        <div id="map"></div>
        <div class="info-panel">
            <div class="route-count">📊 航线总数: <span id="route-count">0</span></div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #4CAF50;"></div>
                    <span>国际进口航线</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #FFC107;"></div>
                    <span>国际出口航线</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const CONFIG = {{CONFIG}};
        const ROUTE_DATA = {{ROUTE_DATA}};
        let map;
        
        function initMap() {
            try {
                // 使用标准Google Maps而不是3D版本
                map = new google.maps.Map(document.getElementById('map'), {
                    center: { lat: 39.9042, lng: 116.4074 },
                    zoom: 5,
                    mapTypeId: 'roadmap',
                    styles: [
                        {
                            featureType: 'water',
                            elementType: 'geometry',
                            stylers: [{ color: '#e9e9e9' }, { lightness: 17 }]
                        },
                        {
                            featureType: 'landscape',
                            elementType: 'geometry',
                            stylers: [{ color: '#f5f5f5' }, { lightness: 20 }]
                        }
                    ]
                });
                
                // 更新航线计数
                document.getElementById('route-count').textContent = ROUTE_DATA.length;
                
                // 绘制航线
                drawRoutes();
                
                console.log('地图初始化完成，航线数据:', ROUTE_DATA.length);
                
            } catch (error) {
                console.error('地图初始化失败:', error);
                document.getElementById('map').innerHTML = 
                    '<div style="padding: 20px; text-align: center; color: #e74c3c;">地图加载失败: ' + error.message + '</div>';
            }
        }
        
        function drawRoutes() {
            if (!map || !ROUTE_DATA) return;
            
            ROUTE_DATA.forEach((route, index) => {
                if (route.origin_coords && route.dest_coords) {
                    const path = [
                        { lat: route.origin_coords[0], lng: route.origin_coords[1] },
                        { lat: route.dest_coords[0], lng: route.dest_coords[1] }
                    ];
                    
                    const color = route.route_type === '国际进口' ? '#4CAF50' : '#FFC107';
                    
                    const polyline = new google.maps.Polyline({
                        path: path,
                        geodesic: true,
                        strokeColor: color,
                        strokeOpacity: 0.8,
                        strokeWeight: Math.max(2, Math.min(8, route.frequency / 2))
                    });
                    
                    polyline.setMap(map);
                }
            });
        }
        
        // 加载Google Maps API
        function loadGoogleMaps() {
            if (window.google && window.google.maps) {
                initMap();
                return;
            }
            
            const script = document.createElement('script');
            script.src = `https://maps.googleapis.com/maps/api/js?key=${CONFIG.apiKey}&callback=initMap`;
            script.async = true;
            script.defer = true;
            document.head.appendChild(script);
        }
        
        // 页面加载完成后初始化
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', loadGoogleMaps);
        } else {
            loadGoogleMaps();
        }
    </script>
</body>
</html>
        '''
    
    def create_control_panel(self) -> Dict[str, Any]:
        """
        创建3D地图控制面板
        
        Returns:
            控制面板配置
        """
        st.subheader("🌐 3D地图控制")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            view_mode = st.selectbox(
                "视图模式",
                ["标准视图", "鸟瞰视图", "侧视图", "自由视角"],
                key="map3d_view_mode"
            )
        
        with col2:
            animation_enabled = st.checkbox(
                "启用动画",
                value=True,
                key="map3d_animation"
            )
        
        with col3:
            show_labels = st.checkbox(
                "显示标签",
                value=True,
                key="map3d_labels"
            )
        
        # 高级设置
        with st.expander("高级设置"):
            col1, col2 = st.columns(2)
            
            with col1:
                altitude_scale = st.slider(
                    "高度缩放",
                    min_value=0.5,
                    max_value=3.0,
                    value=1.0,
                    step=0.1,
                    key="map3d_altitude_scale"
                )
                
                line_width_scale = st.slider(
                    "线条宽度",
                    min_value=0.5,
                    max_value=3.0,
                    value=1.0,
                    step=0.1,
                    key="map3d_line_width"
                )
            
            with col2:
                opacity = st.slider(
                    "透明度",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.8,
                    step=0.1,
                    key="map3d_opacity"
                )
                
                render_quality = st.selectbox(
                    "渲染质量",
                    ["低", "中", "高", "超高"],
                    index=2,
                    key="map3d_quality"
                )
        
        return {
            'view_mode': view_mode,
            'animation_enabled': animation_enabled,
            'show_labels': show_labels,
            'altitude_scale': altitude_scale,
            'line_width_scale': line_width_scale,
            'opacity': opacity,
            'render_quality': render_quality
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取3D地图统计信息
        
        Returns:
            统计信息字典
        """
        if not self.current_data:
            return {}
        
        # 计算统计信息
        total_routes = len(self.current_data)
        
        airports = set()
        airlines = set()
        route_types = {}
        total_frequency = 0
        
        for route in self.current_data:
            airports.add(route.get('start_airport', ''))
            airports.add(route.get('end_airport', ''))
            
            if route.get('airline'):
                airlines.add(route['airline'])
            
            route_type = route.get('route_type', 'unknown')
            route_types[route_type] = route_types.get(route_type, 0) + 1
            
            total_frequency += route.get('frequency', 0)
        
        return {
            'total_routes': total_routes,
            'unique_airports': len(airports),
            'unique_airlines': len(airlines),
            'route_types': route_types,
            'total_frequency': total_frequency,
            'average_frequency': total_frequency / total_routes if total_routes > 0 else 0
        }
    
    def export_data(self, format_type: str = 'json') -> str:
        """
        导出当前3D地图数据
        
        Args:
            format_type: 导出格式 ('json', 'csv')
            
        Returns:
            导出的数据字符串
        """
        if not self.current_data:
            return ""
        
        if format_type.lower() == 'json':
            return json.dumps(self.current_data, ensure_ascii=False, indent=2)
        elif format_type.lower() == 'csv':
            df = pd.DataFrame(self.current_data)
            return df.to_csv(index=False)
        else:
            raise ValueError(f"不支持的导出格式: {format_type}")

# 创建全局实例
map3d_integration = Map3DIntegration()

def render_3d_map(route_data: List[Dict[str, Any]], **kwargs) -> Optional[Dict]:
    """
    便捷函数: 渲染3D地图
    
    Args:
        route_data: 航线数据
        **kwargs: 其他参数
        
    Returns:
        组件返回值
    """
    return map3d_integration.render_map3d(route_data, **kwargs)

def create_3d_control_panel() -> Dict[str, Any]:
    """
    便捷函数: 创建3D地图控制面板
    
    Returns:
        控制面板配置
    """
    return map3d_integration.create_control_panel()

def get_3d_map_stats() -> Dict[str, Any]:
    """
    便捷函数: 获取3D地图统计信息
    
    Returns:
        统计信息
    """
    return map3d_integration.get_statistics()