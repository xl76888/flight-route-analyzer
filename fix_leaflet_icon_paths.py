#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 Leaflet 图标路径错误
解决控制台报错：net::ERR_BLOCKED_BY_ORB https://cdn.jsdelivr.net/npm/leaflet@1.9.3/distmarker-icon.png
"""

import os
import re
from pathlib import Path

def fix_leaflet_icon_paths():
    """修复 Leaflet 图标路径问题"""
    print("🔧 开始修复 Leaflet 图标路径问题...")
    
    # 1. 检查并修复 HTML 模板文件
    html_files = [
        "d:/flight_tool/components/map3d/optimized_map3d_component.html",
        "d:/flight_tool/components/map3d/map3d_component.html"
    ]
    
    for html_file in html_files:
        if os.path.exists(html_file):
            fix_html_file(html_file)
    
    # 2. 创建图标路径修复脚本
    create_icon_fix_script()
    
    print("✅ Leaflet 图标路径修复完成！")

def fix_html_file(file_path):
    """修复 HTML 文件中的 Leaflet 配置"""
    print(f"📝 修复文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经有图标路径设置
        if 'L.Icon.Default.imagePath' in content:
            print(f"   ✓ {file_path} 已包含图标路径设置")
            return
        
        # 在 Leaflet CSS 加载后添加图标路径设置
        leaflet_css_pattern = r'(<link[^>]*leaflet[^>]*\.css[^>]*>)'
        
        if re.search(leaflet_css_pattern, content):
            # 在 Leaflet CSS 后添加图标路径设置
            icon_fix_script = '''
<script>
// 修复 Leaflet 图标路径
if (typeof L !== 'undefined' && L.Icon && L.Icon.Default) {
    L.Icon.Default.imagePath = './static/leaflet/images/';
    
    // 明确设置图标 URL
    L.Icon.Default.prototype.options.iconUrl = './static/leaflet/images/marker-icon.png';
    L.Icon.Default.prototype.options.iconRetinaUrl = './static/leaflet/images/marker-icon-2x.png';
    L.Icon.Default.prototype.options.shadowUrl = './static/leaflet/images/marker-shadow.png';
    
    console.log('✅ Leaflet 图标路径已修复');
}
</script>'''
            
            # 在 </head> 标签前插入脚本
            content = content.replace('</head>', f'{icon_fix_script}\n</head>')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ 已添加图标路径修复脚本到 {file_path}")
        else:
            print(f"   ⚠️ 未找到 Leaflet CSS 引用在 {file_path}")
    
    except Exception as e:
        print(f"   ❌ 修复 {file_path} 时出错: {e}")

def create_icon_fix_script():
    """创建独立的图标修复脚本"""
    script_content = '''
// Leaflet 图标路径修复脚本
(function() {
    // 等待 Leaflet 加载完成
    function fixLeafletIcons() {
        if (typeof L !== 'undefined' && L.Icon && L.Icon.Default) {
            // 设置图标基础路径
            L.Icon.Default.imagePath = './static/leaflet/images/';
            
            // 明确设置每个图标的 URL
            L.Icon.Default.prototype.options.iconUrl = './static/leaflet/images/marker-icon.png';
            L.Icon.Default.prototype.options.iconRetinaUrl = './static/leaflet/images/marker-icon-2x.png';
            L.Icon.Default.prototype.options.shadowUrl = './static/leaflet/images/marker-shadow.png';
            
            console.log('✅ Leaflet 图标路径已修复');
            return true;
        }
        return false;
    }
    
    // 立即尝试修复
    if (!fixLeafletIcons()) {
        // 如果 Leaflet 还未加载，等待 DOM 加载完成后再试
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fixLeafletIcons);
        } else {
            // 延迟执行
            setTimeout(fixLeafletIcons, 100);
        }
    }
})();
'''
    
    script_path = "d:/flight_tool/static/leaflet/fix-icons.js"
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"📝 创建图标修复脚本: {script_path}")

if __name__ == "__main__":
    fix_leaflet_icon_paths()