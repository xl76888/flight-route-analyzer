import pandas as pd
import sys

def analyze_field_differences():
    """分析Excel文件字段与系统现有字段的差异"""
    
    print("=== 航线明细表字段差异分析 ===")
    
    # 1. 系统现有字段（从web_app.py中提取）
    current_system_fields = {
        'airline': '✈️ 航空公司',
        'aircraft': '🛩️ 机型', 
        'simplified_age': '📅 机龄',
        'full_route': '🛣️ 完整航线',
        'origin': '🛫 始发地',
        'destination': '🛬 目的地',
        'direction': '📍 方向',
        '进出口类型': '🔄 进出口类型',
        '航线类型': '🌍 航线类型',
        '中转地分析': '🔀 中转地',
        '每周往返班次': '📊 每周往返班次',
        'flight_time': '⏱️ 飞行时长',
        'flight_distance': '📏 飞行距离'
    }
    
    print("\n1. 系统当前显示字段:")
    for i, (field, display_name) in enumerate(current_system_fields.items(), 1):
        print(f"  {i:2d}. {field} -> {display_name}")
    
    # 2. 读取Excel文件字段
    try:
        excel_file = 'd:/flight_tool/data/中国十六家货航国际航线.xlsx'
        df = pd.read_excel(excel_file)
        excel_fields = list(df.columns)
        
        print(f"\n2. Excel文件字段 (共{len(excel_fields)}个):")
        for i, field in enumerate(excel_fields, 1):
            print(f"  {i:2d}. {field}")
        
        # 3. 分析字段差异
        print("\n=== 字段差异分析 ===")
        
        # Excel中有但系统中没有的字段
        excel_only_fields = []
        for field in excel_fields:
            # 跳过非字符串字段
            if not isinstance(field, str):
                continue
                
            # 检查是否在系统字段中（考虑可能的映射关系）
            field_lower = field.lower()
            found_in_system = False
            
            for sys_field in current_system_fields.keys():
                if not isinstance(sys_field, str):
                    continue
                    
                if (field == sys_field or 
                    field_lower in sys_field.lower() or 
                    sys_field.lower() in field_lower or
                    # 特殊映射检查
                    (field == '航司' and sys_field == 'airline') or
                    (field == '机型' and sys_field == 'aircraft') or
                    ('航线' in field and 'route' in sys_field) or
                    ('时长' in field and 'time' in sys_field) or
                    ('距离' in field and 'distance' in sys_field)):
                    found_in_system = True
                    break
            
            if not found_in_system:
                excel_only_fields.append(field)
        
        print(f"\n3. Excel中有但系统中缺少的字段 (共{len(excel_only_fields)}个):")
        if excel_only_fields:
            for i, field in enumerate(excel_only_fields, 1):
                print(f"  {i:2d}. {field}")
        else:
            print("  无")
        
        # 4. 系统中有但Excel中没有的字段
        system_only_fields = []
        for sys_field, display_name in current_system_fields.items():
            if not isinstance(sys_field, str):
                continue
                
            found_in_excel = False
            for excel_field in excel_fields:
                if not isinstance(excel_field, str):
                    continue
                    
                if (sys_field == excel_field or
                    sys_field.lower() in excel_field.lower() or
                    excel_field.lower() in sys_field.lower() or
                    # 特殊映射检查
                    (sys_field == 'airline' and excel_field == '航司') or
                    (sys_field == 'aircraft' and excel_field == '机型') or
                    ('route' in sys_field and '航线' in excel_field) or
                    ('time' in sys_field and '时长' in excel_field) or
                    ('distance' in sys_field and '距离' in excel_field)):
                    found_in_excel = True
                    break
            
            if not found_in_excel:
                system_only_fields.append((sys_field, display_name))
        
        print(f"\n4. 系统中有但Excel中没有的字段 (共{len(system_only_fields)}个):")
        if system_only_fields:
            for i, (field, display_name) in enumerate(system_only_fields, 1):
                print(f"  {i:2d}. {field} -> {display_name}")
        else:
            print("  无")
        
        # 5. 建议新增的字段
        print("\n=== 建议新增字段分析 ===")
        
        # 分析Excel中的有价值字段
        valuable_fields = []
        for field in excel_only_fields:
            if not isinstance(field, str):
                continue
                
            field_lower = field.lower()
            # 判断字段是否有价值
            if any(keyword in field_lower for keyword in [
                '频次', '班次', '周', '月', '年',  # 频率相关
                '载重', '容量', '重量', '吨',      # 载重相关
                '价格', '费用', '成本', '收入',    # 经济相关
                '时间', '日期', '期间',           # 时间相关
                '备注', '说明', '状态',           # 状态相关
                '代码', '编号', 'code',          # 编码相关
                '坐标', '经度', '纬度',           # 地理相关
                '速度', '注册号', '机龄'          # 新增的有价值字段
            ]):
                valuable_fields.append(field)
        
        print(f"\n5. 建议优先新增的字段 (共{len(valuable_fields)}个):")
        if valuable_fields:
            for i, field in enumerate(valuable_fields, 1):
                print(f"  {i:2d}. {field}")
                # 显示该字段的样例数据
                sample_data = df[field].dropna().head(3).tolist()
                if sample_data:
                    print(f"      样例: {sample_data}")
        else:
            print("  无明显有价值的新字段")
        
        # 6. 字段映射建议
        print("\n6. 字段映射建议:")
        mapping_suggestions = []
        
        for excel_field in excel_fields:
            if not isinstance(excel_field, str):
                continue
                
            for sys_field, display_name in current_system_fields.items():
                if not isinstance(sys_field, str):
                    continue
                    
                # 检查可能的映射关系
                if (excel_field.lower() == sys_field.lower() or
                    ('航司' in excel_field and sys_field == 'airline') or
                    ('机型' in excel_field and sys_field == 'aircraft') or
                    ('航线' in excel_field and 'route' in sys_field) or
                    ('时长' in excel_field and 'time' in sys_field) or
                    ('距离' in excel_field and 'distance' in sys_field)):
                    mapping_suggestions.append((excel_field, sys_field, display_name))
                    break
        
        if mapping_suggestions:
            for i, (excel_field, sys_field, display_name) in enumerate(mapping_suggestions, 1):
                print(f"  {i:2d}. Excel[{excel_field}] -> 系统[{sys_field}] -> 显示[{display_name}]")
        
        # 7. 总结和建议
        print("\n=== 总结和建议 ===")
        print(f"1. Excel文件共有 {len(excel_fields)} 个字段")
        print(f"2. 系统当前显示 {len(current_system_fields)} 个字段")
        print(f"3. Excel独有字段 {len(excel_only_fields)} 个")
        print(f"4. 系统独有字段 {len(system_only_fields)} 个")
        print(f"5. 建议新增字段 {len(valuable_fields)} 个")
        
        print("\n建议操作:")
        if valuable_fields:
            print("1. 优先考虑新增以下字段到系统明细表:")
            for field in valuable_fields[:5]:  # 只显示前5个
                print(f"   - {field}")
        
        print("2. 检查现有字段映射是否正确")
        print("3. 考虑是否需要隐藏或合并某些字段以优化显示")
        
        return {
            'excel_fields': excel_fields,
            'system_fields': list(current_system_fields.keys()),
            'excel_only': excel_only_fields,
            'system_only': [f[0] for f in system_only_fields],
            'valuable_new_fields': valuable_fields,
            'mapping_suggestions': mapping_suggestions
        }
        
    except Exception as e:
        print(f"\n错误: 无法读取Excel文件 - {e}")
        return None

if __name__ == "__main__":
    result = analyze_field_differences()
    if result:
        print("\n分析完成！")
    else:
        print("\n分析失败！")