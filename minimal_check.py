import pandas as pd

print("=== 最简单的Excel检查 ===")
df = pd.read_excel("data/中国十六家货航国际航线.xlsx")
print(f"行数: {len(df)}")
print(f"列数: {len(df.columns)}")
print("\n前3列名:")
for i, col in enumerate(df.columns[:3]):
    print(f"{i+1}. {col}")

print("\n第1行前3列数据:")
for i, col in enumerate(df.columns[:3]):
    print(f"{col}: {df.iloc[0, i]}")