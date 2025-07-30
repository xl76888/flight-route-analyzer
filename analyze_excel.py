import pandas as pd
import numpy as np

def analyze_excel_data():
    """详细分析Excel文件内容"""
    file_path = "D:\\flight_tool\\data\\大陆航司全货机航线.xlsx"
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        print(f"=== Excel文件基本信息 ===")
        print(f"数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        print(f"\n=== 前10行数据 ===")
        print(df.head(10))
        
        print(f"\n=== 数据类型 ===")
        print(df.dtypes)
        
        print(f"\n=== 缺失值统计 ===")
        print(df.isnull().sum())
        
        # 检查航司列的唯一值
        if '航司' in df.columns:
            print(f"\n=== 航司统计 ===")
            airline_counts = df['航司'].value_counts(dropna=False)
            print(f"总航司数: {len(airline_counts)}")
            print(airline_counts)
        
        # 检查出口航线和进口航线的内容
        if '出口航线' in df.columns:
            print(f"\n=== 出口航线内容分析 ===")
            export_routes = df['出口航线'].dropna()
            print(f"非空出口航线数: {len(export_routes)}")
            print("出口航线样例:")
            for i, route in enumerate(export_routes.head(10)):
                print(f"  {i+1}: {route}")
        
        if '进口航线' in df.columns:
            print(f"\n=== 进口航线内容分析 ===")
            import_routes = df['进口航线'].dropna()
            print(f"非空进口航线数: {len(import_routes)}")
            print("进口航线样例:")
            for i, route in enumerate(import_routes.head(10)):
                print(f"  {i+1}: {route}")
        
        # 检查每个航司的航线情况
        print(f"\n=== 每个航司的航线情况 ===")
        for idx, row in df.iterrows():
            airline = row.get('航司', '')
            export_route = row.get('出口航线', '')
            import_route = row.get('进口航线', '')
            
            if pd.notna(airline):
                export_status = "有数据" if pd.notna(export_route) and str(export_route).strip() else "无数据"
                import_status = "有数据" if pd.notna(import_route) and str(import_route).strip() else "无数据"
                print(f"  {airline}: 出口航线-{export_status}, 进口航线-{import_status}")
                
                # 显示具体内容
                if pd.notna(export_route) and str(export_route).strip():
                    print(f"    出口: {export_route}")
                if pd.notna(import_route) and str(import_route).strip():
                    print(f"    进口: {import_route}")
                print()
        
    except Exception as e:
        print(f"分析Excel文件时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_excel_data()