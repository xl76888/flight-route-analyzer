# -*- coding: utf-8 -*-
"""
Google Maps API 配置文件
用于3D地图功能的API密钥管理
"""

import os
import streamlit as st

class GoogleMapsConfig:
    """Google Maps API配置管理类"""
    
    def __init__(self):
        self.api_key = None
        self.map_id = None
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        # 优先从Streamlit secrets加载
        try:
            self.api_key = st.secrets.get("GOOGLE_MAPS_API_KEY")
            self.map_id = st.secrets.get("GOOGLE_MAPS_MAP_ID")
        except:
            pass
        
        # 从环境变量加载
        if not self.api_key:
            self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
        if not self.map_id:
            self.map_id = os.getenv("GOOGLE_MAPS_MAP_ID")
        
        # 使用默认占位符
        if not self.api_key:
            self.api_key = "AIzaSyBoAqo1lCI2FAQIY7A0jTlXI79mC2SO4Kw"
        
        if not self.map_id:
            self.map_id = "45c4f1595b0cd27f9feda952"
    
    def is_configured(self) -> bool:
        """检查是否已正确配置"""
        return (self.api_key and 
                self.api_key not in ["YOUR_GOOGLE_MAPS_API_KEY", "your_api_key_here"] and
                len(self.api_key) > 20 and
                self.map_id and 
                self.map_id not in ["YOUR_MAP_ID", "your_map_id_here"] and
                len(self.map_id) > 10)
    
    def get_config_instructions(self) -> str:
        """获取配置说明"""
        return """
## 🔧 Google Maps API 配置说明

要使用3D地图功能，需要配置Google Maps API密钥：

### 1. 获取API密钥
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用以下API：
   - Maps JavaScript API
   - Maps 3D API (beta)
4. 创建API密钥并设置适当的限制

### 2. 配置方法

**方法一：Streamlit Secrets（推荐）**
在项目根目录创建 `.streamlit/secrets.toml` 文件：
```toml
GOOGLE_MAPS_API_KEY = "your_api_key_here"
GOOGLE_MAPS_MAP_ID = "your_map_id_here"
```

**方法二：环境变量**
```bash
export GOOGLE_MAPS_API_KEY="your_api_key_here"
export GOOGLE_MAPS_MAP_ID="your_map_id_here"
```

### 3. 地图ID配置
1. 在Google Cloud Console中创建地图样式
2. 启用3D功能
3. 获取地图ID

### 4. 注意事项
- API密钥需要启用计费账户
- 建议设置API密钥的使用限制
- 3D Maps功能目前处于beta阶段
        """
    
    def show_config_status(self):
        """显示配置状态"""
        if self.is_configured():
            st.success("✅ Google Maps API已配置")
            return True
        else:
            st.warning("⚠️ Google Maps API未配置")
            
            with st.expander("📖 查看配置说明"):
                st.markdown(self.get_config_instructions())
            
            st.info("💡 配置完成后，3D地图功能将自动启用")
            return False

# 创建全局配置实例
google_maps_config = GoogleMapsConfig()

def get_api_key() -> str:
    """获取API密钥"""
    return google_maps_config.api_key

def get_map_id() -> str:
    """获取地图ID"""
    return google_maps_config.map_id

def is_maps_configured() -> bool:
    """检查Maps是否已配置"""
    return google_maps_config.is_configured()

def show_maps_config_status() -> bool:
    """显示Maps配置状态"""
    return google_maps_config.show_config_status()