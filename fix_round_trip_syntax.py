#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复往返航线视图语法错误
"""

import re

def fix_round_trip_syntax():
    """修复web_app.py中往返航线视图的语法错误"""
    
    # 读取文件内容
    with open('web_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并修复语法错误
    # 问题：else语句缩进错误，应该与if语句对齐
    pattern = r'(\s+)# 在往返航线视图模式下，使用不同的双向航线检测逻辑\n(\s+)if view_mode == "往返航线视图" and \'round_trip_pairs\' in locals\(\):\n([\s\S]*?)\n(\s+)else:\n(\s+)# 标准视图模式下的双向航线检测\n(\s+)is_bidirectional = reverse_route_key in route_stats'
    
    def replacement(match):
        indent1 = match.group(1)  # 注释的缩进
        indent2 = match.group(2)  # if语句的缩进
        if_content = match.group(3)  # if语句内容
        else_indent = match.group(4)  # else语句的缩进（错误的）
        comment_indent = match.group(5)  # 注释的缩进
        code_indent = match.group(6)  # 代码的缩进
        
        # 修复：else语句应该与if语句对齐
        fixed = f"{indent1}# 在往返航线视图模式下，使用不同的双向航线检测逻辑\n{indent2}if view_mode == \"往返航线视图\" and 'round_trip_pairs' in locals():{if_content}\n{indent2}else:\n{indent2}    # 标准视图模式下的双向航线检测\n{indent2}    is_bidirectional = reverse_route_key in route_stats"
        
        return fixed
    
    # 应用修复
    fixed_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # 如果没有找到模式，尝试手动查找和修复
    if fixed_content == content:
        print("未找到预期的模式，尝试手动修复...")
        
        # 查找问题行
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'else:' in line and '# 标准视图模式下的双向航线检测' in lines[i+1] if i+1 < len(lines) else False:
                # 找到问题的else语句
                # 向上查找对应的if语句
                for j in range(i-1, -1, -1):
                    if 'if view_mode == "往返航线视图"' in lines[j]:
                        if_indent = len(lines[j]) - len(lines[j].lstrip())
                        else_indent = len(lines[i]) - len(lines[i].lstrip())
                        
                        if else_indent != if_indent:
                            print(f"修复第{i+1}行的缩进错误")
                            # 修复缩进
                            lines[i] = ' ' * if_indent + 'else:'
                            lines[i+1] = ' ' * (if_indent + 4) + lines[i+1].lstrip()
                            lines[i+2] = ' ' * (if_indent + 4) + lines[i+2].lstrip()
                            fixed_content = '\n'.join(lines)
                        break
                break
    
    # 写入修复后的文件
    if fixed_content != content:
        with open('web_app.py', 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print("✅ 语法错误已修复")
        return True
    else:
        print("❌ 未发现需要修复的语法错误")
        return False

if __name__ == "__main__":
    print("🔧 开始修复往返航线视图语法错误...")
    success = fix_round_trip_syntax()
    
    if success:
        print("\n✅ 修复完成！现在可以重新启动Streamlit应用。")
    else:
        print("\n⚠️ 未发现明显的语法错误，可能需要手动检查。")