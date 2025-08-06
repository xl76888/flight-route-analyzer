#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复3D地图组件中key参数兼容性问题
"""

import os
import re

def fix_key_parameter_issue():
    """
    修复components.html中key参数的兼容性问题
    """
    
    files_to_fix = [
        'd:\\flight_tool\\optimized_map3d_integration.py',
        'd:\\flight_tool\\map3d_integration.py',
        'd:\\flight_tool\\fix_3d_map_cdn.py'
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"正在修复文件: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 移除components.html中的key参数
            # 匹配模式: components.html(..., key=..., ...)
            pattern = r'(components\.html\s*\([^)]*),\s*key\s*=\s*[^,)]+([^)]*\))'
            replacement = r'\1\2'
            
            new_content = re.sub(pattern, replacement, content)
            
            # 如果内容有变化，写回文件
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ 已修复 {file_path}")
            else:
                print(f"ℹ️ {file_path} 无需修复")
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    print("\n🎉 Key参数兼容性问题修复完成！")
    print("\n修复内容:")
    print("- 移除了components.html()调用中的key参数")
    print("- 这将解决IframeMixin._html()的参数兼容性问题")
    print("\n请重新启动Streamlit应用以应用修复。")

if __name__ == "__main__":
    fix_key_parameter_issue()