import pandas as pd
import sys

def analyze_airlines():
    """分析Excel文件中的航司数据"""
    try:
        # 读取Excel文件
        df = pd.read_excel('data/大陆航司全货机航线.xlsx')
        
        print("=== 原始数据分析 ===")
        print(f"总记录数: {len(df)}")
        print(f"列名: {list(df.columns)}")
        
        # 查找航司列
        airline_col = None
        for col in df.columns:
            if '航司' in str(col) or 'airline' in str(col).lower() or '公司' in str(col):
                airline_col = col
                break
        
        if airline_col:
            print(f"\n航司列名: {airline_col}")
            
            # 获取所有航司
            all_airlines = df[airline_col].dropna().unique()
            print(f"\n=== 所有航司列表 ({len(all_airlines)}家) ===")
            for i, airline in enumerate(sorted(all_airlines), 1):
                print(f"{i:2d}. {airline}")
            
            # 统计每个航司的航线数量
            airline_counts = df[airline_col].value_counts()
            print(f"\n=== 航司航线数量统计 ===")
            for airline, count in airline_counts.items():
                print(f"{airline}: {count}条航线")
                
        else:
            print("\n未找到航司列！")
            print("可用列名:")
            for col in df.columns:
                print(f"  - {col}")
        
        # 显示前几行数据
        print(f"\n=== 前5行数据 ===")
        print(df.head())
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_airlines()