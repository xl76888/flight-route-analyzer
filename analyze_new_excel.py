import pandas as pd
import sys

def analyze_excel_structure():
    """分析新Excel文件的结构"""
    try:
        file_path = "data/中国十六家货航国际航线.xlsx"
        
        # 读取Excel文件的所有工作表
        excel_file = pd.ExcelFile(file_path)
        print(f"工作表列表: {excel_file.sheet_names}")
        
        # 分析每个工作表
        for sheet_name in excel_file.sheet_names:
            print(f"\n=== 工作表: {sheet_name} ===")
            
            # 读取前几行数据
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
            print(f"形状: {df.shape}")
            print(f"列名: {list(df.columns)}")
            print("\n前5行数据:")
            print(df.head())
            
            # 检查是否有合并单元格或空行
            df_full = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"\n完整数据形状: {df_full.shape}")
            print(f"非空行数: {df_full.dropna(how='all').shape[0]}")
            
            # 查找可能的数据起始行
            for i in range(min(20, len(df_full))):
                row = df_full.iloc[i]
                if not row.isna().all():
                    print(f"第{i+1}行有数据: {row.dropna().to_dict()}")
                    if i >= 5:  # 只显示前几行
                        break
    
    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_excel_structure()