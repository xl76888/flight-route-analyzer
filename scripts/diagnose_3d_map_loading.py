#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D地图加载问题诊断脚本
检查API密钥、计费、WebGL等常见问题
"""

import json
import time
from pathlib import Path

def create_diagnostic_html():
    """
    创建诊断页面，检查3D地图加载问题
    """
    html_content = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D地图加载诊断工具</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .diagnostic-section {
            padding: 30px;
        }
        .check-item {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            position: relative;
        }
        .check-item h3 {
            margin: 0 0 10px 0;
            color: #333;
            display: flex;
            align-items: center;
        }
        .status-icon {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
            display: inline-block;
        }
        .status-checking {
            background: #ffc107;
            animation: pulse 1.5s infinite;
        }
        .status-success {
            background: #28a745;
        }
        .status-error {
            background: #dc3545;
        }
        .status-warning {
            background: #fd7e14;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .details {
            margin-top: 10px;
            padding: 10px;
            background: white;
            border-radius: 4px;
            border-left: 4px solid #007bff;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .error-details {
            border-left-color: #dc3545;
            background: #fff5f5;
        }
        .success-details {
            border-left-color: #28a745;
            background: #f0fff4;
        }
        .warning-details {
            border-left-color: #ffc107;
            background: #fffbf0;
        }
        .map-container {
            height: 400px;
            margin: 20px 0;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
        }
        .console-output {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            max-height: 300px;
            overflow-y: auto;
            margin: 20px 0;
        }
        .console-line {
            margin: 5px 0;
            padding: 2px 0;
        }
        .console-error {
            color: #f48771;
        }
        .console-warning {
            color: #dcdcaa;
        }
        .console-info {
            color: #9cdcfe;
        }
        .btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 5px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #0056b3;
        }
        .btn-success {
            background: #28a745;
        }
        .btn-success:hover {
            background: #1e7e34;
        }
        .btn-danger {
            background: #dc3545;
        }
        .btn-danger:hover {
            background: #c82333;
        }
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #007bff, #0056b3);
            width: 0%;
            transition: width 0.3s ease;
        }
        .summary {
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .summary h3 {
            color: #1976d2;
            margin: 0 0 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 3D地图加载诊断工具</h1>
            <p>自动检测和诊断Google Maps 3D API加载问题</p>
        </div>
        
        <div class="diagnostic-section">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            
            <!-- API密钥检查 -->
            <div class="check-item" id="apiKeyCheck">
                <h3>
                    <span class="status-icon status-checking" id="apiKeyStatus"></span>
                    API密钥检查
                </h3>
                <p>检查Google Maps API密钥是否正确配置...</p>
                <div class="details" id="apiKeyDetails">正在检查...</div>
            </div>
            
            <!-- WebGL支持检查 -->
            <div class="check-item" id="webglCheck">
                <h3>
                    <span class="status-icon status-checking" id="webglStatus"></span>
                    WebGL支持检查
                </h3>
                <p>检查浏览器WebGL支持情况...</p>
                <div class="details" id="webglDetails">正在检查...</div>
            </div>
            
            <!-- 网络连接检查 -->
            <div class="check-item" id="networkCheck">
                <h3>
                    <span class="status-icon status-checking" id="networkStatus"></span>
                    网络连接检查
                </h3>
                <p>检查Google Maps服务连接...</p>
                <div class="details" id="networkDetails">正在检查...</div>
            </div>
            
            <!-- 3D地图加载测试 -->
            <div class="check-item" id="mapLoadCheck">
                <h3>
                    <span class="status-icon status-checking" id="mapLoadStatus"></span>
                    3D地图加载测试
                </h3>
                <p>尝试加载3D地图组件...</p>
                <div class="map-container" id="mapContainer">
                    <gmp-map-3d 
                        id="diagnostic-map3d"
                        center="39.9042,116.4074"
                        zoom="10"
                        tilt="45"
                        heading="0"
                        mode="HYBRID"
                        map-id="45c4f1595b0cd27f9feda952"
                        style="width: 100%; height: 100%;"
                    ></gmp-map-3d>
                </div>
                <div class="details" id="mapLoadDetails">正在加载...</div>
            </div>
            
            <!-- 控制台输出 -->
            <div class="check-item">
                <h3>
                    <span class="status-icon status-checking"></span>
                    控制台日志
                </h3>
                <p>实时显示浏览器控制台信息...</p>
                <div class="console-output" id="consoleOutput">
                    <div class="console-line console-info">[INFO] 诊断工具已启动</div>
                </div>
            </div>
            
            <!-- 诊断结果汇总 -->
            <div class="summary" id="diagnosticSummary" style="display: none;">
                <h3>📊 诊断结果汇总</h3>
                <div id="summaryContent"></div>
                <div style="margin-top: 15px;">
                    <button class="btn btn-success" onclick="retryDiagnostic()">重新诊断</button>
                    <button class="btn" onclick="exportReport()">导出报告</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Google Maps API -->
    <script>
        let diagnosticResults = {
            apiKey: { status: 'checking', details: '' },
            webgl: { status: 'checking', details: '' },
            network: { status: 'checking', details: '' },
            mapLoad: { status: 'checking', details: '' }
        };
        
        let checkProgress = 0;
        let totalChecks = 4;
        
        function updateProgress() {
            checkProgress++;
            const percentage = (checkProgress / totalChecks) * 100;
            document.getElementById('progressFill').style.width = percentage + '%';
            
            if (checkProgress >= totalChecks) {
                showSummary();
            }
        }
        
        function updateStatus(checkId, status, details) {
            const statusElement = document.getElementById(checkId + 'Status');
            const detailsElement = document.getElementById(checkId + 'Details');
            
            statusElement.className = 'status-icon status-' + status;
            detailsElement.textContent = details;
            detailsElement.className = 'details ' + status + '-details';
            
            diagnosticResults[checkId] = { status, details };
            updateProgress();
        }
        
        function addConsoleLog(message, type = 'info') {
            const consoleOutput = document.getElementById('consoleOutput');
            const logLine = document.createElement('div');
            logLine.className = 'console-line console-' + type;
            logLine.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            consoleOutput.appendChild(logLine);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
        
        // 1. 检查WebGL支持
        function checkWebGL() {
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                
                if (gl) {
                    const renderer = gl.getParameter(gl.RENDERER);
                    const vendor = gl.getParameter(gl.VENDOR);
                    const version = gl.getParameter(gl.VERSION);
                    
                    const details = `WebGL支持正常\n渲染器: ${renderer}\n供应商: ${vendor}\n版本: ${version}`;
                    updateStatus('webgl', 'success', details);
                    addConsoleLog('WebGL检查通过', 'info');
                } else {
                    updateStatus('webgl', 'error', 'WebGL不支持，3D地图无法正常工作');
                    addConsoleLog('WebGL检查失败：不支持WebGL', 'error');
                }
            } catch (error) {
                updateStatus('webgl', 'error', 'WebGL检查出错: ' + error.message);
                addConsoleLog('WebGL检查异常: ' + error.message, 'error');
            }
        }
        
        // 2. 检查网络连接
        function checkNetwork() {
            const testUrl = 'https://maps.googleapis.com/maps/api/js?key=test';
            const startTime = Date.now();
            
            fetch(testUrl, { method: 'HEAD', mode: 'no-cors' })
                .then(() => {
                    const loadTime = Date.now() - startTime;
                    updateStatus('network', 'success', `Google Maps服务连接正常 (${loadTime}ms)`);
                    addConsoleLog(`网络连接检查通过，延迟: ${loadTime}ms`, 'info');
                })
                .catch(error => {
                    updateStatus('network', 'warning', '网络连接检查失败，可能影响地图加载: ' + error.message);
                    addConsoleLog('网络连接检查失败: ' + error.message, 'warning');
                });
        }
        
        // 3. 检查API密钥（通过脚本加载状态）
        function checkAPIKey() {
            // 检查API脚本是否正确加载
            const scripts = document.querySelectorAll('script[src*="maps.googleapis.com"]');
            
            if (scripts.length > 0) {
                const scriptSrc = scripts[0].src;
                if (scriptSrc.includes('key=')) {
                    const keyMatch = scriptSrc.match(/key=([^&]+)/);
                    if (keyMatch && keyMatch[1] !== 'YOUR_API_KEY') {
                        updateStatus('apiKey', 'success', 'API密钥已配置: ' + keyMatch[1].substring(0, 10) + '...');
                        addConsoleLog('API密钥检查通过', 'info');
                    } else {
                        updateStatus('apiKey', 'error', 'API密钥未正确配置，仍使用默认值');
                        addConsoleLog('API密钥检查失败：使用默认值', 'error');
                    }
                } else {
                    updateStatus('apiKey', 'error', 'API密钥缺失');
                    addConsoleLog('API密钥检查失败：缺失key参数', 'error');
                }
            } else {
                updateStatus('apiKey', 'error', 'Google Maps API脚本未加载');
                addConsoleLog('API密钥检查失败：脚本未加载', 'error');
            }
        }
        
        // 4. 检查3D地图加载
        function checkMapLoad() {
            const map3d = document.getElementById('diagnostic-map3d');
            const loadStartTime = Date.now();
            let loadTimeout;
            
            // 设置超时
            loadTimeout = setTimeout(() => {
                updateStatus('mapLoad', 'error', '3D地图加载超时 (>15秒)');
                addConsoleLog('3D地图加载超时', 'error');
            }, 15000);
            
            if (map3d) {
                // 监听加载成功事件
                map3d.addEventListener('gmp-load', () => {
                    clearTimeout(loadTimeout);
                    const loadTime = Date.now() - loadStartTime;
                    updateStatus('mapLoad', 'success', `3D地图加载成功 (${loadTime}ms)`);
                    addConsoleLog(`3D地图加载成功，耗时: ${loadTime}ms`, 'info');
                });
                
                // 监听加载错误事件
                map3d.addEventListener('gmp-error', (event) => {
                    clearTimeout(loadTimeout);
                    const errorMsg = event.detail ? JSON.stringify(event.detail) : '未知错误';
                    updateStatus('mapLoad', 'error', '3D地图加载失败: ' + errorMsg);
                    addConsoleLog('3D地图加载失败: ' + errorMsg, 'error');
                });
            } else {
                clearTimeout(loadTimeout);
                updateStatus('mapLoad', 'error', '3D地图元素未找到');
                addConsoleLog('3D地图元素未找到', 'error');
            }
        }
        
        // 显示诊断汇总
        function showSummary() {
            const summaryElement = document.getElementById('diagnosticSummary');
            const summaryContent = document.getElementById('summaryContent');
            
            let successCount = 0;
            let errorCount = 0;
            let warningCount = 0;
            
            let summaryHTML = '<ul>';
            
            for (const [key, result] of Object.entries(diagnosticResults)) {
                const statusText = {
                    'success': '✅ 通过',
                    'error': '❌ 失败',
                    'warning': '⚠️ 警告'
                }[result.status] || '❓ 未知';
                
                summaryHTML += `<li><strong>${key}:</strong> ${statusText}</li>`;
                
                if (result.status === 'success') successCount++;
                else if (result.status === 'error') errorCount++;
                else if (result.status === 'warning') warningCount++;
            }
            
            summaryHTML += '</ul>';
            summaryHTML += `<p><strong>总计:</strong> ${successCount} 项通过, ${warningCount} 项警告, ${errorCount} 项失败</p>`;
            
            if (errorCount === 0 && warningCount === 0) {
                summaryHTML += '<p style="color: #28a745;">🎉 所有检查都通过了！3D地图应该可以正常工作。</p>';
            } else if (errorCount > 0) {
                summaryHTML += '<p style="color: #dc3545;">⚠️ 发现问题，请根据上述检查结果进行修复。</p>';
            } else {
                summaryHTML += '<p style="color: #fd7e14;">⚠️ 存在一些警告，可能影响性能但不影响基本功能。</p>';
            }
            
            summaryContent.innerHTML = summaryHTML;
            summaryElement.style.display = 'block';
            
            addConsoleLog('诊断完成', 'info');
        }
        
        // 重新诊断
        function retryDiagnostic() {
            location.reload();
        }
        
        // 导出报告
        function exportReport() {
            const report = {
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                results: diagnosticResults
            };
            
            const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '3d-map-diagnostic-report.json';
            a.click();
            URL.revokeObjectURL(url);
        }
        
        // 捕获控制台错误
        const originalConsoleError = console.error;
        const originalConsoleWarn = console.warn;
        const originalConsoleLog = console.log;
        
        console.error = function(...args) {
            addConsoleLog('ERROR: ' + args.join(' '), 'error');
            originalConsoleError.apply(console, args);
        };
        
        console.warn = function(...args) {
            addConsoleLog('WARN: ' + args.join(' '), 'warning');
            originalConsoleWarn.apply(console, args);
        };
        
        console.log = function(...args) {
            addConsoleLog('LOG: ' + args.join(' '), 'info');
            originalConsoleLog.apply(console, args);
        };
        
        // 启动诊断
        function startDiagnostic() {
            addConsoleLog('开始诊断...', 'info');
            
            // 延迟执行各项检查
            setTimeout(checkWebGL, 500);
            setTimeout(checkNetwork, 1000);
            setTimeout(checkAPIKey, 1500);
            setTimeout(checkMapLoad, 2000);
        }
        
        // 页面加载完成后启动诊断
        window.addEventListener('load', startDiagnostic);
    </script>
    
    <!-- 加载Google Maps API -->
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBjsINSEeWNGtKjWNVwOqVPb_RdWgZXBJE&libraries=maps3d&v=beta">
    </script>
</body>
</html>
    '''
    
    # 保存诊断页面
    output_path = Path("D:/flight_tool/3d_map_diagnostic.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 3D地图诊断工具已创建: {output_path}")
    return output_path

def create_troubleshooting_guide():
    """
    创建故障排查指南
    """
    guide_content = """
# 🔧 3D地图加载问题故障排查指南

## 常见问题及解决方案

### 1. API密钥相关问题

#### 问题症状
- 地图显示"仅用于开发目的"水印
- 控制台显示"Google Maps JavaScript API 警告：NoApiKeys"
- 控制台显示"Google Maps JavaScript API 错误：MissingKeyMapError"

#### 解决方案
1. **检查API密钥是否存在**
   ```html
   <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=maps3d&v=beta"></script>
   ```

2. **验证API密钥有效性**
   - 登录Google Cloud Console
   - 检查API密钥是否启用
   - 确认API密钥权限设置

3. **检查API限制设置**
   - HTTP referrer限制
   - IP地址限制
   - API限制设置

### 2. 计费账户问题

#### 问题症状
- 地图显示暗色或"负片"效果
- 显示"仅用于开发目的"水印
- API调用被拒绝

#### 解决方案
1. **启用计费账户**
   - 前往Google Cloud Console
   - 在"结算"部分添加付款方式
   - 确保项目关联了有效的计费账户

2. **检查配额和限制**
   - 查看API使用量
   - 检查是否超出免费配额
   - 设置适当的使用限制

### 3. WebGL支持问题

#### 问题症状
- 3D地图无法渲染
- 地图显示空白或错误
- 控制台显示WebGL相关错误

#### 解决方案
1. **检查WebGL支持**
   - 访问 https://get.webgl.org/
   - 确认浏览器支持WebGL

2. **启用硬件加速**
   - Chrome: chrome://settings/ → 高级 → 系统 → 使用硬件加速
   - Edge: edge://settings/ → 系统 → 使用硬件加速

3. **更新显卡驱动**
   - 下载最新显卡驱动
   - 重启浏览器

### 4. 网络连接问题

#### 问题症状
- 地图加载超时
- 网络请求失败
- 3D瓦片无法下载

#### 解决方案
1. **检查网络连接**
   - 确保网络连接稳定
   - 检查防火墙设置
   - 测试DNS解析

2. **代理和VPN设置**
   - 检查代理配置
   - 尝试禁用VPN
   - 使用直连网络

### 5. 浏览器兼容性问题

#### 问题症状
- 特定浏览器无法加载
- 功能在某些浏览器中异常
- 性能差异明显

#### 解决方案
1. **更新浏览器**
   - 使用最新版本浏览器
   - 启用实验性功能

2. **清除缓存**
   - 清除浏览器缓存
   - 清除Cookie和本地存储

3. **禁用扩展**
   - 禁用广告拦截器
   - 禁用其他可能冲突的扩展

## 诊断步骤

### 第一步：基础检查
1. 打开浏览器开发者工具 (F12)
2. 查看Console标签页的错误信息
3. 查看Network标签页的网络请求
4. 检查Elements标签页的DOM结构

### 第二步：API配置验证
1. 确认API密钥正确配置
2. 检查Google Cloud Console设置
3. 验证计费账户状态
4. 测试API权限

### 第三步：技术环境检查
1. 测试WebGL支持
2. 检查硬件加速状态
3. 验证网络连接
4. 测试浏览器兼容性

### 第四步：代码调试
1. 添加错误处理代码
2. 实现加载状态监控
3. 记录详细日志信息
4. 测试降级方案

## 预防措施

### 1. 监控和告警
- 设置API使用量监控
- 配置错误率告警
- 实现性能监控

### 2. 错误处理
- 实现优雅降级
- 提供用户友好的错误信息
- 添加重试机制

### 3. 测试策略
- 多浏览器测试
- 不同网络环境测试
- 性能压力测试

## 联系支持

如果问题仍然存在，可以：
1. 查看Google Maps Platform文档
2. 访问Google Maps Platform支持页面
3. 在Stack Overflow提问
4. 联系Google技术支持

---

**更新时间**: 2024年12月
**适用版本**: Google Maps JavaScript API v3.x
**状态**: ✅ 已验证有效
"""
    
    # 保存故障排查指南
    guide_path = Path("D:/flight_tool/3D_MAP_TROUBLESHOOTING_GUIDE.md")
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"📋 故障排查指南已创建: {guide_path}")
    return guide_path

def main():
    """
    主函数
    """
    print("🔍 3D地图加载问题诊断工具")
    print("=" * 40)
    
    # 创建诊断页面
    diagnostic_path = create_diagnostic_html()
    
    # 创建故障排查指南
    guide_path = create_troubleshooting_guide()
    
    print("\n📊 诊断工具功能:")
    print("1. 自动检测API密钥配置")
    print("2. 验证WebGL支持状态")
    print("3. 测试网络连接质量")
    print("4. 监控3D地图加载过程")
    print("5. 实时显示控制台日志")
    print("6. 生成详细诊断报告")
    
    print("\n🛠️ 使用方法:")
    print(f"1. 在浏览器中打开: {diagnostic_path}")
    print("2. 等待自动诊断完成")
    print("3. 查看诊断结果和建议")
    print(f"4. 参考故障排查指南: {guide_path}")
    
    print("\n⚠️ 注意事项:")
    print("1. 确保网络连接正常")
    print("2. 使用最新版本浏览器")
    print("3. 启用浏览器硬件加速")
    print("4. 检查API密钥和计费设置")
    
    print(f"\n✅ 诊断工具已准备就绪！")
    print(f"请在浏览器中打开: {diagnostic_path}")

if __name__ == "__main__":
    main()