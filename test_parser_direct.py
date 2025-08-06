import pandas as pd
from parser import detect_table_structure, extract_route_info

print("=== 直接测试解析器 ===")

# 读取Excel文件
print("\n1. 读取Excel文件...")
df = pd.read_excel("data/中国十六家货航国际航线.xlsx")
print(f"数据形状: {df.shape}")
print(f"列名: {list(df.columns)}")

# 检测表格结构
print("\n2. 检测表格结构...")
structure = detect_table_structure(df)
print(f"检测结果: {structure}")

# 测试前几行的航线提取
print("\n3. 测试航线提取...")
for i in range(min(3, len(df))):
    print(f"\n--- 第{i+1}行 ---")
    row = df.iloc[i]
    routes = extract_route_info(row, structure)
    print(f"提取到的航线: {routes}")

print("\n=== 测试完成 ===")