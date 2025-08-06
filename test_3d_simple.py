
import streamlit as st
import pandas as pd
from optimized_map3d_integration import render_optimized_3d_map

st.title("🌐 3D地图测试")

# 创建测试数据
test_data = [
    {
        'id': 'test_1',
        'start_airport': 'PEK',
        'end_airport': 'LAX',
        'start_airport_name': '北京首都国际机场',
        'end_airport_name': '洛杉矶国际机场',
        'start_lat': 40.0799,
        'start_lng': 116.6031,
        'end_lat': 33.9425,
        'end_lng': -118.4081,
        'frequency': 5,
        'airline': '中国国际航空',
        'aircraft_type': 'Boeing 777',
        'route_type': 'international',
        'direction': '出口',
        'is_bidirectional': False
    }
]

st.info(f"测试数据: {len(test_data)} 条航线")

try:
    result = render_optimized_3d_map(
        test_data,
        height=600,
        key="simple_test_3d_map",
        force_reload=True
    )
    
    if result:
        st.success("✅ 3D地图渲染成功！")
    else:
        st.warning("⚠️ 3D地图渲染返回None")
        
except Exception as e:
    st.error(f"❌ 3D地图渲染失败: {str(e)}")
    st.exception(e)
