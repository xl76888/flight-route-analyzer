# D:\flight_tool\web_app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from parser import load_data
from data_cleaner import clean_route_data, get_sorted_cities, print_data_summary, categorize_city
from airport_coords import get_airport_coords
from static_manager import resource_manager
import os
import pandas as pd
import math
import numpy as np
from geopy.distance import geodesic

# 配置Folium使用本地图标，避免CDN加载错误
os.environ['FOLIUM_ICON_PATH'] = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='

# 尝试导入AntPath插件
try:
    from folium import plugins
    ANTPATH_AVAILABLE = True
except ImportError:
    ANTPATH_AVAILABLE = False
    st.warning("AntPath插件不可用，将使用普通线条显示航线")

# 如果AntPath不可用，尝试安装
if not ANTPATH_AVAILABLE:
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "folium[extras]"])
        from folium import plugins
        ANTPATH_AVAILABLE = True
        st.success("AntPath插件安装成功！")
    except:
        pass

def calculate_flight_distance(origin_coords, dest_coords):
    """
    计算两点间的飞行距离（大圆距离）
    
    Args:
        origin_coords: 起点坐标 [lat, lon]
        dest_coords: 终点坐标 [lat, lon]
    
    Returns:
        距离（公里）
    """
    try:
        if origin_coords and dest_coords and len(origin_coords) == 2 and len(dest_coords) == 2:
            distance = geodesic(origin_coords, dest_coords).kilometers
            return round(distance, 0)
    except:
        pass
    return None

def categorize_city(city_name):
    """
    判断城市是国内还是国外
    """
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
        '台东', '花莲', '宜兰', '苗栗', '彰化', '南投', '云林', '屏东', '澎湖', '金门', '马祖'
    }
    
    # 清理城市名称（去除可能的机场后缀）
    clean_city = str(city_name).replace('机场', '').replace('国际机场', '').replace('Airport', '').strip()
    
    # 检查是否为中国城市
    for chinese_city in chinese_cities:
        if chinese_city in clean_city:
            return '国内'
    
    return '国际'

def calculate_flight_time(distance_km, aircraft_type=''):
    """
    根据距离和机型估算飞行时间
    
    Args:
        distance_km: 飞行距离（公里）
        aircraft_type: 机型
    
    Returns:
        飞行时间（小时:分钟格式）
    """
    try:
        if not distance_km or distance_km <= 0:
            return None
        
        # 根据机型设置平均速度（公里/小时）
        aircraft_speeds = {
            'B737': 850,  # 波音737
            'B747': 900,  # 波音747
            'B757': 850,  # 波音757
            'B767': 850,  # 波音767
            'B777': 900,  # 波音777
            'B787': 900,  # 波音787
            'A320': 840,  # 空客A320
            'A330': 880,  # 空客A330
            'A340': 880,  # 空客A340
            'A350': 900,  # 空客A350
            'A380': 900,  # 空客A380
        }
        
        # 默认速度
        default_speed = 850
        
        # 查找匹配的机型速度
        speed = default_speed
        aircraft_upper = aircraft_type.upper()
        for model, model_speed in aircraft_speeds.items():
            if model in aircraft_upper:
                speed = model_speed
                break
        
        # 计算飞行时间（小时）
        flight_hours = distance_km / speed
        
        # 转换为小时:分钟格式
        hours = int(flight_hours)
        minutes = int((flight_hours - hours) * 60)
        
        return f"{hours}:{minutes:02d}"
    except:
        return None

def generate_realistic_flight_path(start_coords, end_coords, num_points=20):
    """
    生成更真实的飞行路径，考虑地球曲率和实际航线
    
    Args:
        start_coords: 起点坐标 [lat, lon]
        end_coords: 终点坐标 [lat, lon]
        num_points: 路径上的点数
    
    Returns:
        飞行路径点列表
    """
    import math
    
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords
    
    # 转换为弧度
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # 计算经度差
    delta_lon = lon2_rad - lon1_rad
    
    # 判断是否为跨太平洋航线（从亚洲到美洲）
    is_transpacific = False
    
    # 检查是否从亚洲（经度60-180）飞往美洲（经度-180到-60）
    if (lon1 > 60 and lon1 <= 180) and (lon2 >= -180 and lon2 < -60):
        is_transpacific = True
        # 跨太平洋航线：向东飞行，经过国际日期变更线
        if delta_lon < 0:
            delta_lon = delta_lon + 2 * math.pi  # 调整为向东飞行
    
    # 检查是否从美洲飞往亚洲
    elif (lon1 >= -180 and lon1 < -60) and (lon2 > 60 and lon2 <= 180):
        is_transpacific = True
        # 跨太平洋航线：向西飞行
        if delta_lon > 0:
            delta_lon = delta_lon - 2 * math.pi  # 调整为向西飞行
    
    # 如果经度差超过180度，选择较短的路径
    elif abs(delta_lon) > math.pi:
        if delta_lon > 0:
            delta_lon = delta_lon - 2 * math.pi
        else:
            delta_lon = delta_lon + 2 * math.pi
    
    path_points = []
    
    for i in range(num_points + 1):
        t = i / num_points
        
        if is_transpacific:
            # 跨太平洋航线：使用大圆路径，但考虑实际飞行路径
            # 计算中间点（大圆路径）
            A = math.sin((1-t) * math.acos(math.sin(lat1_rad) * math.sin(lat2_rad) + 
                                          math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))) / \
                math.sin(math.acos(math.sin(lat1_rad) * math.sin(lat2_rad) + 
                                  math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)))
            
            B = math.sin(t * math.acos(math.sin(lat1_rad) * math.sin(lat2_rad) + 
                                      math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))) / \
                math.sin(math.acos(math.sin(lat1_rad) * math.sin(lat2_rad) + 
                                  math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)))
            
            try:
                x = A * math.cos(lat1_rad) * math.cos(lon1_rad) + B * math.cos(lat2_rad) * math.cos(lon2_rad)
                y = A * math.cos(lat1_rad) * math.sin(lon1_rad) + B * math.cos(lat2_rad) * math.sin(lon2_rad)
                z = A * math.sin(lat1_rad) + B * math.sin(lat2_rad)
                
                lat = math.atan2(z, math.sqrt(x*x + y*y))
                lon = math.atan2(y, x)
                
                # 转换回度数
                lat_deg = math.degrees(lat)
                lon_deg = math.degrees(lon)
                
                # 确保经度在正确范围内
                if lon_deg > 180:
                    lon_deg -= 360
                elif lon_deg < -180:
                    lon_deg += 360
                    
                path_points.append([lat_deg, lon_deg])
            except:
                # 如果大圆计算失败，回退到线性插值
                lat = lat1 + t * (lat2 - lat1)
                lon = lon1 + t * delta_lon / math.pi * 180
                
                # 处理跨越国际日期变更线的情况
                if lon > 180:
                    lon -= 360
                elif lon < -180:
                    lon += 360
                    
                path_points.append([lat, lon])
        else:
            # 普通航线：使用线性插值
            lat = lat1 + t * (lat2 - lat1)
            lon = lon1 + t * delta_lon / math.pi * 180
            
            path_points.append([lat, lon])
    
    return path_points

def generate_straight_path(start_coords, end_coords, num_points=10):
    """
    生成两点间的直线路径（保留原函数作为备用）
    
    Args:
        start_coords: 起点坐标 [lat, lon]
        end_coords: 终点坐标 [lat, lon]
        num_points: 直线上的点数
    
    Returns:
        直线路径点列表
    """
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords
    
    # 生成直线路径
    path_points = []
    for i in range(num_points + 1):
        t = i / num_points
        
        # 线性插值公式
        lat = lat1 + t * (lat2 - lat1)
        lon = lon1 + t * (lon2 - lon1)
        
        path_points.append([lat, lon])
    
    return path_points

# 页面配置
st.set_page_config(
    page_title="航线可视化工具", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 优化页面布局
st.markdown("""
<style>
    /* 减少主容器的边距 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: none;
    }
    
    /* 优化侧边栏 */
    .sidebar .sidebar-content {
        padding-top: 1rem;
    }
    
    /* 减少标题间距 */
    h1, h2, h3 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* 优化地图容器 */
    .stContainer > div {
        gap: 0.5rem;
    }
    
    /* 减少分隔线边距 */
    hr {
        margin: 0.5rem 0;
    }
    
    /* 减少地图和后续内容之间的间距 */
    iframe[title="streamlit_folium.st_folium"] {
        margin-bottom: 0 !important;
    }
    
    /* 减少组件之间的垂直间距 */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* 特别优化导出功能标题的上边距 */
    .element-container:has(h2:contains("导出功能")) {
        margin-top: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# 主标题
st.title("✈️ 航线可视化工具")
st.markdown("---")

# 侧边栏 - 资源管理
st.sidebar.header("🔧 资源管理")

# 本地Leaflet资源管理
with st.sidebar.expander("📦 本地Leaflet资源", expanded=False):
    resource_info = resource_manager.get_resource_info()
    
    st.write(f"**版本**: {resource_info['leaflet_version']}")
    st.write(f"**状态**: {'✅ 可用' if resource_info['resources_available'] else '❌ 不可用'}")
    
    if st.button("📥 下载Leaflet资源", key="download_leaflet"):
        with st.spinner("正在下载资源..."):
            success = resource_manager.download_leaflet_resources()
            if success:
                st.balloons()
    
    # 显示文件状态
    if st.checkbox("显示详细状态", key="show_resource_details"):
        st.write("**文件状态**:")
        for filename, status in resource_info['files_status'].items():
            icon = "✅" if status['exists'] else "❌"
            size_info = f" ({status['size']} bytes)" if status['exists'] else ""
            st.write(f"{icon} {filename}{size_info}")
    
    # 注入本地资源
    if resource_manager.check_resources_available():
        if st.button("🔄 加载本地资源", key="inject_resources"):
            resource_manager.inject_local_resources()

st.sidebar.divider()

# 侧边栏 - 文件上传
st.sidebar.header("📁 数据上传")
uploaded_files = st.sidebar.file_uploader(
    "选择一个或多个航司数据文件（Excel/CSV）", 
    type=["xlsx", "csv"], 
    accept_multiple_files=True
)

# 默认数据文件夹
default_folder = r"D:\flight_tool\data"
if not os.path.exists(default_folder):
    os.makedirs(default_folder)

# 获取默认文件列表
default_files = []
if os.path.exists(default_folder):
    default_files = [
        os.path.join(default_folder, f) 
        for f in os.listdir(default_folder) 
        if f.endswith(('.xlsx', '.csv'))
    ]

# 处理文件上传
files_to_load = []
if uploaded_files:
    # 保存上传的文件到临时位置
    for file in uploaded_files:
        temp_path = os.path.join(default_folder, file.name)
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())
        files_to_load.append(temp_path)
    st.sidebar.success(f"已上传 {len(uploaded_files)} 个文件")
else:
    files_to_load = default_files
    if default_files:
        st.sidebar.info(f"使用默认数据文件 ({len(default_files)} 个)")
    else:
        st.sidebar.warning("请上传数据文件或在 data 文件夹中放置文件")

# 数据处理选项
st.sidebar.subheader("📊 数据处理选项")
enable_deduplication = st.sidebar.checkbox(
    "启用数据去重", 
    value=False,  # 默认不去重，显示原始1198条记录
    help="取消勾选将显示原始记录数（1,198条），勾选后将去除重复记录"
)

# 加载数据
if files_to_load:
    try:
        with st.spinner("正在加载数据..."):
            # 检查是否有大陆航司全货机航线.xlsx文件
            excel_file = None
            for file_path in files_to_load:
                if '大陆航司全货机航线.xlsx' in file_path or '大陆航司全货机航线' in os.path.basename(file_path):
                    excel_file = file_path
                    break
            
            if excel_file:
                # 使用专用解析函数处理Excel文件
                from fix_parser import parse_excel_route_data
                routes_df = parse_excel_route_data(excel_file)
                
                # 转换为标准格式
                if not routes_df.empty:
                    # 重命名列以匹配系统期望的格式
                    routes_df = routes_df.rename(columns={
                        'reg': 'registration',
                        'aircraft': 'aircraft',
                        'age': 'age',
                        'remarks': 'special'
                    })
                    
                    # 添加缺失的列
                    if 'flight_number' not in routes_df.columns:
                        routes_df['flight_number'] = ''
                    if 'frequency' not in routes_df.columns:
                        routes_df['frequency'] = '正常运营'
                    if 'flight_time' not in routes_df.columns:
                        routes_df['flight_time'] = ''
                    if 'flight_distance' not in routes_df.columns:
                        routes_df['flight_distance'] = ''
                    
                    # 重要：对Excel数据也进行清理，添加城市分类字段
                    routes_df = clean_route_data(routes_df, enable_deduplication=enable_deduplication)
                    
                    # 设置成功加载的文件信息
                    routes_df.attrs['successfully_loaded_files'] = [os.path.basename(excel_file)]
                    
                    st.success(f"成功解析Excel文件，共 {len(routes_df)} 条航线记录")
                else:
                    st.error("Excel文件解析失败或无有效航线数据")
                    routes_df = pd.DataFrame()
            else:
                # 使用原有的加载逻辑
                routes_df = load_data(files_to_load)
                # 清理数据
                routes_df = clean_route_data(routes_df, enable_deduplication=enable_deduplication)
            
            if not routes_df.empty:
                print_data_summary(routes_df)
        
        if not routes_df.empty:
            # 补充缺失的飞行距离和时间数据
            with st.spinner("正在计算飞行距离和时间..."):
                for idx, row in routes_df.iterrows():
                    # 获取起点和终点坐标
                    origin_coords = get_airport_coords(row['origin'])
                    dest_coords = get_airport_coords(row['destination'])
                    
                    # 只有当两个坐标都存在时才计算距离
                    if origin_coords and dest_coords:
                        # 如果飞行距离为空，计算距离
                        if pd.isna(row['flight_distance']) or str(row['flight_distance']).strip() == '':
                            distance = calculate_flight_distance(origin_coords, dest_coords)
                            if distance:
                                routes_df.at[idx, 'flight_distance'] = f"{int(distance)}公里"
                    else:
                        # 记录缺失坐标的城市
                        if not origin_coords:
                            print(f"缺失起点坐标: {row['origin']}")
                        if not dest_coords:
                            print(f"缺失终点坐标: {row['destination']}")
                    
                    # 如果飞行时间为空，计算时间
                    if pd.isna(row['flight_time']) or str(row['flight_time']).strip() == '':
                        # 提取距离数值用于计算时间
                        distance_km = None
                        distance_str = str(routes_df.at[idx, 'flight_distance'])
                        if '公里' in distance_str:
                            try:
                                distance_km = float(distance_str.replace('公里', '').strip())
                            except:
                                pass
                        elif distance_str.replace('.', '').isdigit():
                            try:
                                distance_km = float(distance_str)
                            except:
                                pass
                        
                        if distance_km:
                            flight_time = calculate_flight_time(distance_km, row['aircraft'])
                            if flight_time:
                                routes_df.at[idx, 'flight_time'] = flight_time
            
            st.sidebar.success(f"成功加载 {len(routes_df)} 条航线记录")
            
            # 显示数据统计信息
            successfully_loaded_files = routes_df.attrs.get('successfully_loaded_files', [])
            if len(successfully_loaded_files) > 1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📁 有效数据源", len(successfully_loaded_files))
                with col2:
                    st.metric("✈️ 航司数量", len(routes_df['airline'].unique()))
                with col3:
                    st.metric("📊 航线记录", len(routes_df))
                
                # 显示各航司数据分布
                with st.expander("📈 数据源分布", expanded=False):
                    # 显示成功加载的文件
                    st.write("**成功加载的数据源：**")
                    for file_name in successfully_loaded_files:
                        st.write(f"✅ {file_name}")
                    
                    # 显示跳过的文件（如果有）
                    all_uploaded_files = [os.path.basename(f) for f in files_to_load]
                    skipped_files = [f for f in all_uploaded_files if f not in successfully_loaded_files]
                    if skipped_files:
                        st.write("**跳过的文件：**")
                        for file_name in skipped_files:
                            st.write(f"⚠️ {file_name} (无法读取)")
                    
                    st.divider()
                    
                    airline_counts = routes_df['airline'].value_counts()
                    st.bar_chart(airline_counts)
                    
                    # 显示详细统计
                    st.write("**各航司记录数量：**")
                    for airline, count in airline_counts.items():
                        st.write(f"• {airline}: {count} 条记录")
            
            # 侧边栏 - 视图模式选择
            st.sidebar.header("👁️ 视图模式")
            view_mode = st.sidebar.radio(
                "选择视图模式",
                ["标准视图", "往返航线视图"],
                help="标准视图：显示所有航线\n往返航线视图：将出口和进口航线配对显示"
            )
            
            # 侧边栏 - 筛选条件
            st.sidebar.header("🔍 筛选条件")
            
            # 航司筛选
            airlines = sorted(routes_df["airline"].dropna().unique())
            airline = st.sidebar.selectbox("航司", ["全部"] + airlines)
            
            # 始发地筛选 - 按国内外分类
            st.sidebar.subheader("始发地")
            origins_sorted = get_sorted_cities(routes_df, 'origin')
            domestic_origins = [city for city in origins_sorted if categorize_city(city) == '国内']
            international_origins = [city for city in origins_sorted if categorize_city(city) == '国际']
            
            origin_options = ['全部']
            if domestic_origins:
                origin_options.append('--- 国内城市 ---')
                origin_options.extend(domestic_origins)
            if international_origins:
                origin_options.append('--- 国际城市 ---')
                origin_options.extend(international_origins)
            
            origin = st.sidebar.selectbox("选择始发地", origin_options)
            if origin.startswith('---'):
                origin = '全部'
            
            # 目的地筛选 - 按国内外分类
            st.sidebar.subheader("目的地")
            destinations_sorted = get_sorted_cities(routes_df, 'destination')
            domestic_destinations = [city for city in destinations_sorted if categorize_city(city) == '国内']
            international_destinations = [city for city in destinations_sorted if categorize_city(city) == '国际']
            
            destination_options = ['全部']
            if domestic_destinations:
                destination_options.append('--- 国内城市 ---')
                destination_options.extend(domestic_destinations)
            if international_destinations:
                destination_options.append('--- 国际城市 ---')
                destination_options.extend(international_destinations)
            
            destination = st.sidebar.selectbox("选择目的地", destination_options)
            if destination.startswith('---'):
                destination = '全部'
            
            # 机型筛选
            aircrafts = sorted(routes_df["aircraft"].dropna().unique())
            aircraft = st.sidebar.selectbox("机型", ["全部"] + aircrafts)
            
            # 方向筛选
            direction = st.sidebar.radio("方向", ["全部", "出口", "进口"])
            
            # 航线类型筛选（国内/国际）
            route_type = st.sidebar.radio("航线类型", ["全部", "国内航线", "国际航线"])
            
            # 高级筛选：进出口 + 航线类型组合
            st.sidebar.subheader("🔍 高级筛选")
            advanced_filter = st.sidebar.selectbox(
                "进出口 + 航线类型组合",
                [
                    "全部",
                    "国际出口航线",  # 国内到国外
                    "国际进口航线",  # 国外到国内
                    "国内出口航线",  # 国内到国内（出口标记）
                    "国际中转航线"   # 国外到国外
                ]
            )
            
            # 应用筛选条件
            filtered = routes_df.copy()
            if airline != "全部":
                filtered = filtered[filtered["airline"] == airline]
            if origin != "全部":
                filtered = filtered[filtered["origin"] == origin]
            if destination != "全部":
                filtered = filtered[filtered["destination"] == destination]
            if aircraft != "全部":
                filtered = filtered[filtered["aircraft"] == aircraft]
            if direction != "全部":
                filtered = filtered[filtered["direction"] == direction]
            
            # 应用航线类型筛选
            if route_type != "全部":
                if route_type == "国内航线":
                    # 筛选国内航线（起点和终点都是国内城市）
                    filtered = filtered[
                        (filtered["origin_category"] == "国内") & 
                        (filtered["destination_category"] == "国内")
                    ]
                elif route_type == "国际航线":
                    # 筛选国际航线（起点或终点至少有一个是国际城市）
                    filtered = filtered[
                        (filtered["origin_category"] == "国际") | 
                        (filtered["destination_category"] == "国际")
                    ]
            
            # 应用高级筛选条件
            if advanced_filter != "全部":
                if advanced_filter == "国际出口航线":
                    # 国内到国外的出口航线
                    filtered = filtered[
                        (filtered["origin_category"] == "国内") & 
                        (filtered["destination_category"] == "国际") &
                        (filtered["direction"] == "出口")
                    ]
                elif advanced_filter == "国际进口航线":
                    # 国外到国内的进口航线
                    filtered = filtered[
                        (filtered["origin_category"] == "国际") & 
                        (filtered["destination_category"] == "国内") &
                        (filtered["direction"] == "进口")
                    ]
                elif advanced_filter == "国内出口航线":
                    # 国内到国内的航线
                    filtered = filtered[
                        (filtered["origin_category"] == "国内") & 
                        (filtered["destination_category"] == "国内") &
                        (filtered["direction"] == "出口")
                    ]
                elif advanced_filter == "国际中转航线":
                    # 国外到国外的航线
                    filtered = filtered[
                        (filtered["origin_category"] == "国际") & 
                        (filtered["destination_category"] == "国际")
                    ]
            
            # 处理往返航线视图
            if view_mode == "往返航线视图":
                # 创建往返航线配对
                round_trip_pairs = []
                route_pairs_dict = {}
                
                # 按航线对分组
                for _, row in filtered.iterrows():
                    origin = row['origin']
                    destination = row['destination']
                    direction = row['direction']
                    
                    # 创建航线对的键（不区分方向）
                    route_key = tuple(sorted([origin, destination]))
                    
                    if route_key not in route_pairs_dict:
                        route_pairs_dict[route_key] = {'出口': [], '进口': []}
                    
                    # 根据实际的起点终点和方向来分类
                    if direction == '出口':
                        route_pairs_dict[route_key]['出口'].append(row)
                    else:
                        route_pairs_dict[route_key]['进口'].append(row)
                
                # 创建往返航线对
                for route_key, directions in route_pairs_dict.items():
                    city1, city2 = route_key
                    export_routes = directions['出口']
                    import_routes = directions['进口']
                    
                    if export_routes or import_routes:
                        round_trip_pairs.append({
                            'city_pair': f"{city1} ↔ {city2}",
                            'export_routes': export_routes,
                            'import_routes': import_routes,
                            'total_routes': len(export_routes) + len(import_routes),
                            'has_both_directions': len(export_routes) > 0 and len(import_routes) > 0
                        })
                
                # 按总航线数排序
                round_trip_pairs.sort(key=lambda x: x['total_routes'], reverse=True)
                
                # 更新filtered为往返航线视图的数据
                filtered_for_display = []
                for pair in round_trip_pairs:
                    filtered_for_display.extend(pair['export_routes'])
                    filtered_for_display.extend(pair['import_routes'])
                
                # 转换为DataFrame
                if filtered_for_display:
                    filtered = pd.DataFrame(filtered_for_display)
                else:
                    filtered = pd.DataFrame()
            
            # 显示筛选结果统计
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总航线数", len(routes_df))
            with col2:
                st.metric("筛选后航线数", len(filtered))
            with col3:
                st.metric("涉及航司数", len(filtered["airline"].unique()) if not filtered.empty else 0)
            with col4:
                # 统计航线类型
                if not filtered.empty and "origin_category" in filtered.columns and "destination_category" in filtered.columns:
                    domestic_count = len(filtered[
                        (filtered["origin_category"] == "国内") & 
                        (filtered["destination_category"] == "国内")
                    ])
                    international_count = len(filtered[
                        (filtered["origin_category"] == "国际") | 
                        (filtered["destination_category"] == "国际")
                    ])
                    st.metric("国内/国际", f"{domestic_count}/{international_count}")
                else:
                    st.metric("国内/国际", "0/0")
            
            # 往返航线视图专门展示
            if view_mode == "往返航线视图" and 'round_trip_pairs' in locals():
                st.subheader("🔄 往返航线配对视图")
                
                if round_trip_pairs:
                    # 统计信息
                    total_pairs = len(round_trip_pairs)
                    both_directions_pairs = len([p for p in round_trip_pairs if p['has_both_directions']])
                    one_way_pairs = total_pairs - both_directions_pairs
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🔄 双向航线对", both_directions_pairs)
                    with col2:
                        st.metric("➡️ 单向航线对", one_way_pairs)
                    with col3:
                        st.metric("📊 总航线对", total_pairs)
                    
                    # 显示往返航线对列表
                    st.subheader("📋 航线对详情")
                    
                    for i, pair in enumerate(round_trip_pairs[:20]):  # 只显示前20个
                        with st.expander(f"{pair['city_pair']} ({pair['total_routes']}条航线)", expanded=False):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**🛫 出口航线**")
                                if pair['export_routes']:
                                    export_df = pd.DataFrame(pair['export_routes'])
                                    for _, route in export_df.iterrows():
                                        direction_icon = "🛫" if route['direction'] == '出口' else "🛬"
                                        st.write(f"{direction_icon} {route['origin']} → {route['destination']} ({route['airline']}, {route['aircraft']})")
                                else:
                                    st.write("❌ 无出口航线")
                            
                            with col2:
                                st.write("**🛬 进口航线**")
                                if pair['import_routes']:
                                    import_df = pd.DataFrame(pair['import_routes'])
                                    for _, route in import_df.iterrows():
                                        direction_icon = "🛫" if route['direction'] == '出口' else "🛬"
                                        st.write(f"{direction_icon} {route['origin']} → {route['destination']} ({route['airline']}, {route['aircraft']})")
                                else:
                                    st.write("❌ 无进口航线")
                            
                            # 显示往返状态
                            if pair['has_both_directions']:
                                st.success("✅ 完整往返航线")
                            else:
                                st.warning("⚠️ 单向航线")
                    
                    if len(round_trip_pairs) > 20:
                        st.info(f"显示前20个航线对，共{len(round_trip_pairs)}个航线对")
                else:
                    st.warning("没有找到符合条件的往返航线对")
            
            # 路径分析面板
            if not filtered.empty:
                with st.expander("🛣️ 航线路径分析", expanded=False):
                    # 分析往返航线
                    route_pairs = {}
                    city_connections = {}
                    
                    for _, row in filtered.iterrows():
                        origin, destination = row['origin'], row['destination']
                        
                        # 统计往返航线对
                        route_key = tuple(sorted([origin, destination]))
                        if route_key not in route_pairs:
                            route_pairs[route_key] = {'routes': [], 'directions': set()}
                        route_pairs[route_key]['routes'].append(row)
                        route_pairs[route_key]['directions'].add(f"{origin}→{destination}")
                        
                        # 统计城市连接
                        for city in [origin, destination]:
                            if city not in city_connections:
                                city_connections[city] = set()
                            other_city = destination if city == origin else origin
                            city_connections[city].add(other_city)
                    
                    # 显示往返航线统计
                    round_trip_pairs = [(pair, data) for pair, data in route_pairs.items() if len(data['directions']) >= 2]
                    one_way_pairs = [(pair, data) for pair, data in route_pairs.items() if len(data['directions']) == 1]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🔄 往返航线对", len(round_trip_pairs))
                    with col2:
                        st.metric("➡️ 单向航线", len(one_way_pairs))
                    with col3:
                        st.metric("🏢 涉及城市", len(city_connections))
                    
                    # 显示主要中转枢纽
                    st.subheader("🏢 主要中转枢纽")
                    hub_analysis = [(city, len(connections)) for city, connections in city_connections.items() if len(connections) >= 3]
                    hub_analysis.sort(key=lambda x: x[1], reverse=True)
                    
                    if hub_analysis:
                        for i, (city, count) in enumerate(hub_analysis[:8]):
                            if count >= 8:
                                hub_type = "🌟 超级枢纽"
                                color = "red"
                            elif count >= 5:
                                hub_type = "🏢 主要枢纽"
                                color = "orange"
                            else:
                                hub_type = "📍 区域枢纽"
                                color = "blue"
                            
                            # 获取连接的城市列表
                            connected_cities = list(city_connections[city])[:5]
                            cities_text = ", ".join(connected_cities)
                            if len(city_connections[city]) > 5:
                                cities_text += f" 等{len(city_connections[city])}个城市"
                            
                            st.markdown(f"**:{color}[{hub_type}]** {city} ({count}条航线)")
                            st.caption(f"连接: {cities_text}")
                    else:
                        st.info("当前筛选条件下暂无主要中转枢纽")
                    
                    # 显示往返航线详情
                    if round_trip_pairs:
                        st.subheader("🔄 往返航线详情")
                        for (city1, city2), data in round_trip_pairs[:10]:  # 只显示前10个
                            directions = list(data['directions'])
                            airlines = set([route['airline'] for route in data['routes']])
                            st.markdown(f"**{city1} ⇄ {city2}**")
                            st.caption(f"方向: {' | '.join(directions)} | 航司: {', '.join(airlines)}")
            
            # 地图可视化
            st.header("🗺️ 航线地图")
            
            if not filtered.empty:
                # 创建地图（使用美观明亮的瓦片源，强制刷新）
                import time
                map_key = f"map_{int(time.time())}"  # 添加时间戳强制刷新
                
                m = folium.Map(
                    location=[20.0, 0.0],  # 以0度经线为中心，确保美洲在西半球正确显示
                    zoom_start=2,  # 降低初始缩放级别以显示完整世界地图
                    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',  # 使用新的稳定CartoDB URL
                    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>',
                    prefer_canvas=True,  # 使用Canvas渲染，减少闪烁
                    max_bounds=True,  # 限制地图边界
                    min_zoom=1,  # 最小缩放级别
                    max_zoom=18,  # 最大缩放级别
                    world_copy_jump=False,  # 禁用世界地图重复显示
                    crs='EPSG3857',  # 使用Web墨卡托投影，确保正确的大洲位置
                    width='100%',  # 地图宽度设置为100%
                    height='800px'  # 地图高度设置为800像素
                )
                
                # 设置地图显示边界，确保美洲在西半球，亚洲在东半球
                m.fit_bounds([[-60, -180], [75, 180]])  # 调整边界范围，确保大洲位置正确
                
                # 添加美观的备用瓦片源（使用稳定的新URL）
                folium.TileLayer(
                    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
                    attr='&copy; <a href="https://carto.com/attributions">CARTO</a>',
                    name='简洁白色',
                    overlay=False,
                    control=True
                ).add_to(m)
                
                folium.TileLayer(
                    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
                    attr='&copy; <a href="https://carto.com/attributions">CARTO</a>',
                    name='深色主题',
                    overlay=False,
                    control=True
                ).add_to(m)
                
                # 添加卫星图作为备用
                folium.TileLayer(
                    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                    name='卫星图',
                    overlay=False,
                    control=True
                ).add_to(m)
                
                # 注释：为避免网络连接错误，暂时移除外部地理边界数据加载
                # 如需要边界显示，可在网络稳定时重新启用
                
                # 创建基础图层组
                base_layer = folium.FeatureGroup(name='航线图层', show=True)
                base_layer.add_to(m)
                # 添加指南针和方向控件
                from folium.plugins import MiniMap
                
                # 添加小地图（显示当前位置）- 使用稳定瓦片源
                minimap = MiniMap(
                    tile_layer=folium.TileLayer(
                        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
                        attr='&copy; CARTO'
                    ),
                    position='bottomright',
                    width=150,
                    height=150,
                    collapsed_width=25,
                    collapsed_height=25,
                    zoom_level_offset=-5,
                    toggle_display=True
                )
                m.add_child(minimap)
                
                # 添加方向指示器（指南针）
                compass_html = """
                <div id="compass" style="
                    position: fixed;
                    top: 80px;
                    right: 10px;
                    width: 80px;
                    height: 80px;
                    background: rgba(255, 255, 255, 0.9);
                    border: 2px solid #333;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-family: Arial, sans-serif;
                    font-weight: bold;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                    z-index: 1000;
                ">
                    <div style="
                        position: relative;
                        width: 60px;
                        height: 60px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <!-- 北 -->
                        <div style="
                            position: absolute;
                            top: 2px;
                            left: 50%;
                            transform: translateX(-50%);
                            color: #d32f2f;
                            font-size: 12px;
                            font-weight: bold;
                        ">N</div>
                        <!-- 南 -->
                        <div style="
                            position: absolute;
                            bottom: 2px;
                            left: 50%;
                            transform: translateX(-50%);
                            color: #333;
                            font-size: 12px;
                        ">S</div>
                        <!-- 东 -->
                        <div style="
                            position: absolute;
                            right: 2px;
                            top: 50%;
                            transform: translateY(-50%);
                            color: #333;
                            font-size: 12px;
                        ">E</div>
                        <!-- 西 -->
                        <div style="
                            position: absolute;
                            left: 2px;
                            top: 50%;
                            transform: translateY(-50%);
                            color: #333;
                            font-size: 12px;
                        ">W</div>
                        <!-- 指针 -->
                        <div style="
                            width: 2px;
                            height: 20px;
                            background: linear-gradient(to bottom, #d32f2f 0%, #d32f2f 60%, #333 60%, #333 100%);
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                        "></div>
                    </div>
                </div>
                """
                
                m.get_root().html.add_child(folium.Element(compass_html))
                
                # 添加图层控制器
                folium.LayerControl().add_to(m)
                
                # 收集所有机场位置和航线统计
                airports = {}
                route_stats = {}  # 统计每条航线的航班数量
                
                # 定义航司颜色方案（使用更丰富的调色板）
                airline_colors = {
                    '顺丰航空': '#FF6B35',  # 橙红色
                    '中国邮政': '#2E8B57',  # 海绿色
                    '圆通航空': '#4169E1',  # 皇家蓝
                    '中通快递': '#8A2BE2',  # 蓝紫色
                    '申通快递': '#DC143C',  # 深红色
                    '韵达快递': '#FF1493',  # 深粉色
                    '德邦快递': '#32CD32',  # 酸橙绿
                    '京东物流': '#FF4500',  # 橙红色
                    '菜鸟网络': '#1E90FF',  # 道奇蓝
                    '中国国航': '#B22222',  # 火砖红
                    '东方航空': '#4682B4',  # 钢蓝色
                    '南方航空': '#228B22',  # 森林绿
                    '海南航空': '#FF69B4',  # 热粉色
                    '厦门航空': '#20B2AA',  # 浅海绿
                    '深圳航空': '#9370DB',  # 中紫色
                    '山东航空': '#CD853F',  # 秘鲁色
                    '四川航空': '#FF8C00',  # 深橙色
                    '吉祥航空': '#00CED1',  # 深绿松石
                    '春秋航空': '#DA70D6',  # 兰花紫
                    '华夏航空': '#87CEEB'   # 天空蓝
                }
                
                # 为未知航司生成颜色
                import hashlib
                def get_airline_color(airline_name):
                    if airline_name in airline_colors:
                        return airline_colors[airline_name]
                    # 基于航司名称生成一致的颜色
                    hash_obj = hashlib.md5(airline_name.encode())
                    hash_hex = hash_obj.hexdigest()
                    return f"#{hash_hex[:6]}"
                
                # 第一遍：统计航线频率
                for idx, row in filtered.iterrows():
                    route_key = f"{row['origin']}-{row['destination']}"
                    if route_key not in route_stats:
                        route_stats[route_key] = {'count': 0, 'airlines': set(), 'directions': set()}
                    route_stats[route_key]['count'] += 1
                    route_stats[route_key]['airlines'].add(row['airline'])
                    route_stats[route_key]['directions'].add(row.get('direction', '出口'))
                
                # 第二遍：绘制航线
                routes_added = set()
                unique_routes_displayed = 0  # 统计实际显示在地图上的唯一航线数
                routes_without_coords = 0  # 统计无坐标的航线数
                total_route_records = 0  # 统计所有航线记录数（包括重复）
                
                for idx, row in filtered.iterrows():
                    total_route_records += 1  # 统计所有航线记录
                    origin_coords = get_airport_coords(row['origin'])
                    dest_coords = get_airport_coords(row['destination'])
                    
                    # 调试信息：检查坐标获取
                    print(f"航线: {row['origin']} -> {row['destination']}")
                    print(f"起点坐标: {origin_coords}, 终点坐标: {dest_coords}")
                    
                    # 检查坐标是否有效
                    if origin_coords is None or dest_coords is None:
                        print(f"警告：无法获取坐标 - {row['origin']} 或 {row['destination']}")
                        routes_without_coords += 1
                        continue
                    
                    # 记录机场位置
                    if row['origin'] not in airports:
                        airports[row['origin']] = {'coords': origin_coords, 'type': 'origin', 'flights': []}
                    if row['destination'] not in airports:
                        airports[row['destination']] = {'coords': dest_coords, 'type': 'destination', 'flights': []}
                    
                    # 记录航班信息
                    airports[row['origin']]['flights'].append(row)
                    airports[row['destination']]['flights'].append(row)
                    
                    # 创建航线唯一标识
                    route_key = f"{row['origin']}-{row['destination']}"
                    
                    # 只绘制一次相同的航线
                    if route_key not in routes_added:
                        route_info = route_stats[route_key]
                        
                        # 判断航线类型并设置颜色
                        origin_category = categorize_city(row['origin'])
                        dest_category = categorize_city(row['destination'])
                        
                        # 根据航线进出口方向设置颜色（数据源中无纯国内航线，国内机场仅作中转地）
                        direction = row.get('direction', '出口')
                        if direction == '进口':
                            line_color = '#4CAF50'  # 绿色 - 进口
                            route_type = '🌍 国际进口'
                        else:  # 出口
                            line_color = '#FFC107'  # 黄色 - 出口
                            route_type = '🌍 国际出口'
                        
                        # 标识中转航线（经过国内机场的国际航线）
                        origin_category = categorize_city(row['origin'])
                        dest_category = categorize_city(row['destination'])
                        if origin_category == '国内' or dest_category == '国内':
                            route_type += ' (含中转)'
                        
                        # 根据航线频率调整线条粗细和透明度
                        frequency = route_info['count']
                        if frequency >= 10:
                            line_weight = 6
                            line_opacity = 0.9
                        elif frequency >= 5:
                            line_weight = 5
                            line_opacity = 0.8
                        elif frequency >= 2:
                            line_weight = 4
                            line_opacity = 0.7
                        else:
                            line_weight = 3
                            line_opacity = 0.6
                        
                        # 确定主要航司（选择该航线上最多航班的航司）
                        route_flights = filtered[(filtered['origin'] == row['origin']) & (filtered['destination'] == row['destination'])]
                        airline_counts = route_flights['airline'].value_counts().to_dict()
                        
                        main_airline = max(airline_counts.keys(), key=lambda x: airline_counts[x]) if airline_counts else row['airline']
                        
                        # 根据方向调整显示
                        if '出口' in route_info['directions'] and '进口' in route_info['directions']:
                            # 双向航线
                            direction_indicator = '⇄'
                        elif '出口' in route_info['directions']:
                            direction_indicator = '→'
                        else:
                            direction_indicator = '←'
                        
                        # 检查是否为往返航线，调整线条样式
                        reverse_route_key = f"{row['destination']}-{row['origin']}"
                        is_round_trip = reverse_route_key in route_stats
                        
                        # 为往返航线调整透明度和样式
                        if is_round_trip:
                            line_opacity = min(line_opacity + 0.1, 1.0)  # 增加透明度
                            line_weight = min(line_weight + 1, 8)  # 增加线条粗细
                        
                        # 生成直线路径
                        straight_path = generate_straight_path(origin_coords, dest_coords, num_points=10)
                        
                        # 创建详细的航线信息
                        airlines_list = list(route_info['airlines'])
                        directions_list = list(route_info['directions'])
                        
                        # 检查是否有对应的返程航线
                        reverse_route_key = f"{row['destination']}-{row['origin']}"
                        has_return_route = reverse_route_key in route_stats
                        
                        # 构建航线路径信息
                        route_path_info = ""
                        if has_return_route:
                            route_path_info = f"<p style='margin: 3px 0; padding: 3px 8px; background: #e8f5e8; border-radius: 5px; border-left: 3px solid #4caf50;'><b>🔄 往返航线:</b> {row['origin']} ⇄ {row['destination']}</p>"
                        else:
                            route_path_info = f"<p style='margin: 3px 0; padding: 3px 8px; background: #fff3e0; border-radius: 5px; border-left: 3px solid #ff9800;'><b>➡️ 单向航线:</b> {row['origin']} → {row['destination']}</p>"
                        
                        # 分析是否为中转航线（检查是否有相同起点或终点的其他航线）
                        transit_info = ""
                        same_origin_routes = filtered[filtered['origin'] == row['origin']]['destination'].unique()
                        same_dest_routes = filtered[filtered['destination'] == row['destination']]['origin'].unique()
                        
                        if len(same_origin_routes) > 1:
                            other_destinations = [dest for dest in same_origin_routes if dest != row['destination']][:3]
                            transit_info += f"<p style='margin: 3px 0; font-size: 11px; color: #666;'><b>🛫 {row['origin']} 其他航线:</b> → {', '.join(other_destinations)}{'...' if len(same_origin_routes) > 4 else ''}</p>"
                        
                        if len(same_dest_routes) > 1:
                            other_origins = [orig for orig in same_dest_routes if orig != row['origin']][:3]
                            transit_info += f"<p style='margin: 3px 0; font-size: 11px; color: #666;'><b>🛬 {row['destination']} 其他航线:</b> {', '.join(other_origins)}{'...' if len(same_dest_routes) > 4 else ''} →</p>"
                        
                        popup_content = f"""
                        <div style='width: 350px; font-family: Arial, sans-serif; line-height: 1.4;'>
                            <h3 style='margin: 0; color: {line_color}; border-bottom: 2px solid {line_color}; padding-bottom: 5px;'>
                                ✈️ {row['origin']} {direction_indicator} {row['destination']}
                            </h3>
                            <div style='margin: 10px 0;'>
                                <div style='margin: 3px 0; padding: 3px 8px; background: {line_color}20; border-radius: 5px; border-left: 3px solid {line_color};'>
                                    <strong>{route_type}</strong>
                                </div>
                                {route_path_info}
                                <p style='margin: 3px 0;'><b>🏢 主要航司:</b> <span style='color: {line_color};'>{main_airline}</span></p>
                                <p style='margin: 3px 0;'><b>📊 航班频次:</b> <span style='background: {line_color}; color: white; padding: 2px 6px; border-radius: 3px;'>{frequency} 班</span></p>
                                <p style='margin: 3px 0;'><b>🔄 运营方向:</b> {' + '.join(directions_list)}</p>
                                <p style='margin: 3px 0;'><b>🛫 服务航司:</b> {', '.join(airlines_list[:3])}{'...' if len(airlines_list) > 3 else ''}</p>
                                <p style='margin: 3px 0;'><b>✈️ 机型:</b> {row['aircraft']}</p>
                                {transit_info}
                            </div>
                        </div>
                        """
                        
                        # 添加航线（优化渲染，减少闪烁）
                        if frequency >= 5:  # 提高动画阈值，减少动画航线数量
                            # 高频航线使用动态效果
                            try:
                                from folium.plugins import AntPath
                                AntPath(
                                    locations=straight_path,
                                    color=line_color,
                                    weight=line_weight,
                                    opacity=line_opacity * 0.6,  # 进一步降低透明度
                                    delay=2000,  # 大幅减慢动画速度
                                    dash_array=[15, 25],  # 优化虚线间距
                                    pulse_color=line_color,  # 使用相同颜色减少对比
                                    popup=folium.Popup(popup_content, max_width=350),
                                    tooltip=f"{route_type} - {row['origin']} → {row['destination']} ({frequency}班)"
                                ).add_to(m)
                            except ImportError:
                                # 回退到静态线条
                                folium.PolyLine(
                                    locations=straight_path,
                                    color=line_color,
                                    weight=line_weight,
                                    opacity=line_opacity,
                                    smooth_factor=1.0,
                                    popup=folium.Popup(popup_content, max_width=350),
                                    tooltip=f"{route_type} - {row['origin']} → {row['destination']} ({frequency}班)"
                                ).add_to(m)
                        else:
                            # 中低频航线使用静态线条（减少视觉干扰）
                            folium.PolyLine(
                                locations=straight_path,
                                color=line_color,
                                weight=max(1, line_weight - 1),  # 稍微减小线条粗细
                                opacity=line_opacity * 0.5,  # 进一步降低透明度
                                smooth_factor=2.0,  # 增加平滑度
                                popup=folium.Popup(popup_content, max_width=350),
                                tooltip=f"{route_type} - {row['origin']} → {row['destination']} ({frequency}班)"
                            ).add_to(m)
                        
                        # 为超高频航线添加动态脉冲标记（减少闪烁）
                        if frequency >= 8:  # 进一步提高脉冲阈值
                            mid_lat = (origin_coords[0] + dest_coords[0]) / 2
                            mid_lon = (origin_coords[1] + dest_coords[1]) / 2
                            
                            # 添加优化的脉冲动画效果
                            pulse_html = f"""
                            <div style="
                                width: {max(4, min(12, frequency // 2))}px;
                                height: {max(4, min(12, frequency // 2))}px;
                                background-color: {line_color};
                                border-radius: 50%;
                                animation: pulse 4s infinite ease-in-out;
                                opacity: 0.8;
                            ">
                            </div>
                            <style>
                            @keyframes pulse {{
                                0% {{
                                    transform: scale(0.8);
                                    opacity: 0.8;
                                }}
                                50% {{
                                    transform: scale(1.1);
                                    opacity: 0.4;
                                }}
                                100% {{
                                    transform: scale(0.8);
                                    opacity: 0.8;
                                }}
                            }}
                            </style>
                            """
                            
                            folium.Marker(
                                location=[mid_lat, mid_lon],
                                popup=f"高频航线: {frequency}班",
                                tooltip=f"🔥 {frequency}班",
                                icon=folium.DivIcon(
                                    html=pulse_html,
                                    icon_size=(max(6, min(16, frequency)), max(6, min(16, frequency))),
                                    icon_anchor=(max(3, min(8, frequency)), max(3, min(8, frequency)))
                                )
                            ).add_to(m)
                        
                        routes_added.add(route_key)
                        unique_routes_displayed += 1  # 统计实际显示的唯一航线
                
                # 创建航线类型图例
                legend_html = """
                <div style="position: fixed; 
                           top: 10px; right: 10px; width: 240px; height: auto;
                           background-color: white; border:2px solid grey; z-index:9999; 
                           font-size:12px; padding: 12px; border-radius: 8px;
                           box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                    <h4 style="margin: 0 0 12px 0; text-align: center; color: #333; font-size: 14px;">🗺️ 航线图例</h4>
                    
                    <!-- 航线类型图例 -->
                    <div style="margin-bottom: 12px;">
                        <div style="margin: 6px 0; display: flex; align-items: center;">
                            <div style="width: 20px; height: 4px; background-color: #4CAF50; 
                                       border-radius: 2px; margin-right: 10px;"></div>
                            <span style="font-size: 12px; color: #333; font-weight: 500;">🌍 国际进口</span>
                        </div>
                        <div style="margin: 6px 0; display: flex; align-items: center;">
                            <div style="width: 20px; height: 4px; background-color: #FFC107; 
                                       border-radius: 2px; margin-right: 10px;"></div>
                            <span style="font-size: 12px; color: #333; font-weight: 500;">🌍 国际出口</span>
                        </div>
                        <div style="margin: 6px 0; font-size: 11px; color: #666; padding: 5px; background: #f5f5f5; border-radius: 3px;">
                            💡 国内机场作为中转地，无纯国内航线
                        </div>
                    </div>
                    
                    <hr style="margin: 10px 0; border: none; border-top: 1px solid #ddd;">
                    
                    <!-- 地理边界图例 -->
                    <div style="margin-bottom: 12px;">
                        <h5 style="margin: 5px 0; color: #333; font-size: 12px;">🌏 地理边界</h5>
                        <div style="margin: 6px 0; font-size: 10px; color: #666; padding: 4px; background: #f0f8ff; border-radius: 3px;">
                            🗺️ 基于OpenStreetMap地图数据
                        </div>
                    </div>
                    
                    <hr style="margin: 10px 0; border: none; border-top: 1px solid #ddd;">
                    
                    <!-- 线条说明 -->
                    <div style="font-size: 10px; color: #666; text-align: center; line-height: 1.4;">
                        💡 线条粗细表示航班频次<br>
                        🔥 圆点标记高频航线(≥5班)<br>
                        ⚡ 动态效果显示航线流向<br>
                        🔄 粗线条表示往返航线<br>
                        📍 点击航线查看中转信息
                    </div>
                """
                
                # 统计国际航线数量和路径分析（数据源中无纯国内航线）
                international_import_count = 0
                international_export_count = 0
                transit_routes_count = 0  # 经过国内机场的中转航线
                round_trip_count = 0
                transit_hubs = {}
                
                for _, route in filtered.iterrows():
                    # 所有航线都是国际航线，按进出口分类
                    direction = route.get('direction', '出口')
                    if direction == '进口':
                        international_import_count += 1
                    else:
                        international_export_count += 1
                    
                    # 统计中转航线（经过国内机场）
                    origin_category = categorize_city(route['origin'])
                    dest_category = categorize_city(route['destination'])
                    if origin_category == '国内' or dest_category == '国内':
                        transit_routes_count += 1
                    
                    # 统计往返航线
                    route_key = f"{route['origin']}-{route['destination']}"
                    reverse_key = f"{route['destination']}-{route['origin']}"
                    if reverse_key in route_stats:
                        round_trip_count += 1
                    
                    # 统计中转枢纽
                    origin = route['origin']
                    destination = route['destination']
                    
                    if origin not in transit_hubs:
                        transit_hubs[origin] = {'outbound': set(), 'inbound': set()}
                    if destination not in transit_hubs:
                        transit_hubs[destination] = {'outbound': set(), 'inbound': set()}
                    
                    transit_hubs[origin]['outbound'].add(destination)
                    transit_hubs[destination]['inbound'].add(origin)
                
                # 识别主要中转枢纽（连接3个以上城市的机场）
                major_hubs = {}
                for city, connections in transit_hubs.items():
                    total_connections = len(connections['outbound']) + len(connections['inbound'])
                    if total_connections >= 6:  # 至少6个连接才算主要枢纽
                        major_hubs[city] = {
                            'total': total_connections,
                            'outbound': len(connections['outbound']),
                            'inbound': len(connections['inbound'])
                        }
                
                # 构建中转枢纽信息
                hub_info = ""
                if major_hubs:
                    sorted_hubs = sorted(major_hubs.items(), key=lambda x: x[1]['total'], reverse=True)[:3]
                    hub_list = []
                    for hub_name, hub_data in sorted_hubs:
                        hub_list.append(f"{hub_name}({hub_data['total']}条)")
                    hub_info = f"<br>🏢 主要枢纽: {', '.join(hub_list)}"
                
                legend_html += f"""
                    <hr style="margin: 10px 0; border: none; border-top: 1px solid #ddd;">
                    <div style="font-size: 11px; color: #555; text-align: center;">
                        📊 当前显示:<br>
                        国际进口: {international_import_count} 条<br>
                        国际出口: {international_export_count} 条<br>
                        🔄 往返航线: {round_trip_count//2} 对<br>
                        🛫 含中转: {transit_routes_count} 条{hub_info}
                    </div>
                </div>"""
                
                m.get_root().html.add_child(folium.Element(legend_html))
                
                # 添加优化的机场标记
                for airport_code, airport_info in airports.items():
                    coords = airport_info['coords']
                    flights = airport_info['flights']
                    
                    # 统计该机场的航班数量和类型
                    total_flights = len(flights)
                    airlines = set([f['airline'] for f in flights])
                    aircraft_types = set([f['aircraft'] for f in flights])
                    
                    # 统计各航司在该机场的航班数
                    airline_stats = {}
                    for flight in flights:
                        airline = flight['airline']
                        airline_stats[airline] = airline_stats.get(airline, 0) + 1
                    
                    # 确定机场类型和图标
                    if total_flights >= 30:
                        airport_type = "超级枢纽"
                        icon_color = "#8B0000"  # 深红色
                        icon_size = 18
                        circle_radius = 50000
                    elif total_flights >= 20:
                        airport_type = "主要枢纽"
                        icon_color = "#FF4500"  # 橙红色
                        icon_size = 15
                        circle_radius = 35000
                    elif total_flights >= 10:
                        airport_type = "区域枢纽"
                        icon_color = "#FFD700"  # 金色
                        icon_size = 12
                        circle_radius = 25000
                    elif total_flights >= 5:
                        airport_type = "重要机场"
                        icon_color = "#4169E1"  # 皇家蓝
                        icon_size = 10
                        circle_radius = 15000
                    else:
                        airport_type = "一般机场"
                        icon_color = "#32CD32"  # 酸橙绿
                        icon_size = 8
                        circle_radius = 8000
                    
                    # 创建详细的弹出窗口HTML
                    popup_html = f"""
                    <div style="width: 320px; font-family: Arial, sans-serif; line-height: 1.4;">
                        <h3 style="margin: 0; color: {icon_color}; border-bottom: 2px solid {icon_color}; padding-bottom: 5px;">
                            🛫 {airport_code} 机场
                        </h3>
                        <div style="margin: 10px 0; background: #f8f9fa; padding: 8px; border-radius: 5px;">
                            <p style="margin: 3px 0;"><b>🏷️ 机场等级:</b> <span style="color: {icon_color}; font-weight: bold;">{airport_type}</span></p>
                            <p style="margin: 3px 0;"><b>📊 航班总数:</b> <span style="background: {icon_color}; color: white; padding: 1px 5px; border-radius: 3px;">{total_flights} 班</span></p>
                            <p style="margin: 3px 0;"><b>🏢 服务航司:</b> {len(airlines)} 家</p>
                            <p style="margin: 3px 0;"><b>✈️ 机型种类:</b> {len(aircraft_types)} 种</p>
                        </div>
                        <div style="margin: 10px 0;">
                            <h4 style="margin: 5px 0; color: #666; font-size: 13px;">📈 航司分布:</h4>
                    """
                    
                    # 添加航司统计（按航班数排序）
                    sorted_airlines = sorted(airline_stats.items(), key=lambda x: x[1], reverse=True)
                    for airline, count in sorted_airlines[:5]:  # 只显示前5个航司
                        color = get_airline_color(airline)
                        percentage = (count / total_flights) * 100
                        popup_html += f"""
                            <div style="margin: 2px 0; display: flex; align-items: center;">
                                <div style="width: 12px; height: 12px; background-color: {color}; 
                                           border-radius: 2px; margin-right: 6px;"></div>
                                <span style="font-size: 11px;">{airline}: {count}班 ({percentage:.1f}%)</span>
                            </div>
                        """
                    
                    if len(sorted_airlines) > 5:
                        popup_html += f"<div style='font-size: 10px; color: #888; margin-top: 3px;'>...还有{len(sorted_airlines)-5}家航司</div>"
                    
                    popup_html += """
                        </div>
                    </div>
                    """
                    
                    # 创建自定义图标
                    icon_html = f"""
                    <div style="
                        background: linear-gradient(135deg, {icon_color}, {icon_color}dd);
                        border: 2px solid white;
                        border-radius: 50%;
                        width: {icon_size}px;
                        height: {icon_size}px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: {max(8, icon_size-6)}px;
                        color: white;
                        font-weight: bold;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
                    ">{airport_code[:2]}</div>
                    """
                    
                    # 添加机场标记
                    folium.Marker(
                        location=coords,
                        popup=folium.Popup(popup_html, max_width=370),
                        tooltip=f"{airport_code} - {airport_type} ({total_flights}班)",
                        icon=folium.DivIcon(
                            html=icon_html,
                            icon_size=(icon_size, icon_size),
                            icon_anchor=(icon_size//2, icon_size//2)
                        )
                    ).add_to(m)
                    
                    # 为重要机场添加影响范围圆圈
                    if total_flights >= 10:
                        folium.Circle(
                            location=coords,
                            radius=circle_radius,
                            color=icon_color,
                            fillColor=icon_color,
                            fillOpacity=0.08,
                            weight=1,
                            opacity=0.3,
                            popup=f"{airport_code} 服务范围",
                            tooltip=f"📍 {airport_code} 影响区域"
                        ).add_to(m)
                
                # 显示地图 - 使用更大的尺寸和全宽度，强制刷新
                map_output = st_folium(m, width=1400, height=800, returned_objects=["last_object_clicked"], key=map_key)
                
                # 显示坐标统计信息
                if 'unique_routes_displayed' in locals() and 'routes_without_coords' in locals():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.info(f"🗺️ 地图显示航线: {unique_routes_displayed} 条")
                    with col2:
                        st.warning(f"⚠️ 缺失坐标航线: {routes_without_coords} 条")
                    with col3:
                        st.success(f"📊 总航线记录: {total_route_records} 条")
                    with col4:
                        st.metric("去重率", f"{unique_routes_displayed}/{total_route_records - routes_without_coords}")
                    
                    if routes_without_coords > 0:
                        st.caption("💡 提示：缺失坐标的航线仍包含在数据统计中，但无法在地图上显示")
                    
                    if total_route_records > unique_routes_displayed + routes_without_coords:
                        st.caption(f"📋 说明：总记录数包含重复航线，地图仅显示 {unique_routes_displayed} 条唯一航线路径")
                
                # 减少地图和导出功能之间的间距
                st.markdown("<div style='margin-top: -1rem; margin-bottom: -1rem;'></div>", unsafe_allow_html=True)
                
                # 导出功能
                st.header("📤 导出功能")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📄 导出当前地图为 HTML", type="primary"):
                        export_path = "D:/flight_tool/exported_map.html"
                        m.save(export_path)
                        st.success(f"地图已导出到: {export_path}")
                        st.balloons()
                
                with col2:
                    if st.button("📊 导出筛选数据为 Excel"):
                        export_path = "D:/flight_tool/filtered_data.xlsx"
                        filtered.to_excel(export_path, index=False)
                        st.success(f"数据已导出到: {export_path}")
                
                # 减少导出功能和数据表格之间的间距
                st.markdown("<div style='margin-top: -1rem; margin-bottom: -0.5rem;'></div>", unsafe_allow_html=True)
                
                # 数据表格预览 - 默认展开并优化显示
                with st.expander("📋 查看筛选后的数据详情", expanded=True):
                    # 添加航线类型列用于显示
                    display_df = filtered.copy()
                    
                    # 添加航线类型分类
                    if "origin_category" in display_df.columns and "destination_category" in display_df.columns:
                        def classify_route_type(row):
                            origin_cat = row['origin_category']
                            dest_cat = row['destination_category']
                            
                            # 如果任一分类为'未知'，则显示为'未分类'
                            if origin_cat == '未知' or dest_cat == '未知':
                                return '未分类'
                            # 如果都是国内，则为国内航线
                            elif origin_cat == '国内' and dest_cat == '国内':
                                return '国内航线'
                            # 如果至少有一个是国际，则为国际航线
                            elif origin_cat == '国际' or dest_cat == '国际':
                                return '国际航线'
                            else:
                                return '未分类'
                        
                        display_df['航线类型'] = display_df.apply(classify_route_type, axis=1)
                    else:
                        display_df['航线类型'] = '未分类'
                    
                    # 添加进出口类型显示
                    display_df['进出口类型'] = display_df['direction'].map({
                        '出口': '🔴 出口',
                        '进口': '🔵 进口'
                    }).fillna('❓ 未知')
                    
                    # 分析中转地信息
                    def analyze_transit_hubs(df):
                        """分析每条航线的潜在中转地"""
                        transit_info = []
                        
                        for idx, row in df.iterrows():
                            origin = row['origin']
                            destination = row['destination']
                            
                            # 查找可能的中转地（同时连接起点和终点的城市）
                            potential_transits = []
                            
                            # 查找从起点出发的其他航线的目的地
                            origin_destinations = df[df['origin'] == origin]['destination'].unique()
                            # 查找到达终点的其他航线的起点
                            dest_origins = df[df['destination'] == destination]['origin'].unique()
                            
                            # 找到交集，即可能的中转地
                            common_cities = set(origin_destinations) & set(dest_origins)
                            # 排除起点和终点本身
                            common_cities.discard(origin)
                            common_cities.discard(destination)
                            
                            if common_cities:
                                # 按照该中转地的航班频次排序
                                transit_counts = {}
                                for city in common_cities:
                                    count = len(df[(df['origin'] == origin) & (df['destination'] == city)]) + \
                                           len(df[(df['origin'] == city) & (df['destination'] == destination)])
                                    transit_counts[city] = count
                                
                                # 选择频次最高的前3个中转地
                                sorted_transits = sorted(transit_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                                potential_transits = [city for city, count in sorted_transits]
                            
                            # 如果没有找到中转地，检查是否为直飞
                            if not potential_transits:
                                # 检查是否存在直接的往返航线
                                reverse_exists = len(df[(df['origin'] == destination) & (df['destination'] == origin)]) > 0
                                if reverse_exists:
                                    transit_info.append('🔄 直飞往返')
                                else:
                                    transit_info.append('✈️ 直飞')
                            else:
                                transit_info.append('🔀 ' + ', '.join(potential_transits[:2]))
                        
                        return transit_info
                    
                    # 添加中转地分析
                    display_df['中转地分析'] = analyze_transit_hubs(display_df)
                    
                    # 计算航班频次（基于相同航线的出现次数）
                    route_frequency = display_df.groupby(['origin', 'destination']).size().reset_index(name='route_count')
                    display_df = display_df.merge(route_frequency, on=['origin', 'destination'], how='left')
                    
                    # 添加每周往返班次信息
                    def format_weekly_roundtrip_frequency(count):
                        # 假设每条记录代表单程，往返需要除以2
                        roundtrip_count = count / 2
                        if roundtrip_count < 1:
                            return "每周不足1往返"
                        elif roundtrip_count == 1:
                            return "每周1往返"
                        elif roundtrip_count <= 3.5:
                            return f"每周{roundtrip_count:.1f}往返"
                        elif roundtrip_count <= 7:
                            return f"每周{roundtrip_count:.1f}往返"
                        else:
                            return f"高频({roundtrip_count:.1f}往返/周)"
                    
                    display_df['每周往返班次'] = display_df['route_count'].apply(format_weekly_roundtrip_frequency)
                    
                    # 调试：打印分类信息
                    if not display_df.empty:
                        st.write("🔍 调试信息：")
                        if 'origin_category' in display_df.columns:
                            origin_cats = display_df['origin_category'].value_counts()
                            st.write(f"始发地分类: {dict(origin_cats)}")
                        if 'destination_category' in display_df.columns:
                            dest_cats = display_df['destination_category'].value_counts()
                            st.write(f"目的地分类: {dict(dest_cats)}")
                        route_types = display_df['航线类型'].value_counts()
                        st.write(f"航线类型分布: {dict(route_types)}")
                    
                    # 处理机龄数据 - 简化显示，提取平均机龄或主要机龄
                    def simplify_age_data(age_str):
                        """显示实际机龄数据"""
                        if pd.isna(age_str) or str(age_str).strip() == '':
                            return '未知'
                        
                        age_str = str(age_str).strip()
                        
                        # 如果包含换行符，说明是多个机龄
                        if '\n' in age_str:
                            ages = [line.strip() for line in age_str.split('\n') if line.strip()]
                            if ages:
                                # 直接显示所有机龄，用逗号分隔
                                formatted_ages = []
                                for age in ages:
                                    if age.replace('.', '').isdigit():
                                        formatted_ages.append(age + '年')
                                    else:
                                        formatted_ages.append(age)
                                return ', '.join(formatted_ages)
                            else:
                                return '未知'
                        else:
                            # 单个机龄
                            if age_str.replace('.', '').isdigit():
                                return age_str + '年'
                            else:
                                return age_str
                    
                    # 应用机龄简化处理
                    if 'age' in display_df.columns:
                        display_df['simplified_age'] = display_df['age'].apply(simplify_age_data)
                    
                    # 优化列名显示（移除注册号，添加简化的机龄）
                    column_mapping = {
                        'airline': '✈️ 航空公司',
                        'aircraft': '🛩️ 机型',
                        'simplified_age': '📅 机龄',
                        'full_route': '🛣️ 完整航线',
                        'origin': '🛫 始发地',
                        'destination': '🛬 目的地',
                        'direction': '📍 方向',
                        '进出口类型': '🔄 进出口类型',
                        '航线类型': '🌍 航线类型',
                        '中转地分析': '🔀 中转地',
                        '每周往返班次': '📊 每周往返班次',
                        'flight_time': '⏱️ 飞行时长',
                        'flight_distance': '📏 飞行距离'
                    }
                    
                    # 选择要显示的列（移除注册号，添加机龄）
                    display_columns = [
                        '✈️ 航空公司', '🛩️ 机型', '📅 机龄', '🛣️ 完整航线', '🛫 始发地', '🛬 目的地', 
                        '🔄 进出口类型', '🌍 航线类型', '📊 每周往返班次', '⏱️ 飞行时长', '📏 飞行距离'
                    ]
                    
                    # 重命名列
                    display_df_renamed = display_df.rename(columns=column_mapping)
                    
                    # 显示数据统计信息
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("📊 航线记录", len(display_df))
                    with col2:
                        st.metric("✈️ 航空公司", display_df['airline'].nunique())
                    with col3:
                        st.metric("🛩️ 机型种类", display_df['aircraft'].nunique())
                    with col4:
                        export_count = len(display_df[display_df['direction'] == '出口'])
                        import_count = len(display_df[display_df['direction'] == '进口'])
                        st.metric("🔄 出口/进口", f"{export_count}/{import_count}")
                    with col5:
                        # 统计中转航线数量
                        transit_count = len(display_df[display_df['中转地分析'].str.contains('🔀', na=False)])
                        direct_count = len(display_df) - transit_count
                        st.metric("🔀 中转/直飞", f"{transit_count}/{direct_count}")
                    
                    # 添加详细统计信息
                    with st.expander("📈 详细统计信息", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("🛩️ 机型分布")
                            aircraft_counts = display_df['aircraft'].value_counts().head(10)
                            st.bar_chart(aircraft_counts)
                            
                            st.subheader("🔄 进出口分布")
                            direction_counts = display_df['direction'].value_counts()
                            st.bar_chart(direction_counts)
                        
                        with col2:
                            st.subheader("✈️ 航空公司分布")
                            airline_counts = display_df['airline'].value_counts().head(10)
                            st.bar_chart(airline_counts)
                            
                            st.subheader("🔀 中转地分布")
                            # 提取中转地信息进行统计
                            transit_data = display_df['中转地分析'].value_counts()
                            # 只显示实际的中转地（排除直飞）
                            transit_only = transit_data[transit_data.index.str.contains('🔀', na=False)]
                            if len(transit_only) > 0:
                                st.bar_chart(transit_only.head(8))
                            else:
                                st.info("当前筛选条件下暂无中转航线")
                            
                            st.subheader("🌍 航线类型分布")
                            route_type_counts = display_df['航线类型'].value_counts()
                            st.bar_chart(route_type_counts)
                    
                    # 优化表格显示
                    st.subheader("📋 详细航线明细")
                    st.dataframe(
                        display_df_renamed[display_columns],
                        use_container_width=True,
                        height=400
                    )
            
            else:
                st.warning("⚠️ 当前筛选条件下没有匹配的航线数据")
                st.info("💡 请调整筛选条件以查看航线信息")
        
        else:
            st.error("❌ 数据文件为空或格式不正确")
            st.info("请确保Excel/CSV文件包含正确的列名：航司、机型、出口航线、进口航线等")
    
    except Exception as e:
        st.error(f"❌ 数据加载失败: {str(e)}")
        st.info("请检查数据文件格式是否正确")

else:
    st.info("👆 请在左侧上传数据文件开始使用")
    st.markdown("""
    ### 📖 使用说明
    
    1. **数据格式要求**：
       - 支持 Excel (.xlsx) 和 CSV (.csv) 格式
       - 必须包含列：航司、机型、出口航线、进口航线
       - 航线格式：深圳(SZX)-德里(DEL)
    
    2. **功能特性**：
       - 🔍 多维度筛选（航司、始发地、目的地、机型、方向）
       - 🗺️ 交互式地图展示
       - 📤 HTML地图导出
       - 📊 Excel数据导出
    
    3. **数据文件夹**：
       - 默认路径：`D:\\flight_tool\\data`
       - 可直接将文件放入此文件夹
    """)

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>航线可视化工具 v1.0 | 支持多航司数据分析</div>", 
    unsafe_allow_html=True
)