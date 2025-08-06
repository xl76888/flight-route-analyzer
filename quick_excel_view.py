import pandas as pd

# 读取Excel文件
df = pd.read_excel("data/中国十六家货航国际航线.xlsx")

print("=== 基本信息 ===")
print(f"数据形状: {df.shape}")
print(f"列数: {len(df.columns)}")

print("\n=== 列名 ===")
for i, col in enumerate(df.columns):
    print(f"{i+1:2d}. {col}")

print("\n=== 第1行数据 ===")
row1 = df.iloc[0]
for col in df.columns:
    if pd.notna(row1[col]):
        print(f"{col}: {row1[col]}")

print("\n=== 第2行数据 ===")
row2 = df.iloc[1]
for col in df.columns:
    if pd.notna(row2[col]):
        print(f"{col}: {row2[col]}")

print("\n=== 航线相关列的样本数据 ===")
route_cols = [col for col in df.columns if '航线' in str(col)]
for col in route_cols:
    print(f"\n{col}:")
    sample_data = df[col].dropna().head(3)
    for i, val in enumerate(sample_data):
        print(f"  {i+1}. {val}")