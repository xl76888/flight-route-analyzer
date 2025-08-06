# D:\flight_tool\web_app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from parser import load_data
from data_cleaner import clean_route_data, get_sorted_cities, print_data_summary, categorize_city
from airport_coords import get_airport_coords
from static_manager import resource_manager
from map3d_integration import render_3d_map, create_3d_control_panel, get_3d_map_stats
from optimized_map3d_integration import render_optimized_3d_map
from fix_console_errors import apply_all_fixes
import os
import pandas as pd
import math
import numpy as np
from geopy.distance import geodesic

apply_all_fixes()

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
        # 验证坐标格式
        if not (origin_coords and dest_coords and 
                len(origin_coords) == 2 and len(dest_coords) == 2):
            return None
            
        # 验证坐标数值有效性
        for coord_pair in [origin_coords, dest_coords]:
            lat, lon = coord_pair
            # 检查是否为有限数值
            if not (math.isfinite(lat) and math.isfinite(lon)):
                return None
            # 检查经纬度范围
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return None
                
        distance = geodesic(origin_coords, dest_coords).kilometers
        # 验证计算结果
        if math.isfinite(distance) and distance >= 0:
            return round(distance, 0)
        return None
    except Exception as e:
        print(f"计算飞行距离时出错: {e}")
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
        # 验证距离数值有效性
        if not distance_km or not math.isfinite(distance_km) or distance_km <= 0:
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
        if aircraft_type:
            aircraft_upper = str(aircraft_type).upper()
            for model, model_speed in aircraft_speeds.items():
                if model in aircraft_upper:
                    speed = model_speed
                    break
        
        # 计算飞行时间（小时）
        flight_hours = distance_km / speed
        
        # 验证计算结果
        if not math.isfinite(flight_hours) or flight_hours <= 0:
            return None
        
        # 转换为小时h分钟m格式
        hours = int(flight_hours)
        minutes = int((flight_hours - hours) * 60)
        
        # 验证最终结果
        if hours < 0 or minutes < 0 or hours > 24:  # 超过24小时的飞行时间不太现实
            return None
            
        return f"{hours}h{minutes:02d}m"
    except Exception as e:
        print(f"计算飞行时间时出错: {e}")
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
            try:
                # 计算球面距离的余弦值，确保在有效范围内
                cos_d = math.sin(lat1_rad) * math.sin(lat2_rad) + math.cos(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
                cos_d = max(-1.0, min(1.0, cos_d))  # 限制在[-1, 1]范围内
                
                d = math.acos(cos_d)  # 球面距离
                
                # 如果距离太小，使用线性插值
                if d < 1e-6:
                    lat = lat1 + t * (lat2 - lat1)
                    lon = lon1 + t * delta_lon / math.pi * 180
                else:
                    sin_d = math.sin(d)
                    A = math.sin((1-t) * d) / sin_d
                    B = math.sin(t * d) / sin_d
                    
                    x = A * math.cos(lat1_rad) * math.cos(lon1_rad) + B * math.cos(lat2_rad) * math.cos(lon2_rad)
                    y = A * math.cos(lat1_rad) * math.sin(lon1_rad) + B * math.cos(lat2_rad) * math.sin(lon2_rad)
                    z = A * math.sin(lat1_rad) + B * math.sin(lat2_rad)
                    
                    # 确保计算结果有效
                    norm = math.sqrt(x*x + y*y + z*z)
                    if norm > 0:
                        x, y, z = x/norm, y/norm, z/norm
                    
                    lat = math.atan2(z, math.sqrt(x*x + y*y))
                    lon = math.atan2(y, x)
                    
                    # 转换回度数
                    lat_deg = math.degrees(lat)
                    lon_deg = math.degrees(lon)
                    
                    # 确保坐标在有效范围内
                    lat_deg = max(-90, min(90, lat_deg))
                    if lon_deg > 180:
                        lon_deg -= 360
                    elif lon_deg < -180:
                        lon_deg += 360
                
                # 验证坐标有效性
                if not (math.isfinite(lat_deg) and math.isfinite(lon_deg)):
                    raise ValueError("Invalid coordinates")
                    
                path_points.append([lat_deg, lon_deg])
                
            except Exception as e:
                # 如果大圆计算失败，回退到线性插值
                lat = lat1 + t * (lat2 - lat1)
                lon = lon1 + t * delta_lon / math.pi * 180
                
                # 确保坐标在有效范围内
                lat = max(-90, min(90, lat))
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
    生成两点间的直线路径，正确处理跨越180度经线的情况
    
    Args:
        start_coords: 起点坐标 [lat, lon]
        end_coords: 终点坐标 [lat, lon]
        num_points: 直线上的点数
    
    Returns:
        直线路径点列表
    """
    lat1, lon1 = start_coords
    lat2, lon2 = end_coords
    
    # 处理跨越180度经线的情况
    lon_diff = lon2 - lon1
    if abs(lon_diff) > 180:
        # 选择较短的路径
        if lon_diff > 0:
            lon2 -= 360
        else:
            lon2 += 360
    
    # 生成直线路径
    path_points = []
    for i in range(num_points + 1):
        t = i / num_points
        
        # 线性插值公式
        lat = lat1 + t * (lat2 - lat1)
        lon = lon1 + t * (lon2 - lon1)
        
        # 确保经度在-180到180范围内
        if lon > 180:
            lon -= 360
        elif lon < -180:
            lon += 360
        
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

# 指定最新的数据文件 - 优先使用integrated_all_data_latest.csv
integrated_data_file = os.path.join(default_folder, "integrated_all_data_latest.csv")
backup_data_file = os.path.join(default_folder, "中国十六家货航国际航线.xlsx")

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
    # 优先使用最新的integrated数据文件
    if os.path.exists(integrated_data_file):
        files_to_load = [integrated_data_file]
        st.sidebar.info(f"使用最新数据文件: integrated_all_data_latest.csv")
    elif os.path.exists(backup_data_file):
        files_to_load = [backup_data_file]
        st.sidebar.info(f"使用备用数据文件: 中国十六家货航国际航线.xlsx")
    else:
        st.sidebar.error(f"未找到数据文件")
        st.sidebar.warning("请确保文件存在或上传新的数据文件")

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
            # 检查文件类型并使用相应的加载方法
            if len(files_to_load) == 1 and files_to_load[0].endswith('.csv'):
                # 直接加载CSV文件（integrated_all_data_latest.csv）
                try:
                    routes_df = pd.read_csv(files_to_load[0], encoding='utf-8')
                    st.success(f"成功加载CSV文件，共 {len(routes_df)} 条航线记录")
                    
                    # 设置成功加载的文件信息
                    routes_df.attrs = {'successfully_loaded_files': [os.path.basename(files_to_load[0])]}
                    
                    # 添加缺失的列（确保与Excel数据格式一致）
                    if 'flight_number' not in routes_df.columns:
                        routes_df['flight_number'] = ''
                    if 'frequency' not in routes_df.columns:
                        routes_df['frequency'] = '正常运营'
                    if 'flight_time' not in routes_df.columns:
                        routes_df['flight_time'] = ''
                    if 'flight_distance' not in routes_df.columns:
                        routes_df['flight_distance'] = ''
                    if 'speed' not in routes_df.columns:
                        routes_df['speed'] = ''
                    
                    # 对CSV数据进行清理（如果需要）
                    if enable_deduplication:
                        routes_df = clean_route_data(routes_df, enable_deduplication=enable_deduplication)
                        
                except Exception as e:
                    st.error(f"CSV文件加载失败: {str(e)}")
                    routes_df = pd.DataFrame()
            else:
                # 检查是否有中国十六家货航国际航线.xlsx文件
                excel_file = None
                for file_path in files_to_load:
                    if '中国十六家货航国际航线.xlsx' in file_path or '中国十六家货航国际航线' in os.path.basename(file_path):
                        excel_file = file_path
                        break
                
                if excel_file:
                    # 检查是否为十六家货航文件，使用对应的解析函数
                    if '中国十六家货航国际航线' in os.path.basename(excel_file):
                        from parse_sixteen_airlines import parse_sixteen_airlines_excel
                        routes_df = parse_sixteen_airlines_excel(excel_file)
                    else:
                        # 使用原有解析函数处理其他Excel文件
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
                                
                                # 计算飞行速度
                                try:
                                    # 解析飞行时间（格式：小时:分钟）
                                    time_parts = flight_time.split(':')
                                    if len(time_parts) == 2:
                                        hours = float(time_parts[0])
                                        minutes = float(time_parts[1])
                                        total_hours = hours + minutes / 60
                                        
                                        if total_hours > 0:
                                            speed_kmh = distance_km / total_hours
                                            routes_df.at[idx, 'speed'] = f"{int(speed_kmh)} km/h"
                                except Exception as e:
                                    print(f"计算飞行速度时出错: {e}")
                    
                    # 如果飞行速度为空但有距离和时间，计算速度
                    elif (pd.isna(row['speed']) or str(row['speed']).strip() == '') and \
                         not (pd.isna(row['flight_time']) or str(row['flight_time']).strip() == '') and \
                         not (pd.isna(row['flight_distance']) or str(row['flight_distance']).strip() == ''):
                        try:
                            # 提取距离数值
                            distance_str = str(row['flight_distance'])
                            distance_km = None
                            if '公里' in distance_str:
                                distance_km = float(distance_str.replace('公里', '').strip())
                            elif distance_str.replace('.', '').isdigit():
                                distance_km = float(distance_str)
                            
                            # 解析飞行时间
                            flight_time_str = str(row['flight_time'])
                            time_parts = flight_time_str.split(':')
                            if len(time_parts) == 2 and distance_km:
                                hours = float(time_parts[0])
                                minutes = float(time_parts[1])
                                total_hours = hours + minutes / 60
                                
                                if total_hours > 0:
                                    speed_kmh = distance_km / total_hours
                                    routes_df.at[idx, 'speed'] = f"{int(speed_kmh)} km/h"
                        except Exception as e:
                            print(f"计算现有数据飞行速度时出错: {e}")
            
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
            
            # 初始化会话状态
            if 'map_type' not in st.session_state:
                st.session_state.map_type = '2D地图'
            if 'view_mode' not in st.session_state:
                st.session_state.view_mode = '标准视图'
            
            # 地图类型选择 - 使用会话状态管理
            map_type = st.sidebar.radio(
                "地图类型",
                ["2D地图", "3D地图"],
                index=0 if st.session_state.map_type == '2D地图' else 1,
                help="2D地图：传统平面地图\n3D地图：立体航线展示",
                key='map_type_selector'
            )
            # 更新会话状态
            st.session_state.map_type = map_type
            
            view_mode = st.sidebar.radio(
                "数据视图模式",
                ["标准视图", "往返航线视图"],
                index=0 if st.session_state.view_mode == '标准视图' else 1,
                help="标准视图：显示所有航线\n往返航线视图：将出口和进口航线配对显示",
                key='view_mode_selector'
            )
            # 更新会话状态
            st.session_state.view_mode = view_mode
            
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
            
            # 3D地图控制选项
            st.sidebar.subheader("🎛️ 3D地图控制")
            animation_enabled = st.sidebar.checkbox(
                "启用航线动画", 
                value=True, 
                key="3d_animation_enabled",
                help="为高频航线（≥5班/周）添加动态流动效果"
            )
            if animation_enabled:
                animation_speed = st.sidebar.slider(
                    "动画速度", 
                    min_value=500, 
                    max_value=5000, 
                    value=2000, 
                    step=500, 
                    key="3d_animation_speed",
                    help="调节动画播放速度（毫秒）"
                )
            else:
                animation_speed = 2000
                
            # 将动画设置存储到session_state
            st.session_state['animation_enabled'] = animation_enabled
            st.session_state['animation_speed'] = animation_speed
            
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
            
            # 初始化往返航线配对变量（确保在所有模式下都可访问）
            round_trip_pairs = []
            
            # 处理往返航线视图
            if view_mode == "往返航线视图":
                # 创建往返航线配对
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
            if view_mode == "往返航线视图":
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
                # 注入 Leaflet 图标路径修复脚本
                apply_all_fixes()
                
                # 创建地图（使用美观明亮的瓦片源，强制刷新）
                import time
                # 根据地图类型和数据生成唯一键值
                data_signature = f"{len(filtered)}_{hash(str(sorted(filtered['origin'].tolist() + filtered['destination'].tolist())))}"
                map_key = f"map_{map_type}_{data_signature}_{int(time.time())}"
                
                m = folium.Map(
                    location=[20.0, 0.0],  # 以0度经线为中心，确保美洲在西半球正确显示
                    zoom_start=2,  # 降低初始缩放级别以显示完整世界地图
                    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',  # 使用新的稳定CartoDB URL
                    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>',
                    prefer_canvas=True,  # 使用Canvas渲染，减少闪烁
                    max_bounds=False,  # 移除地图边界限制，允许自由移动
                    min_zoom=1,  # 最小缩放级别
                    max_zoom=18,  # 最大缩放级别
                    world_copy_jump=True,  # 启用世界地图重复显示，便于跨越180度经线的航线显示
                    crs='EPSG3857',  # 使用Web墨卡托投影
                    width='100%',  # 地图宽度设置为100%
                    height='800px'  # 地图高度设置为800像素
                )
                
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
                    
                    
                    # 检查坐标是否有效
                    if origin_coords is None or dest_coords is None:
                        print(f"警告：无法获取坐标 - {row['origin']} 或 {row['destination']}")
                        routes_without_coords += 1
                        continue
                    
                    # 验证坐标数值有效性
                    def is_valid_coordinate(coords):
                        if not coords or len(coords) != 2:
                            return False
                        lat, lon = coords
                        return (isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and
                                math.isfinite(lat) and math.isfinite(lon) and
                                -90 <= lat <= 90 and -180 <= lon <= 180)
                    
                    if not is_valid_coordinate(origin_coords) or not is_valid_coordinate(dest_coords):
                        print(f"警告：坐标数值无效 - {row['origin']}: {origin_coords}, {row['destination']}: {dest_coords}")
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
                        
                        # 标识中转航线（基于数据源中的实际中转信息）
                        # 检查是否包含中转信息（支持多种分隔符）
                        transit_separators = ['-', '—', '→', '>']
                        has_transit = any(
                            sep in str(row['origin']) or sep in str(row['destination']) 
                            for sep in transit_separators
                        )
                        if has_transit:
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
                        
                        # 安全处理弹出框内容，避免特殊字符导致闪退
                        import html
                        safe_origin = html.escape(str(row['origin']))
                        safe_destination = html.escape(str(row['destination']))
                        safe_main_airline = html.escape(str(main_airline))
                        safe_aircraft = html.escape(str(row['aircraft']))
                        safe_route_type = html.escape(str(route_type))
                        safe_directions = html.escape(' + '.join(directions_list))
                        safe_airlines = html.escape(', '.join(airlines_list[:3]))
                        
                        popup_content = f"""
                        <div style='width: 350px; font-family: Arial, sans-serif; line-height: 1.4;'>
                            <h3 style='margin: 0; color: {line_color}; border-bottom: 2px solid {line_color}; padding-bottom: 5px;'>
                                ✈️ {safe_origin} {direction_indicator} {safe_destination}
                            </h3>
                            <div style='margin: 10px 0;'>
                                <div style='margin: 3px 0; padding: 3px 8px; background: {line_color}20; border-radius: 5px; border-left: 3px solid {line_color};'>
                                    <strong>{safe_route_type}</strong>
                                </div>
                                <p style='margin: 3px 0;'><b>🏢 主要航司:</b> <span style='color: {line_color};'>{safe_main_airline}</span></p>
                                <p style='margin: 3px 0;'><b>📊 航班频次:</b> <span style='background: {line_color}; color: white; padding: 2px 6px; border-radius: 3px;'>{frequency} 班</span></p>
                                <p style='margin: 3px 0;'><b>🔄 运营方向:</b> {safe_directions}</p>
                                <p style='margin: 3px 0;'><b>🛫 服务航司:</b> {safe_airlines}{'...' if len(airlines_list) > 3 else ''}</p>
                                <p style='margin: 3px 0;'><b>✈️ 机型:</b> {safe_aircraft}</p>
                            </div>
                        </div>
                        """
                        
                        # 添加航线（优化渲染，减少闪烁）
                        # 获取动画控制参数
                        animation_enabled = st.session_state.get('animation_enabled', True)
                        animation_speed = st.session_state.get('animation_speed', 2000)
                        
                        if frequency >= 5 and animation_enabled:  # 高频航线且启用动画
                            # 高频航线使用动态效果
                            try:
                                from folium.plugins import AntPath
                                AntPath(
                                    locations=straight_path,
                                    color=line_color,
                                    weight=line_weight,
                                    opacity=line_opacity * 0.6,  # 进一步降低透明度
                                    delay=animation_speed,  # 使用用户设置的动画速度
                                    dash_array=[15, 25],  # 优化虚线间距
                                    pulse_color=line_color,  # 使用相同颜色减少对比
                                    popup=folium.Popup(popup_content, max_width=350),
                                    tooltip=f"{route_type} - {row['origin']} → {row['destination']} ({frequency}班) 🎬"
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
                        
                        # 添加始发地和目的地标记
                        # 始发地标记
                        folium.Marker(
                            location=origin_coords,
                            popup=f"🛫 始发地: {row['origin']}",
                            tooltip=f"🛫 {row['origin']}",
                            icon=folium.DivIcon(
                                html=f'<div style="background-color: #28a745; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">🛫</div>',
                                icon_size=(20, 20),
                                icon_anchor=(10, 10)
                            )
                        ).add_to(m)
                        
                        # 目的地标记
                        folium.Marker(
                            location=dest_coords,
                            popup=f"🛬 目的地: {row['destination']}",
                            tooltip=f"🛬 {row['destination']}",
                            icon=folium.DivIcon(
                                html=f'<div style="background-color: #dc3545; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">🛬</div>',
                                icon_size=(20, 20),
                                icon_anchor=(10, 10)
                            )
                        ).add_to(m)
                
                # 创建航线类型图例（可折叠）
                legend_html = """
                <div id="legend-container" style="position: fixed; 
                           top: 10px; right: 10px; width: 260px; height: auto;
                           background-color: white; border:2px solid grey; z-index:9999; 
                           font-size:12px; border-radius: 8px;
                           box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                    <!-- 图例标题栏（可点击折叠） -->
                    <div style="
                        padding: 12px; cursor: pointer; background: #f8f9fa; 
                        border-radius: 6px 6px 0 0; border-bottom: 1px solid #ddd;
                        display: flex; justify-content: space-between; align-items: center;"
                        onclick="var content = document.getElementById('legend-content');
                                var toggle = document.getElementById('legend-toggle');
                                if (content.style.display === 'none') {
                                    content.style.display = 'block';
                                    toggle.textContent = '▼';
                                } else {
                                    content.style.display = 'none';
                                    toggle.textContent = '▶';
                                }">
                        <h4 style="margin: 0; color: #333; font-size: 14px;">🗺️ 航线图例</h4>
                        <span id="legend-toggle" style="font-size: 16px; color: #666;">▼</span>
                    </div>
                    
                    <!-- 图例内容（可折叠） -->
                    <div id="legend-content" style="padding: 12px; display: block;">
                        <!-- 机场标记说明 -->
                        <div style="margin-bottom: 12px;">
                            <h5 style="margin: 5px 0; color: #333; font-size: 12px;">🛫 机场标记</h5>
                            <div style="margin: 6px 0; display: flex; align-items: center;">
                                <div style="width: 16px; height: 16px; background: #8B0000; 
                                           border-radius: 50%; margin-right: 8px; border: 1px solid white;"></div>
                                <span style="font-size: 11px; color: #333;">超级枢纽 (≥30班)</span>
                            </div>
                            <div style="margin: 6px 0; display: flex; align-items: center;">
                                <div style="width: 14px; height: 14px; background: #FF4500; 
                                           border-radius: 50%; margin-right: 8px; border: 1px solid white;"></div>
                                <span style="font-size: 11px; color: #333;">主要枢纽 (20-29班)</span>
                            </div>
                            <div style="margin: 6px 0; display: flex; align-items: center;">
                                <div style="width: 12px; height: 12px; background: #FFD700; 
                                           border-radius: 50%; margin-right: 8px; border: 1px solid white;"></div>
                                <span style="font-size: 11px; color: #333;">区域枢纽 (10-19班)</span>
                            </div>
                            <div style="margin: 6px 0; display: flex; align-items: center;">
                                <div style="width: 10px; height: 10px; background: #4169E1; 
                                           border-radius: 50%; margin-right: 8px; border: 1px solid white;"></div>
                                <span style="font-size: 11px; color: #333;">重要机场 (5-9班)</span>
                            </div>
                            <div style="margin: 6px 0; display: flex; align-items: center;">
                                <div style="width: 8px; height: 8px; background: #32CD32; 
                                           border-radius: 50%; margin-right: 8px; border: 1px solid white;"></div>
                                <span style="font-size: 11px; color: #333;">一般机场 (<5班)</span>
                            </div>
                            <div style="margin: 6px 0; font-size: 10px; color: #666; padding: 4px; background: #f0f8ff; border-radius: 3px;">
                                📍 显示完整机场代码标签
                            </div>
                        </div>
                        
                        <hr style="margin: 10px 0; border: none; border-top: 1px solid #ddd;">
                        
                        <!-- 航线标记说明 -->
                        <div style="margin-bottom: 12px;">
                            <h5 style="margin: 5px 0; color: #333; font-size: 12px;">🎯 航线标记</h5>
                            <div style="margin: 6px 0; display: flex; align-items: center;">
                                <div style="width: 16px; height: 16px; background: #28a745; 
                                           border-radius: 50%; margin-right: 8px; border: 2px solid white;"></div>
                                <span style="font-size: 11px; color: #333;">🛫 始发地标记</span>
                            </div>
                            <div style="margin: 6px 0; display: flex; align-items: center;">
                                <div style="width: 16px; height: 16px; background: #dc3545; 
                                           border-radius: 50%; margin-right: 8px; border: 2px solid white;"></div>
                                <span style="font-size: 11px; color: #333;">🛬 目的地标记</span>
                            </div>
                        </div>
                        
                        <hr style="margin: 10px 0; border: none; border-top: 1px solid #ddd;">
                        
                        <!-- 航线类型图例 -->
                        <div style="margin-bottom: 12px;">
                            <h5 style="margin: 5px 0; color: #333; font-size: 12px;">🌍 航线类型</h5>
                            <div style="margin: 6px 0; display: flex; align-items: center;">
                                <div style="width: 20px; height: 4px; background-color: #4CAF50; 
                                           border-radius: 2px; margin-right: 10px;"></div>
                                <span style="font-size: 11px; color: #333;">国际进口</span>
                            </div>
                            <div style="margin: 6px 0; display: flex; align-items: center;">
                                <div style="width: 20px; height: 4px; background-color: #FFC107; 
                                           border-radius: 2px; margin-right: 10px;"></div>
                                <span style="font-size: 11px; color: #333;">国际出口</span>
                            </div>
                            <div style="margin: 6px 0; font-size: 10px; color: #666; padding: 4px; background: #f5f5f5; border-radius: 3px;">
                                💡 国内机场作为中转地，无纯国内航线
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
                    </div>
                    
                    <!-- 折叠功能脚本 -->
                    <script>
                        function toggleLegend() {
                            const content = document.getElementById('legend-content');
                            const toggle = document.getElementById('legend-toggle');
                            const container = document.getElementById('legend-container');
                            
                            if (content.style.display === 'none') {
                                content.style.display = 'block';
                                toggle.textContent = '▼';
                                container.style.height = 'auto';
                            } else {
                                content.style.display = 'none';
                                toggle.textContent = '▶';
                                container.style.height = 'auto';
                            }
                        }
                        
                        // 默认展开状态
                        document.addEventListener('DOMContentLoaded', function() {
                            document.getElementById('legend-content').style.display = 'block';
                        });
                    </script>
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
                    
                    # 统计中转航线（基于分隔符判断）
                    origin = str(route['origin'])
                    destination = str(route['destination'])
                    transit_separators = ['-', '—', '→', '>']
                    has_transit = any(
                        sep in origin or sep in destination 
                        for sep in transit_separators
                    )
                    if has_transit:
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
                    
                    # 创建自定义图标和标签
                    icon_html = f"""
                    <div style="
                        position: relative;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                    ">
                        <!-- 机场图标 -->
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
                        <!-- 机场标签 -->
                        <div style="
                            margin-top: 2px;
                            background: rgba(255, 255, 255, 0.9);
                            border: 1px solid {icon_color};
                            border-radius: 4px;
                            padding: 1px 4px;
                            font-size: 10px;
                            font-weight: bold;
                            color: {icon_color};
                            white-space: nowrap;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                            text-shadow: none;
                        ">{airport_code}</div>
                    </div>
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
                
                # 根据地图类型显示不同的地图
                if map_type == "3D地图":
                    st.subheader("🌐 3D航线地图")
                    
                    # 检查3D地图配置
                    from config.google_maps_config import is_maps_configured, show_maps_config_status
                    
                    if not is_maps_configured():
                        st.warning("⚠️ 3D地图功能需要配置Google Maps API")
                        show_maps_config_status()
                        st.info("💡 暂时显示2D地图，配置完成后可使用3D功能")
                        map_output = st_folium(m, width=1400, height=800, returned_objects=["last_object_clicked"], key=map_key)
                    else:
                        # 准备3D地图数据
                        route_data_3d = []
                        valid_routes_count = 0
                        invalid_routes_count = 0
                        
                        # 导入新的机场信息获取函数
                        from airport_coords import get_airport_info
                        
                        for _, route in filtered.iterrows():
                            # 使用正确的字段名
                            origin_code = route.get('origin', '')
                            destination_code = route.get('destination', '')
                            
                            start_info = get_airport_info(origin_code)
                            end_info = get_airport_info(destination_code)
                            
                            if start_info and end_info:
                                # 验证坐标数值有效性
                                def is_valid_coordinate_3d(coords):
                                    if not coords or len(coords) != 2:
                                        return False
                                    lat, lon = coords
                                    return (isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and
                                            math.isfinite(lat) and math.isfinite(lon) and
                                            -90 <= lat <= 90 and -180 <= lon <= 180)
                                
                                if not is_valid_coordinate_3d(start_info['coords']) or not is_valid_coordinate_3d(end_info['coords']):
                                    print(f"警告：3D地图坐标数值无效 - {origin_code}: {start_info['coords']}, {destination_code}: {end_info['coords']}")
                                    invalid_routes_count += 1
                                    continue
                                
                                try:
                                    # 检查是否为双向航线
                                    route_key = f"{origin_code}-{destination_code}"
                                    reverse_route_key = f"{destination_code}-{origin_code}"
                                    
                                    # 在往返航线视图模式下，使用不同的双向航线检测逻辑
                                    if view_mode == "往返航线视图":
                                        # 在往返航线视图中，检查当前航线对是否有双向数据
                                        origin = route.get('origin', '')
                                        destination = route.get('destination', '')
                                        route_pair_key = tuple(sorted([origin, destination]))
                                        
                                        # 查找对应的航线对
                                        is_bidirectional = False
                                        # 检查round_trip_pairs是否有数据
                                        if round_trip_pairs:
                                            for pair in round_trip_pairs:
                                                if pair['has_both_directions']:
                                                    pair_cities = pair['city_pair'].replace(' ↔ ', '|').split('|')
                                                    if len(pair_cities) == 2:
                                                        pair_key = tuple(sorted(pair_cities))
                                                        if pair_key == route_pair_key:
                                                            is_bidirectional = True
                                                            break
                                        else:
                                            # 如果round_trip_pairs为空，使用route_stats检测
                                            is_bidirectional = reverse_route_key in route_stats
                                    else:
                                        # 标准视图模式下的双向航线检测
                                        is_bidirectional = reverse_route_key in route_stats
                                    
                                    # 调试信息：打印双向航线检测结果
                                    if is_bidirectional:
                                        print(f"发现双向航线: {route_key} <-> {reverse_route_key} (模式: {view_mode})")
                                    
                                    # 检查机场信息是否有效
                                    if start_info and end_info and start_info.get('coords') and end_info.get('coords'):
                                        route_data_3d.append({
                                            'id': f"route_{valid_routes_count}",
                                            'start_airport': origin_code,
                                            'end_airport': destination_code,
                                            'start_airport_name': start_info['name'],  # 使用真实的机场名称
                                            'end_airport_name': end_info['name'],  # 使用真实的机场名称
                                            'origin': origin_code,  # 添加origin字段用于机场标记
                                            'destination': destination_code,  # 添加destination字段用于机场标记
                                            'start_lat': float(start_info['coords'][0]),
                                            'start_lng': float(start_info['coords'][1]),
                                            'end_lat': float(end_info['coords'][0]),
                                            'end_lng': float(end_info['coords'][1]),
                                            'frequency': int(route_stats.get(route_key, {}).get('count', 1)),
                                            'airline': str(route.get('airline', '')),
                                            'aircraft_type': str(route.get('aircraft', '')),
                                            'route_type': 'international',  # 标记为国际航线
                                            'direction': str(route.get('direction', '出口')),  # 添加方向字段
                                            'is_bidirectional': is_bidirectional,  # 添加双向航线标识
                                            'bidirectional': is_bidirectional  # 添加备用字段名
                                        })
                                        valid_routes_count += 1
                                    else:
                                        print(f"跳过航线 {origin_code} -> {destination_code}: 机场信息不完整")
                                        invalid_routes_count += 1
                                except Exception as e:
                                    print(f"处理航线数据时出错: {e}, 航线: {origin_code} -> {destination_code}")
                                    invalid_routes_count += 1
                            else:
                                invalid_routes_count += 1
                        
                        # 显示数据处理统计
                        if invalid_routes_count > 0:
                            st.info(f"📊 数据处理: 有效航线 {valid_routes_count} 条，无效航线 {invalid_routes_count} 条")
                        
                        if len(route_data_3d) == 0:
                            st.warning("⚠️ 没有有效的航线数据可以显示在3D地图上")
                            st.info("💡 可能原因：机场坐标缺失或数据格式错误")
                            st.info("💡 显示2D地图作为替代")
                            map_output = st_folium(m, width=1400, height=800, returned_objects=["last_object_clicked"], key=map_key)
                        else:
                            # 显示3D地图控制面板
                            try:
                                control_config = create_3d_control_panel()
                            except:
                                control_config = {}
                            
                            # 显示3D地图加载提示
                            with st.spinner("🌐 正在加载3D地图，请稍候..."):
                                # 渲染3D地图
                                try:
                                    # 生成数据哈希用于动态key，确保数据变化时强制重新渲染
                                    import hashlib
                                    import json
                                    data_str = json.dumps(route_data_3d, sort_keys=True, default=str)
                                    data_hash = hashlib.md5(data_str.encode()).hexdigest()[:8]
                                    
                                    # 使用动态key强制重新加载3D地图组件
                                    map_output = render_optimized_3d_map(
                                        route_data_3d,
                                        height=700,
                                        key=f"3d_map_{data_hash}",  # 动态key确保数据变化时重新渲染
                                        force_reload=True,  # 强制重新加载
                                        **control_config
                                    )
                                    
                                    # 显示3D地图统计
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.info(f"🗺️ 3D航线: {len(route_data_3d)} 条")
                                    with col2:
                                        unique_airports = len(set([r['start_airport'] for r in route_data_3d] + [r['end_airport'] for r in route_data_3d]))
                                        st.success(f"✈️ 机场: {unique_airports} 个")
                                    with col3:
                                        unique_airlines = len(set([r['airline'] for r in route_data_3d]))
                                        st.warning(f"🏢 航司: {unique_airlines} 家")
                                    with col4:
                                        avg_frequency = sum([r['frequency'] for r in route_data_3d]) / len(route_data_3d) if route_data_3d else 0
                                        st.metric("平均频率", f"{avg_frequency:.1f}")
                                
                                except Exception as e:
                                    st.error(f"❌ 3D地图加载失败: {str(e)}")
                                    st.info("🔧 可能的原因：")
                                    st.info("• Google Maps API密钥未启用3D Maps功能")
                                    st.info("• 地图ID配置不正确")
                                    st.info("• 网络连接问题")
                                    st.info("• 浏览器不支持WebGL")
                                    st.info("💡 正在回退到2D地图...")
                                    map_output = st_folium(m, width=1400, height=800, returned_objects=["last_object_clicked"], key=map_key)
                
                else:
                    # 显示2D地图 - 使用更大的尺寸和全宽度，强制刷新
                    st.subheader("🗺️ 2D航线地图")
                    map_output = st_folium(m, width=1400, height=800, returned_objects=["last_object_clicked"], key=map_key)
                
                # 重新计算当前筛选数据的坐标统计
                current_routes_without_coords = 0
                current_total_records = len(filtered)
                
                for idx, row in filtered.iterrows():
                    origin_coords = get_airport_coords(row['origin'])
                    dest_coords = get_airport_coords(row['destination'])
                    
                    # 检查坐标是否有效
                    if origin_coords is None or dest_coords is None:
                        current_routes_without_coords += 1
                        continue
                    
                    # 验证坐标数值有效性
                    def is_valid_coordinate(coords):
                        if not coords or len(coords) != 2:
                            return False
                        lat, lon = coords
                        return (isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and
                                math.isfinite(lat) and math.isfinite(lon) and
                                -90 <= lat <= 90 and -180 <= lon <= 180)
                    
                    if not is_valid_coordinate(origin_coords) or not is_valid_coordinate(dest_coords):
                        current_routes_without_coords += 1
                
                # 显示地图统计信息
                if map_type == "2D地图":
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.info(f"🗺️ 地图显示航线: {unique_routes_displayed} 条")
                    with col2:
                        if current_routes_without_coords > 0:
                            st.warning(f"⚠️ 缺失坐标航线: {current_routes_without_coords} 条")
                        else:
                            st.success(f"✅ 所有航线坐标完整: 0 条缺失")
                    with col3:
                        st.success(f"📊 总航线记录: {current_total_records} 条")
                    with col4:
                        valid_routes = current_total_records - current_routes_without_coords
                        st.metric("显示率", f"{(unique_routes_displayed/current_total_records*100):.1f}%" if current_total_records > 0 else "0%")
                        st.metric("有效率", f"{(valid_routes/current_total_records*100):.1f}%" if current_total_records > 0 else "0%")
                    
                    if current_routes_without_coords > 0:
                        st.caption("💡 提示：缺失坐标的航线仍包含在数据统计中，但无法在地图上显示")
                    
                    if current_total_records > unique_routes_displayed + current_routes_without_coords:
                        st.caption(f"📋 说明：总记录数包含重复航线，地图仅显示 {unique_routes_displayed} 条唯一航线路径")
                
                # 减少地图和导出功能之间的间距
                st.markdown("<div style='margin-top: -1rem; margin-bottom: -1rem;'></div>", unsafe_allow_html=True)
                
                # 导出功能
                st.header("📤 导出功能")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📄 导出当前地图为 HTML", type="primary"):
                        export_path = "D:/flight_tool/exported_map.html"
                        # 修复导出时的边界问题
                        try:
                            # 临时移除可能的边界限制
                            original_max_bounds = getattr(m, '_max_bounds', None)
                            if hasattr(m, '_max_bounds'):
                                m._max_bounds = None
                            
                            # 保存地图
                            m.save(export_path)
                            
                            # 读取并修复导出的HTML文件，移除maxBounds设置
                            with open(export_path, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            # 移除maxBounds配置
                            import re
                            html_content = re.sub(r'"maxBounds":\s*\[[^\]]+\],?', '', html_content)
                            html_content = re.sub(r'maxBounds:\s*\[[^\]]+\],?', '', html_content)
                            
                            # 写回修复后的内容
                            with open(export_path, 'w', encoding='utf-8') as f:
                                f.write(html_content)
                            
                            # 恢复原始设置
                            if original_max_bounds is not None:
                                m._max_bounds = original_max_bounds
                                
                            st.success(f"地图已导出到: {export_path}")
                            st.balloons()
                        except Exception as e:
                            st.error(f"导出地图时出错: {str(e)}")
                            # 尝试基本导出
                            try:
                                m.save(export_path)
                                st.warning(f"使用基本模式导出到: {export_path}")
                            except:
                                st.error("导出失败，请检查文件路径权限")
                
                with col2:
                    if st.button("📊 导出筛选数据为 Excel"):
                        export_path = "D:/flight_tool/filtered_data.xlsx"
                        filtered.to_excel(export_path, index=False)
                        st.success(f"数据已导出到: {export_path}")
                
                # 减少导出功能和数据表格之间的间距
                st.markdown("<div style='margin-top: -1rem; margin-bottom: -0.5rem;'></div>", unsafe_allow_html=True)
                
                # 添加航线类型列用于显示
                display_df = filtered.copy()
                
            # 数据表格预览 - 移出expander，直接显示
            # with st.expander("📋 查看筛选后的数据详情", expanded=True):
                
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
                """改进的中转地分析逻辑 - 优先使用实际中转站信息"""
                transit_info = []
                
                for idx, row in df.iterrows():
                    origin = str(row['origin'])
                    destination = str(row['destination'])
                    
                    # 首先检查是否有明确的中转站信息
                    actual_transits = []
                    
                    # 从destination字段提取中转站（支持多种分隔符）
                    transit_separators = ['-', '—', '→', '>']
                    for sep in transit_separators:
                        if sep in destination:
                            parts = destination.split(sep)
                            if len(parts) > 1:
                                actual_transits.extend([p.strip() for p in parts[:-1] if p.strip()])
                            break
                    
                    # 从origin字段提取中转站（支持多种分隔符）
                    for sep in transit_separators:
                        if sep in origin:
                            parts = origin.split(sep)
                            if len(parts) > 1:
                                actual_transits.extend([p.strip() for p in parts[1:] if p.strip()])
                            break
                    
                    if actual_transits:
                        # 有明确的中转站信息
                        unique_transits = list(dict.fromkeys(actual_transits))  # 去重保序
                        transit_info.append('🔄 ' + ', '.join(unique_transits[:2]))
                    else:
                        # 没有明确中转站，进行网络分析（仅作为补充）
                        real_origin = origin.split('-')[0].strip() if '-' in origin else origin.strip()
                        real_destination = destination.split('-')[-1].strip() if '-' in destination else destination.strip()
                        
                        # 查找可能的中转地（同时连接起点和终点的城市）
                        potential_transits = []
                        
                        # 查找从起点出发的其他航线的目的地
                        origin_destinations = df[df['origin'] == real_origin]['destination'].unique()
                        # 查找到达终点的其他航线的起点
                        dest_origins = df[df['destination'] == real_destination]['origin'].unique()
                        
                        # 找到交集，即可能的中转地
                        common_cities = set(origin_destinations) & set(dest_origins)
                        # 排除起点和终点本身
                        common_cities.discard(real_origin)
                        common_cities.discard(real_destination)
                        
                        if common_cities:
                            # 按照该中转地的航班频次排序
                            transit_counts = {}
                            for city in common_cities:
                                count = len(df[(df['origin'] == real_origin) & (df['destination'] == city)]) + \
                                       len(df[(df['origin'] == city) & (df['destination'] == real_destination)])
                                transit_counts[city] = count
                            
                            # 选择频次最高的前2个中转地，并标记为潜在中转枢纽
                            sorted_transits = sorted(transit_counts.items(), key=lambda x: x[1], reverse=True)[:2]
                            potential_transits = [city for city, count in sorted_transits]
                            transit_info.append('🔀 潜在枢纽: ' + ', '.join(potential_transits))
                        else:
                            # 检查是否存在直接的往返航线
                            reverse_exists = len(df[
                                (df['origin'].str.contains(real_destination, na=False)) & 
                                (df['destination'].str.contains(real_origin, na=False))
                            ]) > 0
                            
                            if reverse_exists:
                                transit_info.append('✈️ 直飞往返')
                            else:
                                transit_info.append('✈️ 直飞')
                
                return transit_info
            
            # 添加中转地分析
            display_df['中转地分析'] = analyze_transit_hubs(display_df)
            
            # 添加中转站字段（从原始数据中提取）
            def extract_transit_station(row):
                """从原始数据中提取中转站信息"""
                transit_stations = []
                transit_separators = ['-', '—', '→', '>']
                
                # 检查destination字段是否包含中转站信息
                destination = str(row.get('destination', '')).strip()
                for sep in transit_separators:
                    if sep in destination:
                        parts = destination.split(sep)
                        if len(parts) >= 2:
                            # 除了最后一个部分（真正的目的地），前面的都可能是中转站
                            for i in range(len(parts) - 1):
                                transit_part = parts[i].strip()
                                if transit_part:
                                    transit_stations.append(transit_part)
                        break  # 找到第一个分隔符就停止
                
                # 检查origin字段是否包含中转站信息
                origin = str(row.get('origin', '')).strip()
                for sep in transit_separators:
                    if sep in origin:
                        parts = origin.split(sep)
                        if len(parts) >= 2:
                            # 除了第一个部分（真正的起点），后面的都可能是中转站
                            for i in range(1, len(parts)):
                                transit_part = parts[i].strip()
                                if transit_part:
                                    transit_stations.append(transit_part)
                        break  # 找到第一个分隔符就停止
                
                # 去重并返回
                unique_stations = list(dict.fromkeys(transit_stations))  # 保持顺序的去重
                return ', '.join(unique_stations) if unique_stations else ''
            
            display_df['中转站'] = display_df.apply(extract_transit_station, axis=1)
            
            # 添加航线类型字段（区分直飞和中转）
            def determine_route_type(row):
                """判断航线类型：直飞或中转"""
                origin = str(row['origin'])
                destination = str(row['destination'])
                
                # 检查是否包含中转信息（支持多种分隔符）
                transit_separators = ['-', '—', '→', '>']
                has_transit = any(
                    sep in origin or sep in destination 
                    for sep in transit_separators
                )
                return '🔄 中转' if has_transit else '✈️ 直飞'
            
            display_df['航线类型'] = display_df.apply(determine_route_type, axis=1)
            
            # 修改进出口类型显示，包含航线类型信息
            display_df['进出口类型'] = display_df.apply(
                lambda row: f"{row['direction']} ({row['航线类型'].replace('🔄 ', '').replace('✈️ ', '')})",
                axis=1
            )
            
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
                
                # 处理速度数据
                def format_speed_data(speed_str):
                    """格式化速度数据显示"""
                    if pd.isna(speed_str) or str(speed_str).strip() == '':
                        return '未知'
                    
                    speed_str = str(speed_str).strip()
                    
                    # 如果已经包含单位，直接返回
                    if any(unit in speed_str.lower() for unit in ['km/h', 'mph', 'knots', '节', '公里/小时']):
                        return speed_str
                    
                    # 如果是纯数字，添加km/h单位
                    if speed_str.replace('.', '').replace(',', '').isdigit():
                        return speed_str + ' km/h'
                    
                    return speed_str
                
                # 处理每周班次数据
                def format_weekly_frequency_data(freq_str):
                    """格式化每周班次数据显示"""
                    if pd.isna(freq_str) or str(freq_str).strip() == '':
                        return '未知'
                    
                    freq_str = str(freq_str).strip()
                    
                    # 如果已经包含单位，直接返回
                    if any(unit in freq_str for unit in ['班', '次', '班/周', '次/周']):
                        return freq_str
                    
                    # 如果是纯数字，添加班/周单位
                    if freq_str.replace('.', '').replace(',', '').isdigit():
                        return freq_str + ' 班/周'
                    
                    return freq_str
                
                # 应用速度和每周班次处理
                if 'speed' in display_df.columns:
                    display_df['speed'] = display_df['speed'].apply(format_speed_data)
                
                if 'weekly_frequency' in display_df.columns:
                    display_df['weekly_frequency'] = display_df['weekly_frequency'].apply(format_weekly_frequency_data)
                
                # 处理进出口城市-城市数据
                def format_import_export_cities_data(row):
                    """格式化进出口城市-城市数据显示"""
                    if pd.isna(row) or str(row).strip() == '':
                        # 如果没有专门的进出口城市字段，从始发地和目的地构建
                        if hasattr(format_import_export_cities_data, 'origin_col') and hasattr(format_import_export_cities_data, 'dest_col'):
                            origin = getattr(format_import_export_cities_data, 'origin_col', '未知')
                            dest = getattr(format_import_export_cities_data, 'dest_col', '未知')
                            return f"{origin}-{dest}"
                        return '未知'
                    
                    return str(row).strip()
                
                # 应用进出口城市-城市处理
                if 'import_export_cities' in display_df.columns:
                    display_df['import_export_cities'] = display_df['import_export_cities'].apply(format_import_export_cities_data)
                else:
                    # 如果没有专门的进出口城市字段，从始发地和目的地构建
                    if 'origin' in display_df.columns and 'destination' in display_df.columns:
                        display_df['import_export_cities'] = display_df.apply(
                            lambda row: f"{row['origin']}-{row['destination']}", axis=1
                        )
                
                # 优化列名显示（根据实际数据字段）
                column_mapping = {
                        'airline': '✈️ 航空公司',
                        'reg': '🏷️ 注册号',
                        'aircraft': '🛩️ 机型',
                        'age': '📅 机龄',
                        '航线类型': '🌍 航线类型',
                        'direction': '📍 方向',
                        'origin': '🛫 始发地',
                        '中转站': '🔄 中转站',
                        'destination': '🛬 目的地',
                        'flight_time': '⏱️ 飞行时长',
                        'flight_distance': '📏 飞行距离',
                        'speed': '🚀 飞行速度',
                        '中转地分析': '🔀 中转地分析',
                        'remarks': '📝 备注',
                        'city_route': '🏙️ 城市航线',
                        'airport_route': '🛫 机场航线',
                        'iata_route': '✈️ 机场代码',
                        'weekly_frequency': '📊 每周班次',
                        '进出口类型': '📊 进出口类型',
                        '每周往返班次': '🔄 每周往返班次'
                }
                
                # 按照用户指定的顺序显示列
                desired_order = [
                    '✈️ 航空公司',
                    '🏷️ 注册号', 
                    '🛩️ 机型',
                    '📅 机龄',
                    '🌍 航线类型',
                    '📍 方向',
                    '🛫 始发地',
                    '🔄 中转站',
                    '🛬 目的地',
                    '⏱️ 飞行时长',
                    '📏 飞行距离',
                    '🚀 飞行速度',
                    '🔀 中转地分析',
                    '📝 备注'
                ]
                
                # 只显示实际存在的列，按指定顺序排列
                display_columns = []
                for desired_col in desired_order:
                    # 找到对应的原始列名
                    for col_key, col_display in column_mapping.items():
                        if col_display == desired_col and col_key in display_df.columns:
                            display_columns.append(col_display)
                            break
                
                # 清理飞行距离列的空值，防止转换错误
                if 'flight_distance' in display_df.columns:
                    # 先转换为字符串类型
                    display_df['flight_distance'] = display_df['flight_distance'].astype(str)
                    # 处理各种空值情况
                    display_df['flight_distance'] = display_df['flight_distance'].replace(['nan', 'NaN', 'None', '', ' '], '未知')
                    # 再次填充可能的空值
                    display_df['flight_distance'] = display_df['flight_distance'].fillna('未知')
                    # 确保所有值都是字符串类型，避免Arrow转换错误
                    display_df['flight_distance'] = display_df['flight_distance'].apply(lambda x: str(x) if pd.notna(x) else '未知')
                
                # 清理其他可能导致类型转换错误的列
                for col in display_df.columns:
                    if display_df[col].dtype == 'object':
                        # 将所有object类型的列转换为字符串，避免混合类型
                        display_df[col] = display_df[col].astype(str)
                        display_df[col] = display_df[col].replace(['nan', 'NaN', 'None'], '')
                        display_df[col] = display_df[col].fillna('')
                
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
                
                # 添加详细统计信息（移出列布局，使其占用全宽度）
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
                    height=600  # 增加表格高度以显示更多数据
                )
                
                # 显示数据统计信息和数据来源说明
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.info(f"📊 当前显示 {len(display_df_renamed)} 条航线记录")
                with col2:
                    with st.expander("📋 数据来源说明"):
                        st.markdown("""
                        **数据来源**：
                        - 📊 每周班次：来自原始Excel数据源
                        - ✈️ 机场代码：来自Excel "机场—机场" 列
                        - 🏙️ 城市航线：来自Excel "城市—城市" 列
                        - 📏 飞行距离：来自Excel原始数据或系统计算
                        - ⏱️ 飞行时长：来自Excel原始数据或系统计算
                        """)
            
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