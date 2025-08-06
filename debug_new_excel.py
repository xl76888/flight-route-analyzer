import pandas as pd
import sys
sys.path.append('.')
from parser import detect_table_structure, extract_route_info

def debug_new_excel():
    """调试新Excel文件的解析过程"""
    try:
        file_path = "data/中国十六家货航国际航线.xlsx"
        
        # 读取Excel文件
        df = pd.read_excel(file_path)
        print(f"数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        
        # 检测表格结构
        structure = detect_table_structure(df)
        print(f"\n检测到的结构:")
        for key, value in structure.items():
            if value:
                print(f"  {key}: {value}")
        
        # 查看前几行实际数据
        print(f"\n前5行数据:")
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            print(f"\n第{i+1}行:")
            for col in df.columns:
                if pd.notna(row[col]) and str(row[col]).strip():
                    print(f"  {col}: {row[col]}")
        
        # 测试航线提取
        print(f"\n测试航线提取:")
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            routes = extract_route_info(row, structure)
            if routes:
                print(f"第{i+1}行提取到 {len(routes)} 条航线: {routes}")
            elif i < 5:  # 只显示前5行的详细信息
                print(f"第{i+1}行未提取到航线")
                
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_new_excel()