import pandas as pd

def analyze_guohang_data():
    """详细分析国货航的航线数据"""
    try:
        # 读取解析结果
        df = pd.read_csv('parsed_routes.csv')
        guohang = df[df['airline'] == '国货航']
        
        print(f"=== 国货航航线数据分析 ===")
        print(f"总航线数: {len(guohang)}")
        
        print(f"\n=== 按方向统计 ===")
        direction_counts = guohang['direction'].value_counts()
        for direction, count in direction_counts.items():
            print(f"  {direction}: {count} 条")
        
        print(f"\n=== 起点城市统计 ===")
        origin_counts = guohang['origin'].value_counts()
        for origin, count in origin_counts.items():
            print(f"  {origin}: {count} 条")
        
        print(f"\n=== 终点城市统计 ===")
        dest_counts = guohang['destination'].value_counts()
        for dest, count in dest_counts.items():
            print(f"  {dest}: {count} 条")
        
        print(f"\n=== 详细航线列表 ===")
        for i, row in guohang.iterrows():
            print(f"  {row['origin']} -> {row['destination']} ({row['direction']})")
        
        # 检查是否有浦东相关航线
        print(f"\n=== 浦东相关航线检查 ===")
        pudong_routes = guohang[(guohang['origin'].str.contains('浦东', na=False)) | 
                               (guohang['destination'].str.contains('浦东', na=False))]
        
        if len(pudong_routes) > 0:
            print(f"找到 {len(pudong_routes)} 条浦东相关航线:")
            for i, row in pudong_routes.iterrows():
                print(f"  {row['origin']} -> {row['destination']} ({row['direction']})")
        else:
            print("未找到浦东相关航线")
        
        # 检查原始Excel数据中国货航的所有记录
        print(f"\n=== 原始Excel数据检查 ===")
        excel_df = pd.read_excel('D:\\flight_tool\\data\\大陆航司全货机航线.xlsx')
        
        # 找到国货航的起始行
        guohang_start_idx = None
        for idx, row in excel_df.iterrows():
            if pd.notna(row.get('航司', '')) and str(row.get('航司', '')).strip() == '国货航':
                guohang_start_idx = idx
                break
        
        if guohang_start_idx is not None:
            print(f"国货航数据从第 {guohang_start_idx + 1} 行开始")
            
            # 找到下一个航司的起始行
            next_airline_idx = None
            for idx in range(guohang_start_idx + 1, len(excel_df)):
                if pd.notna(excel_df.iloc[idx].get('航司', '')) and str(excel_df.iloc[idx].get('航司', '')).strip() != '':
                    next_airline_idx = idx
                    break
            
            if next_airline_idx is None:
                next_airline_idx = len(excel_df)
            
            print(f"国货航数据到第 {next_airline_idx} 行结束，共 {next_airline_idx - guohang_start_idx} 行")
            
            # 显示国货航的所有原始数据
            guohang_data = excel_df.iloc[guohang_start_idx:next_airline_idx]
            print(f"\n=== 国货航原始数据 ===")
            
            for idx, row in guohang_data.iterrows():
                export_route = row.get('出口航线', '')
                import_route = row.get('进口航线', '')
                reg_no = row.get('注册号', '')
                
                print(f"第 {idx + 1} 行:")
                print(f"  注册号: {reg_no}")
                print(f"  出口航线: {export_route}")
                print(f"  进口航线: {import_route}")
                print()
        
    except Exception as e:
        print(f"分析时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_guohang_data()