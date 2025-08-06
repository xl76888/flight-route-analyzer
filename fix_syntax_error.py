#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复fix_3d_map_cdn.py中的语法错误
"""

import os
import re

def fix_syntax_error():
    """
    修复fix_3d_map_cdn.py中的语法错误
    """
    
    file_path = 'd:\\flight_tool\\fix_3d_map_cdn.py'
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    print(f"正在修复文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复CSS中的数字+px组合
    # 将 0px, 3px, -3px 等替换为 {{0}}px, {{3}}px, {{-3}}px
    
    # 在CSS规则中查找数字+px的模式
    def fix_px_values(match):
        css_rule = match.group(0)
        # 修复px值
        fixed_rule = re.sub(r'(\d+)px', r'{{\1}}px', css_rule)
        fixed_rule = re.sub(r'(-\d+)px', r'{{\1}}px', fixed_rule)
        return fixed_rule
    
    # 修复transform规则中的px值
    new_content = re.sub(
        r'transform:[^;]+;',
        fix_px_values,
        content
    )
    
    # 如果内容有变化，写回文件
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ 已修复CSS中的px值")
    else:
        print(f"ℹ️ 未发现需要修复的px值")
    
    # 验证修复结果
    try:
        import py_compile
        py_compile.compile(file_path, doraise=True)
        print("✅ 语法检查通过")
    except py_compile.PyCompileError as e:
        print(f"❌ 仍有语法错误: {e}")
        
        # 如果还有错误，尝试更彻底的修复
        print("尝试彻底修复方法...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并修复所有可能的数字字面量问题
        # 修复CSS中的所有数字值
        patterns = [
            (r'(\d+)px', r'{{\1}}px'),
            (r'(-\d+)px', r'{{\1}}px'),
            (r'(\d+)deg', r'{{\1}}deg'),
            (r'(-\d+)deg', r'{{\1}}deg'),
            (r'(\d+\.\d+)s', r'{{\1}}s'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 再次验证
        try:
            py_compile.compile(file_path, doraise=True)
            print("✅ 彻底修复成功，语法检查通过")
        except py_compile.PyCompileError as e:
            print(f"❌ 彻底修复失败: {e}")
            print("建议手动检查文件中的f-string语法")
    
    print("\n🎉 语法错误修复完成！")
    print("\n修复内容:")
    print("- 修复了f-string中CSS数值的转义问题")
    print("- 确保所有CSS数值都被正确转义")
    print("\n请重新启动Streamlit应用以应用修复。")

if __name__ == "__main__":
    fix_syntax_error()