import pandas as pd

def check_guohang_pudong():
    """检查国货航的浦东相关航线"""
    df = pd.read_csv('parsed_routes.csv')
    guohang = df[df['airline'] == '国货航']
    
    print(f"国货航总航线数: {len(guohang)}")
    
    # 查找浦东相关航线
    pudong = guohang[
        (guohang['origin'].str.contains('浦东', na=False)) | 
        (guohang['destination'].str.contains('浦东', na=False))
    ]
    
    print(f"浦东相关航线数: {len(pudong)}")
    
    print("\n=== 浦东相关航线详情 ===")
    for i, row in pudong.iterrows():
        print(f"{row['origin']} -> {row['destination']} ({row['direction']})")
    
    print("\n=== 国货航所有起点城市统计 ===")
    origin_counts = guohang['origin'].value_counts()
    for city, count in origin_counts.head(15).items():
        print(f"  {city}: {count} 条")
    
    print("\n=== 国货航所有终点城市统计 ===")
    dest_counts = guohang['destination'].value_counts()
    for city, count in dest_counts.head(15).items():
        print(f"  {city}: {count} 条")
    
    # 检查是否有遗漏的浦东航线
    print("\n=== 检查可能遗漏的浦东航线 ===")
    all_origins = guohang['origin'].unique()
    all_dests = guohang['destination'].unique()
    
    pudong_origins = [city for city in all_origins if '浦东' in str(city)]
    pudong_dests = [city for city in all_dests if '浦东' in str(city)]
    
    print(f"包含'浦东'的起点城市: {pudong_origins}")
    print(f"包含'浦东'的终点城市: {pudong_dests}")
    
    # 显示前20条国货航航线
    print("\n=== 国货航前20条航线 ===")
    for i, row in guohang.head(20).iterrows():
        print(f"{i+1:2d}. {row['origin']} -> {row['destination']} ({row['direction']})")

if __name__ == "__main__":
    check_guohang_pudong()