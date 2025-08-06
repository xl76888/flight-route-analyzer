# D:\flight_tool\data_cleaner.py
import pandas as pd
import re
from typing import List, Dict, Set

# 定义有效的城市名称映射和清理规则
CITY_NAME_MAPPING = {
    # 机场名称到城市名称的映射（确保映射后的城市在相应列表中存在）
    '班达拉奈克': '科伦坡',
    '英迪拉甘地': '新德里',
    '贾特拉帕蒂希瓦': '孟买', 
    '达卡沙阿贾拉勒': '达卡',
    '肯佩戈达': '班加罗尔',
    '阿拉玛伊克巴尔': '拉合尔',
    '扎耶德': '阿布扎比',
    '安克雷奇': '安克雷奇',
    '博乐阿拉山口': '博乐',
    # 直接使用原名称，避免映射问题
    '列日': '列日',
    '布达佩斯': '布达佩斯',
    '金奈': '金奈',
    '东京': '东京',
    '首尔': '首尔',
    '新加坡': '新加坡',
    
    # 标准化城市名称
    '北京': '北京',
    '上海': '上海',
    '广州': '广州',
    '深圳': '深圳',
    '成都': '成都',
    '重庆': '重庆',
    '杭州': '杭州',
    '南京': '南京',
    '武汉': '武汉',
    '西安': '西安',
    '昆明': '昆明',
    '郑州': '郑州',
    '长沙': '长沙',
    '沈阳': '沈阳',
    '大连': '大连',
    '青岛': '青岛',
    '天津': '天津',
    '海口': '海口',
    '贵阳': '贵阳',
    '兰州': '兰州',
    '乌鲁木齐': '乌鲁木齐',
    '哈尔滨': '哈尔滨',
    '长春': '长春',
    '南宁': '南宁',
    
    # 常见拼写错误映射
    '日本大版': '大阪',
    '日本大坂': '大阪',
    '南通': '南通',
    '无锡': '无锡',
    '宁波': '宁波',
    '潍坊': '潍坊',
    '烟台': '烟台',
    '鄂州': '鄂州',
    
    # 国际城市
    '东京': '东京',
    '大阪': '大阪',
    '首尔': '首尔',
    '台北': '台北',
    '香港': '香港',
    '新加坡': '新加坡',
    '吉隆坡': '吉隆坡',
    '马尼拉': '马尼拉',
    '胡志明': '胡志明市',
    '金奈': '金奈',
    '法兰克福': '法兰克福',
    '列日': '列日',
    '布达佩斯': '布达佩斯',
    '奥斯陆': '奥斯陆',
    '洛杉矶': '洛杉矶',
    '纽约': '纽约',
    '哈利法克斯': '哈利法克斯',
    '卡拉干达': '卡拉干达',
    '阿拉木图': '阿拉木图',
    '第比利斯': '第比利斯',
    '伊斯兰堡': '伊斯兰堡',
    
    # 机场全名到城市名称的映射
    '昆明长水': '昆明',
    '温州龙湾': '温州',
    '杭州萧山': '杭州',
    '马尼拉尼诺阿基诺': '马尼拉',
    '首尔仁川': '首尔',
    '苏巴斯·钱德拉·鲍斯': '科伦坡',
    '苏巴斯·钱德拉·鲍斯-阿勒马克图姆': '科伦坡',
    '阿勒马克图姆': '迪拜',
    '努尔苏丹纳扎尔巴耶夫': '阿斯塔纳',
    '努尔苏丹纳扎尔巴耶夫-布达佩斯': '阿斯塔纳',
    '达卡沙阿贾拉勒': '达卡',
    '布达佩斯': '布达佩斯',
    '东京成田': '东京',
    # 修复中货航缺失的城市映射
    '上海浦东': '上海',
    '纽约肯尼迪': '纽约',
    '伦敦斯坦斯特德': '伦敦',
    '伦敦斯塔斯特德': '伦敦'
}

# 无效数据模式
INVALID_PATTERNS = [
    r'^\d+ER类似$',  # 如 338ER类似
    r'^[A-Z0-9]+$',   # 纯大写字母数字组合
    r'^\s*$',         # 空白
    r'^nan$',         # NaN值
    r'^null$',        # null值
]

# 国内城市列表
DOMESTIC_CITIES = {
    # 直辖市
    '北京', '上海', '天津', '重庆',
    # 省会及重要城市
    '广州', '深圳', '成都', '杭州', '南京', '武汉', '西安', '昆明', '郑州', '长沙',
    '沈阳', '大连', '青岛', '海口', '贵阳', '兰州', '乌鲁木齐', '哈尔滨', '长春', '南宁',
    '南通', '无锡', '宁波', '潍坊', '烟台', '鄂州', '石家庄', '太原', '呼和浩特',
    '合肥', '福州', '南昌', '济南', '银川', '西宁', '拉萨',
    # 其他重要城市
    '苏州', '温州', '厦门', '泉州', '佛山', '东莞', '中山', '珠海', '汕头', '湛江',
    '惠州', '江门', '茂名', '肇庆', '梅州', '韶关', '河源', '阳江', '清远', '潮州',
    '揭阳', '云浮', '汕尾', '宜昌', '襄阳', '荆州', '黄冈', '孝感', '十堰', '随州',
    '恩施', '黄石', '咸宁', '鄂州', '荆门', '仙桃', '潜江', '天门', '神农架',
    # 补充缺失的国内城市
    '芜湖', '盐城', '淮安', '连云港', '扬州', '镇江', '泰州', '宿迁',
    '嘉兴', '湖州', '绍兴', '金华', '衢州', '舟山', '台州', '丽水',
    '蚌埠', '淮南', '马鞍山', '淮北', '铜陵', '安庆', '黄山', '滁州',
    '阜阳', '宿州', '六安', '亳州', '池州', '宣城'
}

# 国际城市列表
INTERNATIONAL_CITIES = {
    # 亚洲
    '东京', '大阪', '名古屋', '福冈', '札幌', '仙台', '关西', '成田', '羽田',
    '首尔', '釜山', '济州', '仁川',
    '台北', '高雄', '台中', '桃园',
    '香港', '澳门',
    '新加坡', '樟宜',
    '吉隆坡', '槟城', '亚庇',
    '马尼拉', '宿务', '克拉克',
    '胡志明市', '河内', '岘港',
    '曼谷', '普吉', '清迈',
    '雅加达', '巴厘岛', '泗水',
    '金奈', '科伦坡', '新德里', '孟买', '达卡', '班加罗尔', '拉合尔', '卡拉奇',
    '伊斯兰堡', '加德满都', '科威特', '多哈', '迪拜', '阿布扎比', '沙迦',
    '利雅得', '吉达', '达曼', '麦地那',
    # 欧洲
    '法兰克福', '慕尼黑', '柏林', '汉堡', '杜塞尔多夫', '科隆',
    '伦敦', '曼彻斯特', '爱丁堡', '格拉斯哥', '东米德兰兹', '斯坦斯特德',
    '巴黎', '里昂', '马赛', '尼斯', '戴高乐',
    '阿姆斯特丹', '鹿特丹',
    '布鲁塞尔', '列日', '安特卫普',
    '苏黎世', '日内瓦', '巴塞尔',
    '维也纳', '萨尔茨堡',
    '罗马', '米兰', '威尼斯', '那不勒斯',
    '马德里', '巴塞罗那', '塞维利亚',
    '里斯本', '波尔图',
    '斯德哥尔摩', '哥德堡', '奥斯陆', '卑尔根', '赫尔辛基',
    '哥本哈根', '奥胡斯',
    '华沙', '克拉科夫', '格但斯克',
    '布拉格', '布尔诺',
    '布达佩斯', '德布勒森',
    '布加勒斯特', '康斯坦察',
    '索非亚', '普罗夫迪夫',
    '贝尔格莱德', '诺维萨德',
    '萨格勒布', '斯普利特',
    '卢布尔雅那', '马里博尔',
    '塔林', '里加', '维尔纽斯',
    '莫斯科', '圣彼得堡', '新西伯利亚', '叶卡捷琳堡',
    # 北美洲
    '纽约', '洛杉矶', '芝加哥', '旧金山', '西雅图', '波士顿', '华盛顿',
    '迈阿密', '拉斯维加斯', '丹佛', '达拉斯', '休斯顿', '亚特兰大',
    '多伦多', '温哥华', '蒙特利尔', '卡尔加里', '哈利法克斯',
    '墨西哥城', '坎昆', '瓜达拉哈拉',
    # 南美洲
    '圣保罗', '里约热内卢', '巴西利亚',
    '布宜诺斯艾利斯', '科尔多瓦',
    '圣地亚哥', '瓦尔帕莱索',
    '利马', '库斯科',
    '波哥大', '麦德林',
    '基多', '瓜亚基尔',
    '加拉加斯', '马拉开波',
    # 非洲
    '开罗', '亚历山大',
    '约翰内斯堡', '开普敦', '德班',
    '拉各斯', '阿布贾',
    '内罗毕', '蒙巴萨',
    '亚的斯亚贝巴', '阿克拉',
    '卡萨布兰卡', '拉巴特',
    '突尼斯', '阿尔及尔',
    # 大洋洲
    '悉尼', '墨尔本', '布里斯班', '珀斯', '阿德莱德', '达尔文',
    '奥克兰', '惠灵顿', '基督城',
    # 中亚
    '卡拉干达', '阿拉木图', '阿斯塔纳', '奇姆肯特',
    '塔什干', '撒马尔罕', '布哈拉',
    '比什凯克', '奥什',
    '杜尚别', '库洛布',
    '阿什哈巴德', '土库曼纳巴德',
    '第比利斯', '巴统',
    '埃里温', '久姆里',
    '巴库', '占贾',
    # 其他
    '安克雷奇', '费尔班克斯',
    '博乐', '霍尔果斯', '阿拉山口',
    # 补充缺失的国际城市
    '阿克托别', '宿务', '瓦茨拉夫哈维尔', '菲利普安吉利斯',
    '义乌', '巴库比纳', '巴库比钠', '贾特拉帕蒂希瓦',
    '英迪拉甘地', '马德里巴拉哈斯', '普雷斯蒂克', '斯坦斯特德',
    '肯尼迪', '成田', '浦东', '白云', '咸阳', '萧山', '龙湾',
    '长水', '南阳', '晋江', '兴东',
    # 添加在数据中发现的缺失城市
    '达卡', '素万那普', '卡拉干达', '奥斯陆', '哥本哈根',
    '安赫莱斯', '克拉克', '帕拉尼亚克', '拉普拉普市',
    '麦克坦', '马克坦', '尼诺阿基诺', '阿勒马克图姆',
    '扎阿布扎比', '槟榔屿州', '槟城州', '万塔市',
    '伦敦斯坦斯特德', '英格兰东米德兰兹', '哈利法克斯'
}

def is_valid_city(city_name: str) -> bool:
    """检查是否为有效的城市名称"""
    if not city_name or pd.isna(city_name):
        return False
    
    city_str = str(city_name).strip()
    
    # 检查无效模式
    for pattern in INVALID_PATTERNS:
        if re.match(pattern, city_str, re.IGNORECASE):
            return False
    
    # 检查是否在有效城市列表中
    normalized_city = normalize_city_name(city_str)
    return normalized_city in (DOMESTIC_CITIES | INTERNATIONAL_CITIES)

def normalize_city_name(city_name: str) -> str:
    """标准化城市名称"""
    if not city_name or pd.isna(city_name):
        return ''
    
    city_str = str(city_name).strip()
    
    # 去除多余空格
    city_str = re.sub(r'\s+', '', city_str)
    
    # 应用映射
    if city_str in CITY_NAME_MAPPING:
        return CITY_NAME_MAPPING[city_str]
    
    # 处理带有国家前缀的城市名称
    # 例如: "日本东京" -> "东京", "韩国首尔" -> "首尔"
    country_city_patterns = [
        r'^日本(.+)$',
        r'^韩国(.+)$', 
        r'^美国(.+)$',
        r'^德国(.+)$',
        r'^英国(.+)$',
        r'^法国(.+)$',
        r'^荷兰(.+)$',
        r'^比利时(.+)$',
        r'^丹麦(.+)$',
        r'^挪威(.+)$',
        r'^瑞典(.+)$',
        r'^芬兰(.+)$',
        r'^意大利(.+)$',
        r'^西班牙(.+)$',
        r'^葡萄牙(.+)$',
        r'^俄罗斯(.+)$',
        r'^加拿大(.+)$',
        r'^澳大利亚(.+)$',
        r'^新西兰(.+)$',
        r'^泰国(.+)$',
        r'^越南(.+)$',
        r'^马来西亚(.+)$',
        r'^新加坡(.+)$',
        r'^印度尼西亚(.+)$',
        r'^菲律宾(.+)$',
        r'^印度(.+)$',
        r'^孟加拉(.+)$',
        r'^巴基斯坦(.+)$',
        r'^阿联酋(.+)$',
        r'^沙特阿拉伯(.+)$',
        r'^土耳其(.+)$',
        r'^埃及(.+)$',
        r'^南非(.+)$',
        r'^肯尼亚(.+)$',
        r'^埃塞俄比亚(.+)$',
        r'^巴西(.+)$',
        r'^阿根廷(.+)$',
        r'^智利(.+)$',
        r'^哈萨克斯坦(.+)$',
        r'^乌兹别克斯坦(.+)$',
        r'^吉尔吉斯斯坦(.+)$',
        r'^塔吉克斯坦(.+)$',
        r'^土库曼斯坦(.+)$',
        r'^阿塞拜疆(.+)$',
        r'^格鲁吉亚(.+)$',
        r'^亚美尼亚(.+)$'
    ]
    
    for pattern in country_city_patterns:
        match = re.match(pattern, city_str)
        if match:
            extracted_city = match.group(1)
            # 检查提取的城市名是否在映射中
            if extracted_city in CITY_NAME_MAPPING:
                return CITY_NAME_MAPPING[extracted_city]
            return extracted_city
    
    # 处理复合路线名称，例如: "哈萨克斯坦卡拉干达州-挪威奥斯陆"
    # 取第一个有效的城市名称
    if '-' in city_str:
        parts = city_str.split('-')
        for part in parts:
            part = part.strip()
            # 直接检查是否在映射中
            if part in CITY_NAME_MAPPING:
                candidate = CITY_NAME_MAPPING[part]
                if candidate in (DOMESTIC_CITIES | INTERNATIONAL_CITIES):
                    return candidate
            # 尝试提取国家前缀
            for pattern in country_city_patterns:
                match = re.match(pattern, part)
                if match:
                    extracted_city = match.group(1)
                    if extracted_city in CITY_NAME_MAPPING:
                        extracted_city = CITY_NAME_MAPPING[extracted_city]
                    if extracted_city in (DOMESTIC_CITIES | INTERNATIONAL_CITIES):
                        return extracted_city
            # 直接检查是否在城市列表中
            if part in (DOMESTIC_CITIES | INTERNATIONAL_CITIES):
                return part
    
    return city_str

def categorize_city(city_name: str) -> str:
    """分类城市为国内或国际"""
    normalized = normalize_city_name(city_name)
    
    if normalized in DOMESTIC_CITIES:
        return '国内'
    elif normalized in INTERNATIONAL_CITIES:
        return '国际'
    else:
        return '未知'

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """去除重复的航线记录"""
    if df.empty:
        return df
    
    # 定义用于去重的关键列（不包含airline，保留不同航司的相同航线）
    key_columns = ['origin', 'destination', 'aircraft', 'direction', 'flight_number']
    
    # 只保留存在的列
    existing_key_columns = [col for col in key_columns if col in df.columns]
    
    if not existing_key_columns:
        return df
    
    # 记录去重前的数量
    original_count = len(df)
    
    # 去重，保留第一个出现的记录
    df_dedup = df.drop_duplicates(subset=existing_key_columns, keep='first')
    
    # 记录去重后的数量
    dedup_count = len(df_dedup)
    removed_count = original_count - dedup_count
    
    if removed_count > 0:
        print(f"🔄 数据去重完成：移除了 {removed_count} 条重复记录")
        print(f"   原始记录数：{original_count}")
        print(f"   去重后记录数：{dedup_count}")
    else:
        print("✅ 未发现重复记录")
    
    return df_dedup

def clean_route_data(df: pd.DataFrame, enable_deduplication: bool = True) -> pd.DataFrame:
    """清理航线数据中的始发地和目的地信息
    
    Args:
        df: 原始数据DataFrame
        enable_deduplication: 是否启用去重功能，默认为True
    """
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    # 根据参数决定是否进行数据去重
    if enable_deduplication:
        df_clean = remove_duplicates(df_clean)
    else:
        print(f"📊 保留原始数据：共 {len(df_clean)} 条记录（未去重）")
    
    # 清理始发地
    if 'origin' in df_clean.columns:
        # 标准化城市名称
        df_clean['origin'] = df_clean['origin'].apply(normalize_city_name)
        # 过滤无效城市
        df_clean = df_clean[df_clean['origin'].apply(is_valid_city)]
        # 添加始发地分类
        df_clean['origin_category'] = df_clean['origin'].apply(categorize_city)
    
    # 清理目的地
    if 'destination' in df_clean.columns:
        # 标准化城市名称
        df_clean['destination'] = df_clean['destination'].apply(normalize_city_name)
        # 过滤无效城市
        df_clean = df_clean[df_clean['destination'].apply(is_valid_city)]
        # 添加目的地分类
        df_clean['destination_category'] = df_clean['destination'].apply(categorize_city)
    
    # 移除始发地和目的地相同的记录
    if 'origin' in df_clean.columns and 'destination' in df_clean.columns:
        df_clean = df_clean[df_clean['origin'] != df_clean['destination']]
    
    return df_clean

def get_sorted_cities(df: pd.DataFrame, column: str) -> List[str]:
    """获取排序后的城市列表，国内城市在前，国际城市在后"""
    if column not in df.columns:
        return []
    
    cities = df[column].dropna().unique()
    valid_cities = [city for city in cities if is_valid_city(city)]
    
    # 分类排序
    domestic = sorted([city for city in valid_cities if categorize_city(city) == '国内'])
    international = sorted([city for city in valid_cities if categorize_city(city) == '国际'])
    
    return domestic + international

def print_data_summary(df: pd.DataFrame):
    """打印数据清理摘要"""
    print("\n=== 数据清理摘要 ===")
    print(f"总航线数: {len(df)}")
    
    if 'origin' in df.columns:
        origins = get_sorted_cities(df, 'origin')
        domestic_origins = [city for city in origins if categorize_city(city) == '国内']
        international_origins = [city for city in origins if categorize_city(city) == '国际']
        
        print(f"\n始发地统计:")
        print(f"  国内城市 ({len(domestic_origins)}): {', '.join(domestic_origins)}")
        print(f"  国际城市 ({len(international_origins)}): {', '.join(international_origins)}")
    
    if 'destination' in df.columns:
        destinations = get_sorted_cities(df, 'destination')
        domestic_destinations = [city for city in destinations if categorize_city(city) == '国内']
        international_destinations = [city for city in destinations if categorize_city(city) == '国际']
        
        print(f"\n目的地统计:")
        print(f"  国内城市 ({len(domestic_destinations)}): {', '.join(domestic_destinations)}")
        print(f"  国际城市 ({len(international_destinations)}): {', '.join(international_destinations)}")