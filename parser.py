# D:\flight_tool\parser.py
import pandas as pd
import re
import os
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

def parse_route_text(text):
    """解析航线文本，提取起点和终点信息"""
    if pd.isna(text) or not str(text).strip():
        return []
    
    # 使用正则表达式分割航线文本
    parts = re.split(r'\s*[-—>\u2192]\s*', str(text).strip())
    results = []
    
    for p in parts:
        # 提取IATA代码
        m = re.search(r'([A-Z]{3})', p)
        iata = m.group(1) if m else None
        # 清理城市名称
        clean_name = re.sub(r'\([A-Z]{3}\)', '', p).strip()
        results.append({"name": clean_name, "iata": iata})
    
    # 生成航段
    segments = []
    for i in range(len(results) - 1):
        segments.append((results[i], results[i + 1]))
    
    return segments

def detect_table_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """智能检测表格结构和列映射"""
    structure = {
        'airline_col': None,
        'route_cols': [],
        'origin_col': None,
        'destination_col': None,
        'aircraft_col': None,
        'flight_number_col': None,
        'frequency_col': None,
        'reg_col': None,
        'age_col': None,
        'flight_time_cols': [],
        'flight_distance_cols': [],
        'special_col': None,
        'data_start_row': 0,
        'has_merged_cells': False
    }
    
    # 列名关键词映射
    column_keywords = {
        'airline': ['航司', '航空公司', '公司', 'airline', 'carrier'],
        'route': ['航线', '路线', 'route', '出口航线', '进口航线'],
        'origin': ['起点', '出发地', '始发地', 'origin', 'departure', '起飞'],
        'destination': ['终点', '目的地', '到达地', 'destination', 'arrival', '降落'],
        'aircraft': ['机型', '飞机型号', 'aircraft', 'plane', '机种'],
        'flight_number': ['航班号', '班次', 'flight', 'number'],
        'frequency': ['频率', '班期', 'frequency', '运营'],
        'reg': ['注册号', 'reg', '机号', '尾号'],
        'age': ['机龄', 'age', '年龄'],
        'flight_time': ['飞行时长', '飞行时间', 'time', '时长'],
        'flight_distance': ['飞行距离', '距离', 'distance', '里程'],
        'special': ['特殊', '备注', '说明', 'special', 'note']
    }
    
    # 检测列映射
    for col in df.columns:
        col_str = str(col).lower().strip()
        
        for key, keywords in column_keywords.items():
            if any(keyword in col_str for keyword in keywords):
                if key == 'route':
                    structure['route_cols'].append(col)
                elif key == 'flight_time':
                    structure['flight_time_cols'].append(col)
                elif key == 'flight_distance':
                    structure['flight_distance_cols'].append(col)
                else:
                    structure[f'{key}_col'] = col
                break
    
    # 检测数据开始行（跳过标题和空行）
    for i, row in df.iterrows():
        if not row.isna().all() and any(str(val).strip() for val in row if pd.notna(val)):
            # 检查是否是数据行而不是标题行
            non_empty_values = [str(val).strip() for val in row if pd.notna(val) and str(val).strip()]
            if len(non_empty_values) >= 2:  # 至少有2个非空值才认为是数据行
                structure['data_start_row'] = i
                break
    
    # 检测是否有合并单元格（通过检查重复值模式）
    if len(df) > 1:
        for col in df.columns:
            consecutive_same = 0
            max_consecutive = 0
            prev_val = None
            
            for val in df[col]:
                if pd.notna(val) and val == prev_val:
                    consecutive_same += 1
                    max_consecutive = max(max_consecutive, consecutive_same)
                else:
                    consecutive_same = 0
                prev_val = val
            
            if max_consecutive > 2:  # 连续3个以上相同值可能是合并单元格
                structure['has_merged_cells'] = True
                break
    
    return structure

def clean_and_normalize_data(df: pd.DataFrame, structure: Dict[str, Any]) -> pd.DataFrame:
    """清理和标准化数据"""
    # 从检测到的数据开始行开始处理
    if structure['data_start_row'] > 0:
        df = df.iloc[structure['data_start_row']:].reset_index(drop=True)
    
    # 删除完全空白的行
    df = df.dropna(how='all').reset_index(drop=True)
    
    # 处理合并单元格（向下填充）
    if structure['has_merged_cells']:
        # 对关键列进行前向填充
        key_cols = [structure['airline_col'], structure['aircraft_col'], structure['reg_col']]
        for col in key_cols:
            if col and col in df.columns:
                df[col] = df[col].fillna(method='ffill')
    
    # 清理文本数据
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['nan', 'NaN', '', 'None'], np.nan)
    
    return df

def categorize_city_for_direction(city_name: str) -> str:
    """判断城市是国内还是国外（用于方向判断）"""
    # 中国主要城市列表（包括港澳台）
    chinese_cities = {
        # 直辖市
        '北京', '上海', '天津', '重庆',
        # 省会城市
        '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '郑州', '济南', '沈阳',
        '长春', '哈尔滨', '石家庄', '太原', '呼和浩特', '兰州', '西宁', '银川', '乌鲁木齐',
        '合肥', '福州', '南昌', '长沙', '海口', '南宁', '贵阳', '昆明', '拉萨',
        # 其他重要城市
        '苏州', '无锡', '常州', '南通', '徐州', '扬州', '镇江', '泰州', '盐城', '淮安', '宿迁', '连云港',
        '宁波', '温州', '嘉兴', '湖州', '绍兴', '金华', '衢州', '舟山', '台州', '丽水',
        '青岛', '烟台', '潍坊', '临沂', '淄博', '济宁', '泰安', '威海', '日照', '滨州',
        '东营', '聊城', '德州', '菏泽', '枣庄', '莱芜',
        '大连', '鞍山', '抚顺', '本溪', '丹东', '锦州', '营口', '阜新', '辽阳', '盘锦',
        '铁岭', '朝阳', '葫芦岛',
        '长春', '吉林', '四平', '辽源', '通化', '白山', '松原', '白城', '延边',
        '哈尔滨', '齐齐哈尔', '鸡西', '鹤岗', '双鸭山', '大庆', '伊春', '佳木斯', '七台河',
        '牡丹江', '黑河', '绥化', '大兴安岭',
        '厦门', '泉州', '漳州', '莆田', '三明', '龙岩', '南平', '宁德',
        '南昌', '景德镇', '萍乡', '九江', '新余', '鹰潭', '赣州', '吉安', '宜春', '抚州', '上饶',
        '珠海', '汕头', '佛山', '韶关', '湛江', '肇庆', '江门', '茂名', '惠州', '梅州',
        '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮',
        '柳州', '桂林', '梧州', '北海', '防城港', '钦州', '贵港', '玉林', '百色', '贺州',
        '河池', '来宾', '崇左',
        '三亚', '三沙', '儋州',
        '遵义', '六盘水', '安顺', '毕节', '铜仁', '黔西南', '黔东南', '黔南',
        '曲靖', '玉溪', '保山', '昭通', '丽江', '普洱', '临沧', '楚雄', '红河', '文山',
        '西双版纳', '大理', '德宏', '怒江', '迪庆',
        '日喀则', '昌都', '林芝', '山南', '那曲', '阿里',
        '宝鸡', '咸阳', '铜川', '渭南', '延安', '榆林', '汉中', '安康', '商洛',
        '洛阳', '开封', '平顶山', '安阳', '鹤壁', '新乡', '焦作', '濮阳', '许昌', '漯河',
        '三门峡', '南阳', '商丘', '信阳', '周口', '驻马店', '济源',
        '株洲', '湘潭', '衡阳', '邵阳', '岳阳', '常德', '张家界', '益阳', '郴州', '永州',
        '怀化', '娄底', '湘西',
        '芜湖', '蚌埠', '淮南', '马鞍山', '淮北', '铜陵', '安庆', '黄山', '滁州', '阜阳',
        '宿州', '六安', '亳州', '池州', '宣城',
        '唐山', '秦皇岛', '邯郸', '邢台', '保定', '张家口', '承德', '沧州', '廊坊', '衡水',
        '大同', '阳泉', '长治', '晋城', '朔州', '晋中', '运城', '忻州', '临汾', '吕梁',
        '包头', '乌海', '赤峰', '通辽', '鄂尔多斯', '呼伦贝尔', '巴彦淖尔', '乌兰察布',
        '兴安盟', '锡林郭勒盟', '阿拉善盟',
        '金昌', '白银', '天水', '武威', '张掖', '平凉', '酒泉', '庆阳', '定西', '陇南',
        '临夏', '甘南',
        '海东', '海北', '黄南', '海南', '果洛', '玉树', '海西',
        '石嘴山', '吴忠', '固原', '中卫',
        '克拉玛依', '吐鲁番', '哈密', '昌吉', '博尔塔拉', '巴音郭楞', '阿克苏', '克孜勒苏',
        '喀什', '和田', '伊犁', '塔城', '阿勒泰',
        # 港澳台
        '香港', '澳门', '台北', '高雄', '台中', '台南', '桃园', '新竹', '基隆', '嘉义',
        '台东', '花莲', '宜兰', '苗栗', '彰化', '南投', '云林', '屏东', '澎湖', '金门', '马祖',
        # 其他常见城市
        '鄂州'
    }
    
    # 清理城市名称（去除可能的机场后缀）
    clean_city = str(city_name).replace('机场', '').replace('国际机场', '').replace('Airport', '').strip()
    
    # 检查是否为中国城市
    for chinese_city in chinese_cities:
        if chinese_city in clean_city:
            return '国内'
    
    return '国外'

def determine_direction(origin: str, destination: str) -> str:
    """根据起点和终点判断进出口方向"""
    origin_type = categorize_city_for_direction(origin)
    dest_type = categorize_city_for_direction(destination)
    
    # 国内到国外 = 出口
    if origin_type == '国内' and dest_type == '国外':
        return '出口'
    # 国外到国内 = 进口
    elif origin_type == '国外' and dest_type == '国内':
        return '进口'
    # 国内到国内 = 国内航线（标记为出口）
    elif origin_type == '国内' and dest_type == '国内':
        return '出口'
    # 国外到国外 = 国际中转（标记为出口）
    else:
        return '出口'

def extract_route_info(row: pd.Series, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
    """从行数据中提取航线信息"""
    routes = []
    
    # 优先使用明确的起点终点列
    if structure['origin_col'] and structure['destination_col']:
        origin = row.get(structure['origin_col'])
        destination = row.get(structure['destination_col'])
        
        if pd.notna(origin) and pd.notna(destination):
            origin_str = str(origin).strip()
            destination_str = str(destination).strip()
            direction = determine_direction(origin_str, destination_str)
            
            routes.append({
                'origin': origin_str,
                'destination': destination_str,
                'direction': direction
            })
    
    # 解析航线列
    for route_col in structure['route_cols']:
        if route_col in row.index and pd.notna(row[route_col]):
            route_text = str(row[route_col]).strip()
            
            # 解析航线文本
            segments = parse_route_text(route_text)
            for origin_info, dest_info in segments:
                origin_name = origin_info['name']
                dest_name = dest_info['name']
                direction = determine_direction(origin_name, dest_name)
                
                routes.append({
                    'origin': origin_name,
                    'destination': dest_name,
                    'direction': direction,
                    'origin_iata': origin_info['iata'],
                    'dest_iata': dest_info['iata']
                })
    
    return routes

def load_data(files):
    """加载并解析多个航司数据文件 - 智能解析版本"""
    all_rows = []
    successfully_loaded_files = []  # 记录成功加载的文件
    
    for file in files:
        try:
            print(f"正在处理文件: {os.path.basename(file)}")
            
            # 多种方式尝试读取文件
            df = None
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            
            if file.lower().endswith(('.xlsx', '.xls')):
                try:
                    df = pd.read_excel(file, engine='openpyxl')
                except:
                    try:
                        df = pd.read_excel(file, engine='xlrd')
                    except:
                        print(f"无法读取Excel文件: {file}")
                        continue
            elif file.lower().endswith('.csv'):
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file, encoding=encoding)
                        break
                    except:
                        continue
                if df is None:
                    print(f"⚠️ 跳过无法读取的CSV文件: {os.path.basename(file)}")
                    continue
            else:
                # 尝试自动检测格式
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file, encoding=encoding)
                        break
                    except:
                        try:
                            df = pd.read_excel(file)
                            break
                        except:
                            continue
                if df is None:
                    print(f"⚠️ 跳过无法识别格式的文件: {os.path.basename(file)}")
                    continue
            
            if df is None or df.empty:
                print(f"⚠️ 跳过空文件: {os.path.basename(file)}")
                continue
            
            print(f"原始数据形状: {df.shape}")
            print(f"列名: {list(df.columns)}")
            
            # 智能检测表格结构
            structure = detect_table_structure(df)
            print(f"检测到的结构: {structure}")
            
            # 清理和标准化数据
            df_clean = clean_and_normalize_data(df, structure)
            print(f"清理后数据形状: {df_clean.shape}")
            
            # 从文件名提取航司名称
            airline_name = os.path.basename(file).split('.')[0]
            # 清理文件名中的前缀
            for prefix in ['示例数据_', '数据_', 'sample_', 'data_']:
                if airline_name.startswith(prefix):
                    airline_name = airline_name[len(prefix):]
                    break
            
            # 处理每一行数据
            processed_count = 0
            for idx, row in df_clean.iterrows():
                # 获取航司名称
                airline_value = None
                if structure['airline_col'] and structure['airline_col'] in row.index:
                    airline_value = row[structure['airline_col']]
                
                # 如果没有航司列或航司为空，使用文件名
                if pd.isna(airline_value) or str(airline_value).strip() == '':
                    airline_value = airline_name
                
                if pd.isna(airline_value) or str(airline_value).strip() == '':
                    continue  # 跳过无法确定航司的行
                
                # 提取航线信息
                routes = extract_route_info(row, structure)
                
                # 如果没有找到航线信息，尝试其他方法
                if not routes:
                    # 检查是否有未识别的列包含航线信息
                    for col in df_clean.columns:
                        if col not in [structure.get(k) for k in structure.keys() if k.endswith('_col')]:
                            col_value = row[col]
                            if pd.notna(col_value) and '-' in str(col_value):
                                segments = parse_route_text(str(col_value))
                                for origin_info, dest_info in segments:
                                    routes.append({
                                        'origin': origin_info['name'],
                                        'destination': dest_info['name'],
                                        'direction': '出口',
                                        'origin_iata': origin_info['iata'],
                                        'dest_iata': dest_info['iata']
                                    })
                                break
                
                # 为每个航线创建记录
                for route_info in routes:
                    # 获取其他字段值
                    reg_value = ''
                    if structure['reg_col'] and structure['reg_col'] in row.index:
                        reg_value = row[structure['reg_col']] if pd.notna(row[structure['reg_col']]) else ''
                    
                    aircraft_value = ''
                    if structure['aircraft_col'] and structure['aircraft_col'] in row.index:
                        aircraft_value = row[structure['aircraft_col']] if pd.notna(row[structure['aircraft_col']]) else ''
                    
                    age_value = ''
                    if structure['age_col'] and structure['age_col'] in row.index:
                        age_value = row[structure['age_col']] if pd.notna(row[structure['age_col']]) else ''
                    
                    flight_number_value = ''
                    if structure['flight_number_col'] and structure['flight_number_col'] in row.index:
                        flight_number_value = row[structure['flight_number_col']] if pd.notna(row[structure['flight_number_col']]) else ''
                    
                    frequency_value = '正常运营'
                    if structure['frequency_col'] and structure['frequency_col'] in row.index:
                        frequency_value = row[structure['frequency_col']] if pd.notna(row[structure['frequency_col']]) else '正常运营'
                    
                    special_value = ''
                    if structure['special_col'] and structure['special_col'] in row.index:
                        special_value = row[structure['special_col']] if pd.notna(row[structure['special_col']]) else ''
                    
                    # 获取飞行时间和距离
                    flight_time_value = ''
                    flight_distance_value = ''
                    
                    for time_col in structure['flight_time_cols']:
                        if time_col in row.index and pd.notna(row[time_col]):
                            flight_time_value = str(row[time_col])
                            break
                    
                    for dist_col in structure['flight_distance_cols']:
                        if dist_col in row.index and pd.notna(row[dist_col]):
                            flight_distance_value = str(row[dist_col])
                            break
                    
                    all_rows.append({
                        "direction": route_info.get('direction', '出口'),
                        "airline": str(airline_value).strip(),
                        "reg": str(reg_value).strip(),
                        "aircraft": str(aircraft_value).strip(),
                        "age": str(age_value).strip(),
                        "origin": route_info['origin'],
                        "origin_iata": route_info.get('origin_iata', ''),
                        "destination": route_info['destination'],
                        "dest_iata": route_info.get('dest_iata', ''),
                        "flight_time": str(flight_time_value).strip(),
                        "flight_distance": str(flight_distance_value).strip(),
                        "special": str(special_value or frequency_value).strip(),
                        "flight_number": str(flight_number_value).strip()
                    })
                    processed_count += 1
            
            print(f"从文件 {os.path.basename(file)} 中提取了 {processed_count} 条航线记录")
            successfully_loaded_files.append(os.path.basename(file))  # 记录成功加载的文件
            
        except Exception as e:
            print(f"处理文件 {file} 时出错: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    result_df = pd.DataFrame(all_rows)
    
    # 数据合并统计
    if len(successfully_loaded_files) > 1:
        print(f"\n📊 数据合并统计：")
        print(f"   成功加载文件数量：{len(successfully_loaded_files)}")
        print(f"   合并后总记录数：{len(result_df)}")
        
        # 按航司统计
        if 'airline' in result_df.columns:
            airline_counts = result_df['airline'].value_counts()
            print(f"   涉及航司数量：{len(airline_counts)}")
            for airline, count in airline_counts.head(5).items():
                print(f"     - {airline}: {count} 条记录")
            if len(airline_counts) > 5:
                print(f"     - 其他 {len(airline_counts) - 5} 个航司...")
    else:
        print(f"总共加载了 {len(result_df)} 条航线记录")
    
    # 将成功加载的文件信息添加到DataFrame的元数据中
    result_df.attrs['successfully_loaded_files'] = successfully_loaded_files
    return result_df