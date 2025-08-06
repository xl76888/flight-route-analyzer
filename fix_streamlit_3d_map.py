#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Streamlit应用中3D地图加载问题
解决航线可视化工具中3D地图选项无法正常显示的问题
"""

import os
from pathlib import Path
import shutil

def fix_map3d_component():
    """修复map3d_component.html文件"""
    print("🔧 修复3D地图组件...")
    
    component_path = Path("D:/flight_tool/components/map3d/map3d_component.html")
    
    # 创建修复后的HTML内容
    fixed_html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D航线地图</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Microsoft YaHei', sans-serif;
            background: #f5f5f5;
        }
        
        #map3d-container {
            width: 100%;
            height: 600px;
            position: relative;
            background: #f0f0f0;
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
            background: rgba(255, 255, 255, 0.95);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-text {
            color: #666;
            font-size: 14px;
            text-align: center;
        }
        
        .error-message {
            color: #e74c3c;
            text-align: center;
            padding: 20px;
            background: #fff;
            border-radius: 8px;
            margin: 20px;
            border: 1px solid #e74c3c;
        }
        
        .success-message {
            color: #27ae60;
            text-align: center;
            padding: 10px;
            background: #d4edda;
            border-radius: 4px;
            margin: 10px;
            border: 1px solid #27ae60;
        }
        
        #map3d {
            width: 100%;
            height: 100%;
            display: none;
        }
        
        .status-bar {
            position: absolute;
            bottom: 10px;
            left: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            color: #666;
            z-index: 100;
        }
        
        .controls {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 4px;
            z-index: 100;
            display: none;
        }
        
        .control-item {
            margin-bottom: 5px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div id="map3d-container">
        <!-- 加载状态 -->
        <div id="loading-overlay">
            <div class="loading-spinner"></div>
            <div class="loading-text">正在加载3D地图...</div>
            <div style="margin-top: 10px; color: #666;">正在加载3D地图...</div>
        </div>
        
        <!-- 状态栏 -->
        <div class="status-bar" id="status-bar">
            <div>状态: <span id="status-text">初始化中...</span></div>
            <div>API状态: <span id="api-status">检查中...</span></div>
            <div>渲染模式: <span id="render-mode">3D</span></div>
        </div>
        
        <!-- 3D地图将在这里渲染 -->
        <gmp-map-3d id="map3d"
            center="39.9042,116.4074"
            zoom="5"
            map-id="{{MAP_ID}}"
            mode="HYBRID"
            tilt="45"
            heading="0">
        </gmp-map-3d>
        
        <!-- 控制面板 -->
        <div class="controls" id="controls">
            <div class="control-item">缩放: <span id="zoom-level">5</span></div>
            <div class="control-item">倾斜: <span id="tilt-angle">45°</span></div>
        </div>
    </div>
    
    <script>
        // 配置数据
        const CONFIG = {{CONFIG}};
        const ROUTE_DATA = {{ROUTE_DATA}};
        
        // 全局变量
        let map3d = null;
        let isMapLoaded = false;
        let loadStartTime = Date.now();
        
        // 状态更新函数
        function updateStatus(text) {
            const statusElement = document.getElementById('status-text');
            if (statusElement) {
                statusElement.textContent = text;
            }
            console.log('状态更新:', text);
        }
        
        function updateApiStatus(text) {
            const apiStatusElement = document.getElementById('api-status');
            if (apiStatusElement) {
                apiStatusElement.textContent = text;
            }
        }
        
        // 初始化3D地图
        async function initMap3D() {
            console.log('开始初始化3D地图...');
            updateStatus('正在初始化...');
            
            try {
                // 检查API密钥
                if (!CONFIG.apiKey || CONFIG.apiKey === 'YOUR_API_KEY') {
                    throw new Error('API密钥未配置');
                }
                updateApiStatus('API密钥已配置');
                
                // 动态加载Google Maps API
                if (typeof google === 'undefined' || !google.maps) {
                    updateStatus('加载Google Maps API...');
                    await loadGoogleMapsAPI();
                }
                updateApiStatus('API已加载');
                
                // 获取地图元素
                map3d = document.getElementById('map3d');
                if (!map3d) {
                    throw new Error('无法找到3D地图容器');
                }
                
                // 设置事件监听
                map3d.addEventListener('gmp-load', onMapLoaded);
                map3d.addEventListener('gmp-error', onMapError);
                
                // 显示地图
                map3d.style.display = 'block';
                updateStatus('等待地图加载...');
                
                console.log('3D地图初始化完成');
                
            } catch (error) {
                console.error('3D地图初始化失败:', error);
                showError('3D地图初始化失败: ' + error.message);
            }
        }
        
        // 动态加载Google Maps API
        function loadGoogleMapsAPI() {
            return new Promise((resolve, reject) => {
                if (typeof google !== 'undefined' && google.maps) {
                    resolve();
                    return;
                }
                
                const script = document.createElement('script');
                script.src = `https://maps.googleapis.com/maps/api/js?key=${CONFIG.apiKey}&libraries=maps3d&v=beta`;
                script.async = true;
                script.defer = true;
                
                script.onload = () => {
                    console.log('Google Maps API加载完成');
                    resolve();
                };
                
                script.onerror = () => {
                    console.error('Google Maps API加载失败');
                    reject(new Error('Google Maps API加载失败，请检查网络连接'));
                };
                
                document.head.appendChild(script);
            });
        }
        
        // 地图加载完成事件
        function onMapLoaded() {
            const loadTime = Date.now() - loadStartTime;
            console.log('3D地图加载完成');
            
            // 隐藏加载状态
            const loadingOverlay = document.getElementById('loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
            }
            
            // 显示控制面板
            const controls = document.getElementById('controls');
            if (controls) {
                controls.style.display = 'block';
            }
            
            updateStatus('地图加载成功');
            updateApiStatus(`加载完成 (${loadTime}ms)`);
            isMapLoaded = true;
            
            // 发送成功事件到Streamlit
            window.parent.postMessage({
                type: 'map3d-ready',
                data: { loadTime, routeCount: ROUTE_DATA.length }
            }, '*');
            
            // 加载航线数据
            loadRoutes();
        }
        
        // 地图加载错误事件
        function onMapError(event) {
            console.error('3D地图加载错误:', event);
            showError('3D地图加载失败，请检查API密钥和网络连接');
            updateStatus('加载失败');
            updateApiStatus('错误');
        }
        
        // 显示错误信息
        function showError(message) {
            const loadingOverlay = document.getElementById('loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.innerHTML = `
                    <div class="error-message">
                        <h3>❌ 加载失败</h3>
                        <p>${message}</p>
                        <button onclick="location.reload()">重新加载</button>
                    </div>
                `;
            }
        }
        
        // 加载航线数据
        function loadRoutes() {
            if (!isMapLoaded || !map3d) return;
            
            console.log('开始加载航线数据:', ROUTE_DATA.length, '条');
            updateStatus(`已加载 ${ROUTE_DATA.length} 条航线`);
            
            // 设置地图视角
            if (ROUTE_DATA.length > 0) {
                map3d.flyCameraTo({
                    endCamera: {
                        center: CONFIG.center || { lat: 39.9042, lng: 116.4074 },
                        zoom: CONFIG.zoom || 5,
                        tilt: CONFIG.tilt || 45,
                        heading: CONFIG.heading || 0
                    },
                    durationMillis: 2000
                });
            }
        }
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', () => {
            console.log('页面加载完成，开始初始化3D地图');
            setTimeout(initMap3D, 500); // 延迟500ms确保DOM完全准备好
        });
        
        // 错误处理
        window.addEventListener('error', (event) => {
            console.error('页面错误:', event.error);
            updateStatus('发生错误');
        });
        
        // 调试信息
        console.log('3D地图组件已加载');
        console.log('配置信息:', CONFIG);
        console.log('航线数据:', ROUTE_DATA.length, '条');
    </script>
</body>
</html>
'''
    
    # 确保目录存在
    component_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入修复后的文件
    with open(component_path, 'w', encoding='utf-8') as f:
        f.write(fixed_html)
    
    print(f"✅ 3D地图组件已修复: {component_path}")
    return component_path

def fix_map3d_integration():
    """修复map3d_integration.py中的问题"""
    print("🔧 修复3D地图集成模块...")
    
    integration_path = Path("D:/flight_tool/map3d_integration.py")
    
    # 读取原文件
    with open(integration_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复HTML模板中的问题
    # 替换默认模板中的API加载逻辑
    old_template_start = "return '''"
    new_template_start = "return '''"
    
    if old_template_start in content:
        # 找到模板开始位置
        start_pos = content.find(old_template_start)
        if start_pos != -1:
            # 找到模板结束位置
            end_pos = content.find("'''\n    ", start_pos + len(old_template_start))
            if end_pos != -1:
                # 替换整个模板
                new_template = '''
return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D航线地图</title>
    <style>
        body { margin: 0; padding: 0; font-family: 'Microsoft YaHei', sans-serif; }
        #map3d-container { width: 100%; height: 100%; position: relative; }
        #loading { 
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            text-align: center; color: #666;
        }
        .error { color: #e74c3c; text-align: center; padding: 20px; }
        #map3d { width: 100%; height: 100%; }
    </style>
</head>
<body>
    <div id="map3d-container">
        <div id="loading">正在加载3D地图...</div>
        <gmp-map-3d id="map3d" map-id="{{MAP_ID}}" mode="HYBRID" 
                     center="39.9042,116.4074" zoom="5" tilt="45" 
                     style="width: 100%; height: 100%; display: none;"></gmp-map-3d>
    </div>
    
    <script>
        const CONFIG = {{CONFIG}};
        const ROUTE_DATA = {{ROUTE_DATA}};
        
        async function initMap() {
            try {
                if (!window.google) {
                    const script = document.createElement('script');
                    script.src = `https://maps.googleapis.com/maps/api/js?key=${CONFIG.apiKey}&libraries=maps3d&v=beta`;
                    document.head.appendChild(script);
                    
                    await new Promise((resolve, reject) => {
                        script.onload = resolve;
                        script.onerror = () => reject(new Error('API加载失败'));
                    });
                }
                
                const map = document.getElementById('map3d');
                map.addEventListener('gmp-load', () => {
                    document.getElementById('loading').style.display = 'none';
                    map.style.display = 'block';
                    console.log('3D地图加载成功');
                });
                
                map.addEventListener('gmp-error', (event) => {
                    document.getElementById('loading').innerHTML = 
                        '<div class="error">地图加载失败: ' + event.detail + '</div>';
                });
                
            } catch (error) {
                document.getElementById('loading').innerHTML = 
                    '<div class="error">地图加载失败: ' + error.message + '</div>';
            }
        }
        
        document.addEventListener('DOMContentLoaded', initMap);
    </script>
</body>
</html>
"""'''
                
                # 替换内容
                content = content[:start_pos] + new_template + content[end_pos + 3:]
    
    # 写入修复后的文件
    with open(integration_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 3D地图集成模块已修复: {integration_path}")
    return integration_path

def create_test_page():
    """创建测试页面验证修复效果"""
    print("🔧 创建测试页面...")
    
    test_path = Path("D:/flight_tool/test_streamlit_3d_fix.html")
    
    test_html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Streamlit 3D地图修复测试</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .test-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .success { background: #d4edda; border-color: #c3e6cb; }
        .warning { background: #fff3cd; border-color: #ffeaa7; }
        .error { background: #f8d7da; border-color: #f5c6cb; }
        iframe { width: 100%; height: 600px; border: 1px solid #ccc; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Streamlit 3D地图修复测试</h1>
        
        <div class="test-section success">
            <h2>✅ 修复内容</h2>
            <ul>
                <li>修复了map3d_component.html中的API加载逻辑</li>
                <li>优化了错误处理和状态显示</li>
                <li>改进了地图初始化流程</li>
                <li>添加了详细的调试信息</li>
            </ul>
        </div>
        
        <div class="test-section warning">
            <h2>⚠️ 测试说明</h2>
            <p>修复完成后，请按以下步骤测试：</p>
            <ol>
                <li>重启Streamlit应用</li>
                <li>上传航线数据文件</li>
                <li>在侧边栏选择"3D地图"</li>
                <li>观察地图是否正常加载</li>
            </ol>
        </div>
        
        <div class="test-section">
            <h2>🌐 3D地图组件测试</h2>
            <p>以下是修复后的3D地图组件预览：</p>
            <iframe src="file:///D:/flight_tool/components/map3d/map3d_component.html"></iframe>
        </div>
        
        <div class="test-section">
            <h2>📋 故障排查</h2>
            <p>如果3D地图仍无法加载，请检查：</p>
            <ul>
                <li>✅ Google Maps API密钥是否正确配置</li>
                <li>✅ 网络连接是否正常（需要访问Google服务）</li>
                <li>✅ 浏览器是否支持WebGL</li>
                <li>✅ API配额是否充足</li>
            </ul>
        </div>
    </div>
</body>
</html>
'''
    
    with open(test_path, 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print(f"✅ 测试页面已创建: {test_path}")
    return test_path

def main():
    """主函数"""
    print("🚀 Streamlit 3D地图修复工具")
    print("=" * 50)
    
    try:
        # 1. 修复3D地图组件
        component_path = fix_map3d_component()
        
        # 2. 修复集成模块
        integration_path = fix_map3d_integration()
        
        # 3. 创建测试页面
        test_path = create_test_page()
        
        print("\n" + "=" * 50)
        print("✅ 修复完成！")
        print("\n📁 修复的文件：")
        print(f"   - {component_path}")
        print(f"   - {integration_path}")
        print(f"   - {test_path}")
        
        print("\n🔄 下一步操作：")
        print("1. 重启Streamlit应用")
        print("2. 上传航线数据文件")
        print("3. 选择'3D地图'模式")
        print("4. 验证地图是否正常加载")
        
        print("\n💡 重要提示：")
        print("- 确保网络可以访问Google服务")
        print("- 检查API密钥配置是否正确")
        print("- 如果仍有问题，查看浏览器控制台错误信息")
        
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()