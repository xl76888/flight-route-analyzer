import pandas as pd

try:
    # 直接读取Excel文件
    df = pd.read_excel("data/中国十六家货航国际航线.xlsx")
    print(f"数据形状: {df.shape}")
    print(f"列名: {list(df.columns)[:10]}...")  # 只显示前10列
    print("\n第1行数据:")
    print(df.iloc[0].dropna())
    print("\n第2行数据:")
    print(df.iloc[1].dropna())
except Exception as e:
    print(f"错误: {e}")