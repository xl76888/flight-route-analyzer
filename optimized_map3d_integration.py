
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的3D地图集成模块
支持数据动态更新，避免重复加载
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
import time
import hashlib
from typing import Dict, List, Any, Optional
from config.google_maps_config import get_api_key, get_map_id, is_maps_configured, show_maps_config_status

class OptimizedMap3DIntegration:
    """
    优化的3D地图集成类
    """
    
    def __init__(self):
        # 修正路径问题
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.component_path = os.path.join(base_dir, 'components', 'map3d')
        self.current_data = []
        self.is_initialized = False
        self.component_key = 'optimized_map3d'
        self.last_render_time = 0
        
        # 确保组件目录存在
        if not os.path.exists(self.component_path):
            st.error(f"❌ 3D地图组件目录不存在: {self.component_path}")
            st.info("💡 请检查项目文件结构是否完整")
        
    def render_map3d(self, 
                     route_data: List[Dict[str, Any]], 
                     height: int = 600,
                     api_key: str = None,
                     map_id: str = None,
                     force_reload: bool = False,
                     key: str = None,
                     **kwargs) -> Optional[Dict]:
        """
        渲染优化的3D地图组件
        
        Args:
            route_data: 航线数据列表
            height: 地图高度
            api_key: Google Maps API密钥
            map_id: Google Maps地图ID
            force_reload: 是否强制重新加载
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
        
        # 生成唯一的组件键值，确保每次地图类型切换都重新渲染
        current_time = int(time.time())
        data_hash = self._generate_data_hash(processed_data)
        map_type = st.session_state.get('map_type', '2D地图')
        
        # 使用传入的key参数或生成默认key
        if key:
            self.component_key = key
        else:
            self.component_key = f"map3d_{data_hash}_{current_time}"
        
        # 检查是否需要重新加载组件
        data_changed = self._has_data_changed(processed_data)
        
        # 如果是3D地图且数据发生变化，或者强制重新加载，或者有自定义key，则重新渲染
        if (map_type == '3D地图' and 
            (data_changed or 
             force_reload or 
             key or 
             not self.is_initialized)):
            self.last_render_time = current_time
            return self._render_full_component(processed_data, api_key, map_id, height, **kwargs)
        
        if not self.is_initialized or force_reload:
            # 首次加载或强制重新加载
            return self._render_full_component(processed_data, api_key, map_id, height, **kwargs)
        elif data_changed:
            # 数据变化，仅更新数据
            return self._update_component_data(processed_data)
        else:
            # 数据未变化，返回缓存的组件
            return self._get_cached_component()
    
    def _render_full_component(self, processed_data, api_key, map_id, height, **kwargs):
        """
        渲染完整的组件
        """
        # 生成HTML内容
        html_content = self._generate_optimized_html(
            processed_data, 
            api_key=api_key,
            map_id=map_id,
            **kwargs
        )
        
        # 渲染组件 - 添加强制高度样式
        iframe_style = f"""
        <style>
        iframe[title="streamlit_app"] {{
            height: {height}px !important;
            min-height: {height}px !important;
        }}
        </style>
        """
        
        # 在HTML内容前添加样式
        html_with_style = iframe_style + html_content
        
        component_value = components.html(
            html_with_style,
            height=height,
            scrolling=False)
        
        self.current_data = processed_data
        self.is_initialized = True
        
        return component_value
    
    def _update_component_data(self, processed_data):
        """
        更新组件数据（不重新加载整个组件）
        """
        # 通过JavaScript消息更新数据
        update_script = f"""
        <script>
        if (window.parent) {{
            window.parent.postMessage({{
                type: 'update-routes',
                routes: {json.dumps(processed_data, ensure_ascii=False)}
            }}, '*');
        }}
        </script>
        """
        
        # 显示更新指示器
        st.info(f"🔄 数据已更新: {len(processed_data)} 条航线")
        
        # 执行更新脚本
        components.html(update_script, height=0)
        
        self.current_data = processed_data
        
        return {'updated': True, 'route_count': len(processed_data)}
    
    def _get_cached_component(self):
        """
        获取缓存的组件
        """
        return {'cached': True, 'route_count': len(self.current_data)}
    
    def _has_data_changed(self, new_data):
        """
        检查数据是否发生变化
        """
        if len(new_data) != len(self.current_data):
            return True
        
        # 简单的数据比较（可以根据需要优化）
        for i, (new_route, old_route) in enumerate(zip(new_data, self.current_data)):
            if (new_route.get('start_airport') != old_route.get('start_airport') or
                new_route.get('end_airport') != old_route.get('end_airport') or
                new_route.get('direction') != old_route.get('direction') or  # 检查方向字段变化
                new_route.get('frequency') != old_route.get('frequency')):
                return True
        
        return False
    
    def _generate_data_hash(self, data: List[Dict[str, Any]]) -> str:
        """
        生成数据的哈希值
        """
        if not data:
            return "empty"
        
        # 创建数据的字符串表示
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        
        # 生成MD5哈希
        hash_obj = hashlib.md5(data_str.encode('utf-8'))
        return hash_obj.hexdigest()[:8]  # 只取前8位
    
    def _preprocess_data(self, route_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        预处理航线数据
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
                'route_type': str(route.get('route_type', 'domestic')),
                'direction': str(route.get('direction', '出口'))  # 保留方向字段
            }
            
            processed.append(standardized)
        
        return processed
    
    def _validate_route(self, route: Dict[str, Any]) -> bool:
        """
        验证航线数据
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
    
    def _generate_optimized_html(self, route_data, api_key, map_id, **kwargs):
        """
        生成优化的HTML内容
        """
        # 读取优化的HTML模板
        template_path = os.path.join(self.component_path, 'optimized_map3d_component.html')
        
        # 调试信息
        st.write(f"🔍 调试信息: 模板路径 = {template_path}")
        st.write(f"🔍 调试信息: 路径存在 = {os.path.exists(template_path)}")
        
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    html_template = f.read()
                st.success(f"✅ 成功读取3D地图模板 ({len(html_template)} 字符)")
            except Exception as e:
                st.error(f"❌ 读取模板文件失败: {str(e)}")
                raise
        else:
            st.error(f"❌ 3D地图模板文件不存在: {template_path}")
            # 列出实际存在的文件
            if os.path.exists(self.component_path):
                files = os.listdir(self.component_path)
                st.info(f"📁 目录中的文件: {files}")
            raise FileNotFoundError(f"优化的3D地图模板未找到: {template_path}")
        
        # 准备数据
        data_json = json.dumps(route_data, ensure_ascii=False, indent=2)
        
        # 配置参数
        config = {
            'apiKey': api_key,
            'mapId': map_id,
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

# 创建全局实例
optimized_map3d_integration = OptimizedMap3DIntegration()

def render_optimized_3d_map(route_data: List[Dict[str, Any]], **kwargs) -> Optional[Dict]:
    """
    便捷函数: 渲染优化的3D地图
    
    Args:
        route_data: 航线数据
        **kwargs: 其他参数
        
    Returns:
        组件返回值
    """
    return optimized_map3d_integration.render_map3d(route_data, **kwargs)
