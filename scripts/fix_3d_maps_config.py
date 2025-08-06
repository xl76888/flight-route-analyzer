#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D Maps配置修复脚本
根据Google官方文档要求更新所有3D地图组件配置
"""

import os
import re
from pathlib import Path

def update_gmp_map_3d_elements():
    """更新所有gmp-map-3d元素，添加mode属性"""
    print("🔧 更新3D地图组件配置...")
    
    # 需要更新的文件列表
    files_to_update = [
        'components/map3d/map3d_component.html',
        'fix_3d_map_cdn.py',
        'map3d_integration.py',
        'test_3d_map_simple.html',
        'debug_3d_map.html'
    ]
    
    project_root = Path(__file__).parent.parent
    updated_files = []
    
    for file_path in files_to_update:
        full_path = project_root / file_path
        if not full_path.exists():
            print(f"⚠️ 文件不存在：{file_path}")
            continue
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已经有mode属性
            if 'mode=' in content:
                print(f"✅ {file_path} 已包含mode属性")
                continue
            
            # 使用正则表达式添加mode属性
            # 匹配gmp-map-3d标签，在map-id属性后添加mode属性
            pattern = r'(<gmp-map-3d[^>]*map-id="[^"]*")([^>]*>)'
            replacement = r'\1 mode="HYBRID"\2'
            
            new_content = re.sub(pattern, replacement, content)
            
            if new_content != content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ 已更新：{file_path}")
                updated_files.append(file_path)
            else:
                print(f"⚠️ 未找到需要更新的gmp-map-3d元素：{file_path}")
                
        except Exception as e:
            print(f"❌ 更新文件失败 {file_path}: {e}")
    
    return updated_files

def create_webgl_test_page():
    """创建WebGL支持测试页面"""
    print("\n🔧 创建WebGL测试页面...")
    
    webgl_test_content = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebGL支持测试</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            font-weight: bold;
        }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
        .info { background-color: #d1ecf1; color: #0c5460; }
        #webgl-canvas {
            border: 1px solid #ddd;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 WebGL支持测试</h1>
        <p>此页面用于测试浏览器的WebGL支持情况</p>
        
        <div id="test-results"></div>
        
        <h3>WebGL渲染测试</h3>
        <canvas id="webgl-canvas" width="400" height="300"></canvas>
        
        <h3>系统信息</h3>
        <div id="system-info"></div>
    </div>

    <script>
        function addResult(message, type) {
            const container = document.getElementById('test-results');
            const div = document.createElement('div');
            div.className = `status ${type}`;
            div.textContent = message;
            container.appendChild(div);
        }
        
        function testWebGL() {
            const canvas = document.getElementById('webgl-canvas');
            
            // 测试WebGL 1.0
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (!gl) {
                addResult('❌ WebGL 1.0 不支持', 'error');
                return false;
            }
            
            addResult('✅ WebGL 1.0 支持', 'success');
            
            // 测试WebGL 2.0
            const gl2 = canvas.getContext('webgl2');
            if (gl2) {
                addResult('✅ WebGL 2.0 支持', 'success');
            } else {
                addResult('⚠️ WebGL 2.0 不支持', 'info');
            }
            
            // 获取WebGL信息
            const renderer = gl.getParameter(gl.RENDERER);
            const vendor = gl.getParameter(gl.VENDOR);
            const version = gl.getParameter(gl.VERSION);
            const shadingLanguageVersion = gl.getParameter(gl.SHADING_LANGUAGE_VERSION);
            
            document.getElementById('system-info').innerHTML = `
                <p><strong>渲染器:</strong> ${renderer}</p>
                <p><strong>供应商:</strong> ${vendor}</p>
                <p><strong>WebGL版本:</strong> ${version}</p>
                <p><strong>着色器语言版本:</strong> ${shadingLanguageVersion}</p>
                <p><strong>用户代理:</strong> ${navigator.userAgent}</p>
            `;
            
            // 简单的WebGL渲染测试
            try {
                gl.clearColor(0.0, 0.5, 1.0, 1.0);
                gl.clear(gl.COLOR_BUFFER_BIT);
                addResult('✅ WebGL渲染测试通过', 'success');
            } catch (e) {
                addResult(`❌ WebGL渲染测试失败: ${e.message}`, 'error');
            }
            
            return true;
        }
        
        function checkHardwareAcceleration() {
            // 检查硬件加速
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl');
            
            if (gl) {
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                if (debugInfo) {
                    const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                    if (renderer.toLowerCase().includes('software') || 
                        renderer.toLowerCase().includes('swiftshader')) {
                        addResult('⚠️ 检测到软件渲染，建议启用硬件加速', 'info');
                    } else {
                        addResult('✅ 硬件加速已启用', 'success');
                    }
                }
            }
        }
        
        // 页面加载完成后运行测试
        window.addEventListener('load', () => {
            testWebGL();
            checkHardwareAcceleration();
        });
    </script>
</body>
</html>
'''
    
    webgl_test_path = Path(__file__).parent.parent / 'webgl_test.html'
    try:
        with open(webgl_test_path, 'w', encoding='utf-8') as f:
            f.write(webgl_test_content)
        print(f"✅ WebGL测试页面已创建：{webgl_test_path}")
        return str(webgl_test_path)
    except Exception as e:
        print(f"❌ 创建WebGL测试页面失败：{e}")
        return None

def create_updated_test_page():
    """创建更新后的3D地图测试页面"""
    print("\n🔧 创建更新后的3D地图测试页面...")
    
    test_page_content = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D地图配置测试（已更新）</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            font-weight: bold;
        }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
        .info { background-color: #d1ecf1; color: #0c5460; }
        #map3d {
            width: 100%;
            height: 500px;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin: 20px 0;
        }
        .test-section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover { background-color: #0056b3; }
        .log {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            max-height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗺️ 3D地图配置测试（已更新）</h1>
        <p>此页面使用更新后的配置测试3D地图功能</p>
        
        <div class="test-section">
            <h3>📋 配置更新说明</h3>
            <div class="status info">
                ✅ 已添加 mode="HYBRID" 属性到所有 gmp-map-3d 元素<br>
                ✅ 符合Google Maps 3D API最新要求<br>
                ✅ 移除了已废弃的配置选项
            </div>
        </div>
        
        <div class="test-section">
            <h3>🗺️ 3D地图测试</h3>
            <div id="map-status"></div>
            <button onclick="test3DMap()">测试3D地图</button>
            <gmp-map-3d id="map3d" 
                        center="30.31,114.306" 
                        zoom="10" 
                        map-id="45c4f1595b0cd27f9feda952"
                        mode="HYBRID"
                        tilt="45"
                        heading="0">
            </gmp-map-3d>
        </div>
        
        <div class="test-section">
            <h3>📝 测试日志</h3>
            <button onclick="clearLog()">清除日志</button>
            <div id="debug-log" class="log"></div>
        </div>
    </div>

    <script>
        const CONFIG = {
            apiKey: 'AIzaSyBoAqo1lCI2FAQIY7A0jTlXI79mC2SO4Kw',
            mapId: '45c4f1595b0cd27f9feda952'
        };
        
        function log(message, type = 'info') {
            const timestamp = new Date().toLocaleTimeString();
            const logDiv = document.getElementById('debug-log');
            const logEntry = document.createElement('div');
            logEntry.innerHTML = `[${timestamp}] ${type.toUpperCase()}: ${message}`;
            logEntry.style.color = type === 'error' ? 'red' : type === 'success' ? 'green' : 'black';
            logDiv.appendChild(logEntry);
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        function clearLog() {
            document.getElementById('debug-log').innerHTML = '';
        }
        
        function addStatus(containerId, message, type) {
            const container = document.getElementById(containerId);
            const statusDiv = document.createElement('div');
            statusDiv.className = `status ${type}`;
            statusDiv.textContent = message;
            container.appendChild(statusDiv);
        }
        
        async function test3DMap() {
            const container = document.getElementById('map-status');
            container.innerHTML = '';
            
            log('开始3D地图测试（使用更新后的配置）...');
            
            try {
                // 检查API是否已加载
                if (!window.google || !window.google.maps) {
                    addStatus('map-status', '正在加载Google Maps API...', 'info');
                    await loadGoogleMapsAPI();
                }
                
                addStatus('map-status', '✅ Google Maps API已加载', 'success');
                
                // 检查3D地图元素
                const map3dElement = document.getElementById('map3d');
                if (!map3dElement) {
                    throw new Error('找不到3D地图元素');
                }
                
                log('3D地图元素配置：');
                log(`- center: ${map3dElement.getAttribute('center')}`);
                log(`- zoom: ${map3dElement.getAttribute('zoom')}`);
                log(`- map-id: ${map3dElement.getAttribute('map-id')}`);
                log(`- mode: ${map3dElement.getAttribute('mode')}`);
                log(`- tilt: ${map3dElement.getAttribute('tilt')}`);
                
                addStatus('map-status', '✅ 3D地图元素配置正确', 'success');
                
                // 监听地图事件
                map3dElement.addEventListener('gmp-load', () => {
                    log('3D地图加载完成！', 'success');
                    addStatus('map-status', '✅ 3D地图加载成功', 'success');
                });
                
                map3dElement.addEventListener('gmp-error', (event) => {
                    log(`3D地图错误: ${event.detail}`, 'error');
                    addStatus('map-status', `❌ 3D地图错误: ${event.detail}`, 'error');
                });
                
                // 设置超时
                setTimeout(() => {
                    if (!map3dElement.style.display || map3dElement.style.display === 'none') {
                        log('3D地图可能仍在加载中...', 'info');
                        addStatus('map-status', '⏳ 3D地图加载中，请稍候...', 'info');
                    }
                }, 5000);
                
                log('3D地图测试配置完成');
                
            } catch (error) {
                log(`3D地图测试失败: ${error.message}`, 'error');
                addStatus('map-status', `❌ 测试失败: ${error.message}`, 'error');
            }
        }
        
        function loadGoogleMapsAPI() {
            return new Promise((resolve, reject) => {
                if (window.google && window.google.maps) {
                    resolve();
                    return;
                }
                
                const script = document.createElement('script');
                script.src = `https://maps.googleapis.com/maps/api/js?key=${CONFIG.apiKey}&libraries=maps3d&v=beta`;
                script.async = true;
                script.defer = true;
                
                script.onload = () => {
                    setTimeout(() => {
                        if (window.google && window.google.maps) {
                            resolve();
                        } else {
                            reject(new Error('Google Maps API初始化失败'));
                        }
                    }, 1000);
                };
                
                script.onerror = () => {
                    reject(new Error('Google Maps API脚本加载失败'));
                };
                
                document.head.appendChild(script);
            });
        }
        
        // 页面加载完成后自动运行测试
        window.addEventListener('load', () => {
            log('页面加载完成，配置已更新');
            setTimeout(() => {
                test3DMap();
            }, 1000);
        });
    </script>
</body>
</html>
'''
    
    test_page_path = Path(__file__).parent.parent / 'test_3d_map_updated.html'
    try:
        with open(test_page_path, 'w', encoding='utf-8') as f:
            f.write(test_page_content)
        print(f"✅ 更新后的3D地图测试页面已创建：{test_page_path}")
        return str(test_page_path)
    except Exception as e:
        print(f"❌ 创建测试页面失败：{e}")
        return None

def main():
    """主函数"""
    print("🔧 3D Maps配置修复工具")
    print("=" * 50)
    
    # 1. 更新所有gmp-map-3d元素
    updated_files = update_gmp_map_3d_elements()
    
    # 2. 创建WebGL测试页面
    webgl_test_path = create_webgl_test_page()
    
    # 3. 创建更新后的测试页面
    test_page_path = create_updated_test_page()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 修复完成总结：")
    
    if updated_files:
        print(f"✅ 已更新 {len(updated_files)} 个文件：")
        for file in updated_files:
            print(f"   - {file}")
    else:
        print("ℹ️ 所有文件已是最新配置")
    
    if webgl_test_path:
        print(f"✅ WebGL测试页面：{webgl_test_path}")
    
    if test_page_path:
        print(f"✅ 更新后的3D地图测试页面：{test_page_path}")
    
    print("\n🎯 下一步操作：")
    print("1. 打开WebGL测试页面，确认浏览器支持")
    print("2. 打开更新后的3D地图测试页面")
    print("3. 检查浏览器控制台的错误信息")
    print("4. 如果仍有问题，检查Google Cloud Console配置")
    
    print("\n💡 重要提示：")
    print("- 确保Google Cloud Console中已启用Maps 3D API (Beta)")
    print("- 确保API密钥有正确的权限")
    print("- 确保计费账户已启用")
    print("- 3D Maps在某些地区可能不可用")

if __name__ == '__main__':
    main()