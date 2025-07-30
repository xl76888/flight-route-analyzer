import pandas as pd

def check_airline_routes():
    file_path = "D:\\flight_tool\\data\\大陆航司全货机航线.xlsx"
    df = pd.read_excel(file_path)
    
    print("=== 各航司航线数据检查 ===")
    
    for airline in df['航司'].dropna().unique():
        airline_data = df[df['航司'] == airline]
        print(f"\n{airline} (共{len(airline_data)}条记录):")
        
        for idx, row in airline_data.iterrows():
            export_route = row.get('出口航线', '')
            import_route = row.get('进口航线', '')
            reg_no = row.get('注册号', '')
            
            print(f"  记录{idx+1} - 注册号: {reg_no}")
            print(f"    出口航线: {export_route}")
            print(f"    进口航线: {import_route}")
            print()

if __name__ == "__main__":
    check_airline_routes()