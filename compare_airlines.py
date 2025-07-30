import pandas as pd
from fix_parser import parse_excel_route_data
from data_cleaner import clean_route_data

def compare_airlines():
    """对比原始数据、解析后数据和清理后数据的航司差异"""
    
    # 1. 读取原始Excel数据
    print("=== 1. 原始Excel数据中的航司 ===")
    df_original = pd.read_excel('data/大陆航司全货机航线.xlsx')
    original_airlines = set(df_original['航司'].dropna().unique())
    print(f"原始航司数量: {len(original_airlines)}")
    for i, airline in enumerate(sorted(original_airlines), 1):
        print(f"{i:2d}. {airline}")
    
    # 2. 解析后的数据
    print("\n=== 2. 解析后数据中的航司 ===")
    df_parsed = parse_excel_route_data('data/大陆航司全货机航线.xlsx')
    if not df_parsed.empty:
        parsed_airlines = set(df_parsed['airline'].unique())
        print(f"解析后航司数量: {len(parsed_airlines)}")
        for i, airline in enumerate(sorted(parsed_airlines), 1):
            print(f"{i:2d}. {airline}")
        
        # 找出被过滤掉的航司
        filtered_out_1 = original_airlines - parsed_airlines
        if filtered_out_1:
            print(f"\n解析阶段被过滤的航司 ({len(filtered_out_1)}家):")
            for airline in sorted(filtered_out_1):
                print(f"  - {airline}")
    else:
        print("解析失败")
        return
    
    # 3. 清理后的数据
    print("\n=== 3. 清理后数据中的航司 ===")
    df_cleaned = clean_route_data(df_parsed.copy())
    if not df_cleaned.empty:
        cleaned_airlines = set(df_cleaned['airline'].unique())
        print(f"清理后航司数量: {len(cleaned_airlines)}")
        for i, airline in enumerate(sorted(cleaned_airlines), 1):
            print(f"{i:2d}. {airline}")
        
        # 找出在清理阶段被过滤掉的航司
        filtered_out_2 = parsed_airlines - cleaned_airlines
        if filtered_out_2:
            print(f"\n清理阶段被过滤的航司 ({len(filtered_out_2)}家):")
            for airline in sorted(filtered_out_2):
                print(f"  - {airline}")
                
                # 分析为什么被过滤
                airline_data = df_parsed[df_parsed['airline'] == airline]
                print(f"    该航司原有 {len(airline_data)} 条航线记录")
                
                # 检查城市有效性
                invalid_origins = []
                invalid_destinations = []
                
                for _, row in airline_data.iterrows():
                    origin = row['origin']
                    destination = row['destination']
                    
                    # 这里需要导入城市验证函数
                    from data_cleaner import is_valid_city
                    
                    if not is_valid_city(origin):
                        invalid_origins.append(origin)
                    if not is_valid_city(destination):
                        invalid_destinations.append(destination)
                
                if invalid_origins:
                    print(f"    无效起点城市: {set(invalid_origins)}")
                if invalid_destinations:
                    print(f"    无效终点城市: {set(invalid_destinations)}")
    else:
        print("清理失败")
        return
    
    # 4. 总结
    print(f"\n=== 总结 ===")
    print(f"原始航司: {len(original_airlines)} 家")
    print(f"解析后航司: {len(parsed_airlines)} 家")
    print(f"清理后航司: {len(cleaned_airlines)} 家")
    print(f"总共丢失: {len(original_airlines) - len(cleaned_airlines)} 家航司")
    
    total_lost = original_airlines - cleaned_airlines
    if total_lost:
        print(f"\n丢失的航司:")
        for airline in sorted(total_lost):
            print(f"  - {airline}")

if __name__ == "__main__":
    compare_airlines()