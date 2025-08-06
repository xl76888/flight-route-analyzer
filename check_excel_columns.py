import pandas as pd

# 读取Excel文件
df = pd.read_excel('data/中国十六家货航国际航线.xlsx')

print('所有列名:')
for i, col in enumerate(df.columns):
    print(f'{i}: {repr(col)}')

# 查看国货航数据
guohuo_data = df[df['航司'].str.contains('国货航', na=False)]
print(f'\n国货航数据行数: {len(guohuo_data)}')

# 查看前几行数据的出口和进口航线
if len(guohuo_data) > 0:
    print('\n国货航前5行数据:')
    # 找到包含"出口航线"和"进口航线"的列
    export_cols = [col for col in df.columns if '出口航线' in col]
    import_cols = [col for col in df.columns if '进口航线' in col]
    
    print('\n出口航线相关列:', export_cols)
    print('进口航线相关列:', import_cols)
    
    if export_cols:
        print('\n出口航线样本:')
        print(guohuo_data[export_cols].head().to_string())
    
    if import_cols:
        print('\n进口航线样本:')
        print(guohuo_data[import_cols].head().to_string())