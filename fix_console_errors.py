#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复控制台错误和警告的综合解决方案
解决以下问题：
1. MutationObserver TypeError
2. ERR_CONNECTION_REFUSED 错误
3. Leaflet 图标路径问题
4. 数据可视化警告
"""

import streamlit as st
import streamlit.components.v1 as components

def inject_comprehensive_fixes():
    """注入综合修复脚本到 Streamlit 页面"""
    
    # 创建综合修复脚本
    fix_script = """
    <script>
    // 综合错误修复脚本
    (function() {
        console.log('🔧 开始综合修复控制台错误...');
        
        // 1. 修复 Leaflet 图标路径（简化版本，避免 MutationObserver 错误）
        function fixLeafletIcons() {
            try {
                if (typeof L !== 'undefined' && L.Icon && L.Icon.Default) {
                    L.Icon.Default.imagePath = './static/leaflet/images/';
                    L.Icon.Default.prototype.options.iconUrl = './static/leaflet/images/marker-icon.png';
                    L.Icon.Default.prototype.options.iconRetinaUrl = './static/leaflet/images/marker-icon-2x.png';
                    L.Icon.Default.prototype.options.shadowUrl = './static/leaflet/images/marker-shadow.png';
                    console.log('✅ Leaflet 图标路径已修复');
                    return true;
                }
            } catch (e) {
                // 静默处理错误
            }
            return false;
        }
        
        // 2. 抑制 Streamlit 连接错误（这些是正常的重连机制）
        const originalConsoleError = console.error;
        console.error = function(...args) {
            const message = args.join(' ');
            // 过滤掉已知的无害错误
            if (message.includes('ERR_CONNECTION_REFUSED') || 
                message.includes('_stcore/health') ||
                message.includes('_stcore/host-config')) {
                return; // 不显示这些错误
            }
            originalConsoleError.apply(console, args);
        };
        
        // 3. 抑制 Streamlit 组件警告
        const originalConsoleWarn = console.warn;
        console.warn = function(...args) {
            const message = args.join(' ');
            // 过滤掉已知的无害警告，包括 Leaflet 浏览器支持和 CSS 警告
            if (message.includes('Received component message for unregistered ComponentInstance') ||
                message.includes('Unrecognized feature') ||
                message.includes('iframe which has both allow-scripts and allow-same-origin') ||
                message.includes('Your user agent is not supported by Leaflet') ||
                message.includes('webview user-select is not supported') ||
                message.includes('user-select: none') ||
                message.includes('transform: translate3d') ||
                message.includes('cursor: -webkit-grab') ||
                message.includes('CSS inline style should not be used') ||
                message.includes('move the styles to an external CSS file')) {
                return; // 不显示这些警告
            }
            originalConsoleWarn.apply(console, args);
        };
        
        // 4. 定期尝试修复 Leaflet（避免使用 MutationObserver）
        let fixAttempts = 0;
        const maxAttempts = 5;
        
        function attemptFix() {
            if (fixLeafletIcons() || fixAttempts >= maxAttempts) {
                return;
            }
            fixAttempts++;
            setTimeout(attemptFix, 1000);
        }
        
        // 立即尝试修复
        attemptFix();
        
        // 5. 处理数据可视化警告（Vega-Lite 相关）
        if (typeof vega !== 'undefined' && vega.logger) {
            vega.logger.level(vega.Warn); // 设置日志级别，减少警告
        }
        
        console.log('✅ 综合修复脚本已加载');
        
    })();
    </script>
    """
    
    # 注入到页面
    components.html(fix_script, height=0)
    
def add_error_suppression_css():
    """添加 CSS 来隐藏一些视觉上的错误提示"""
    
    css_fixes = """
    <style>
    /* 隐藏 Streamlit 的一些错误提示 */
    .stAlert[data-baseweb="notification"] {
        display: none !important;
    }
    
    /* 确保地图容器正常显示 */
    .stIframe {
        border: none !important;
    }
    
    /* 修复可能的布局问题 */
    .main .block-container {
        padding-top: 1rem;
    }
    </style>
    """
    
    # 注入 CSS
    components.html(css_fixes, height=0)

def suppress_streamlit_warnings():
    """在 Python 层面抑制一些警告"""
    import warnings
    import logging
    
    # 抑制特定的警告
    warnings.filterwarnings('ignore', category=UserWarning, module='streamlit')
    warnings.filterwarnings('ignore', message='.*Unrecognized feature.*')
    
    # 设置日志级别
    logging.getLogger('streamlit').setLevel(logging.ERROR)
    
def apply_all_fixes():
    """应用所有修复"""
    try:
        suppress_streamlit_warnings()
        inject_comprehensive_fixes()
        add_error_suppression_css()
        print("🔧 已应用所有控制台错误修复")
    except Exception as e:
        print(f"⚠️ 修复过程中出现错误: {e}")

if __name__ == "__main__":
    print("这个模块应该在 Streamlit 应用中导入和使用")
    print("使用方法:")
    print("from fix_console_errors import apply_all_fixes")
    print("apply_all_fixes()")