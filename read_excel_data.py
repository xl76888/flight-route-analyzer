import pandas as pd
import os

# 设置文件路径
file_path = r'd:\flight_tool\data\中国十六家货航国际航线.xlsx'

def read_and_display_excel():
    """读取并展示Excel文件数据"""
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None
        
        # 读取Excel文件
        print("正在读取Excel文件...")
        df = pd.read_excel(file_path)
        
        # 显示基本信息
        print(f"\n文件读取成功！")
        print(f"数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
        print(f"列名: {list(df.columns)}")
        
        # 显示前10行数据
        print("\n前10行数据:")
        print("-" * 80)
        print(df.head(10).to_string(index=False))
        
        # 显示数据基本信息
        print(f"\n数据概览:")
        print("-" * 40)
        print(df.info())
        
        # 显示数据统计
        print(f"\n数据统计:")
        print("-" * 40)
        print(df.describe(include='all'))
        
        return df
        
    except Exception as e:
        print(f"读取文件时出错: {str(e)}")
        return None

if __name__ == "__main__":
    # 检查pandas是否安装
    try:
        import pandas
    except ImportError:
        print("正在安装pandas...")
        os.system("pip install pandas openpyxl")
    
    # 读取并显示数据
    data = read_and_display_excel()
    
    if data is not None:
        print(f"\n数据读取完成！共 {len(data)} 条记录")
        
        # 保存为CSV文件以便查看
        csv_path = r'd:\flight_tool\data\中国十六家货航国际航线_导出.csv'
        data.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"数据已导出到: {csv_path}")