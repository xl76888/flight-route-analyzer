import os
import requests
from pathlib import Path
import streamlit as st

class LocalResourceManager:
    """本地静态资源管理器"""
    
    def __init__(self, static_dir="static"):
        self.static_dir = Path(static_dir)
        self.leaflet_dir = self.static_dir / "leaflet"
        self.leaflet_version = "1.9.4"
        
    def ensure_directories(self):
        """确保目录存在"""
        self.leaflet_dir.mkdir(parents=True, exist_ok=True)
        (self.leaflet_dir / "images").mkdir(exist_ok=True)
    
    def download_leaflet_resources(self):
        """下载Leaflet资源"""
        base_url = f"https://unpkg.com/leaflet@{self.leaflet_version}/dist"
        
        resources = {
            "leaflet.css": f"{base_url}/leaflet.css",
            "leaflet.js": f"{base_url}/leaflet.js",
            "images/layers.png": f"{base_url}/images/layers.png",
            "images/layers-2x.png": f"{base_url}/images/layers-2x.png",
            "images/marker-icon.png": f"{base_url}/images/marker-icon.png",
            "images/marker-icon-2x.png": f"{base_url}/images/marker-icon-2x.png",
            "images/marker-shadow.png": f"{base_url}/images/marker-shadow.png"
        }
        
        self.ensure_directories()
        
        success_count = 0
        total_count = len(resources)
        
        for filename, url in resources.items():
            file_path = self.leaflet_dir / filename
            if not file_path.exists():
                try:
                    st.info(f"正在下载: {filename}")
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    st.success(f"✅ 下载完成: {filename} ({len(response.content)} bytes)")
                    success_count += 1
                except Exception as e:
                    st.error(f"❌ 下载失败 {filename}: {e}")
            else:
                st.info(f"📁 文件已存在: {filename}")
                success_count += 1
        
        if success_count == total_count:
            st.success(f"🎉 所有资源下载完成! ({success_count}/{total_count})")
        else:
            st.warning(f"⚠️ 部分资源下载失败 ({success_count}/{total_count})")
        
        return success_count == total_count
    
    def check_resources_available(self):
        """检查本地资源是否可用"""
        required_files = ["leaflet.css", "leaflet.js"]
        return all((self.leaflet_dir / f).exists() for f in required_files)
    
    def get_resource_info(self):
        """获取资源信息"""
        info = {
            "leaflet_version": self.leaflet_version,
            "static_dir": str(self.static_dir),
            "leaflet_dir": str(self.leaflet_dir),
            "resources_available": self.check_resources_available()
        }
        
        # 检查各个文件的存在状态
        files_status = {}
        required_files = [
            "leaflet.css", "leaflet.js",
            "images/layers.png", "images/layers-2x.png",
            "images/marker-icon.png", "images/marker-icon-2x.png",
            "images/marker-shadow.png"
        ]
        
        for filename in required_files:
            file_path = self.leaflet_dir / filename
            files_status[filename] = {
                "exists": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0
            }
        
        info["files_status"] = files_status
        return info
    
    def load_local_leaflet_css(self):
        """加载本地Leaflet CSS"""
        css_file = self.leaflet_dir / "leaflet.css"
        if css_file.exists():
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                # 修复CSS中的相对路径
                css_content = css_content.replace('url(images/', f'url(./static/leaflet/images/')
                return css_content
            except Exception as e:
                st.error(f"读取CSS文件失败: {e}")
                return None
        return None
    
    def inject_local_resources(self):
        """注入本地资源到页面"""
        if self.check_resources_available():
            css_content = self.load_local_leaflet_css()
            if css_content:
                st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
                st.success("✅ 本地Leaflet CSS已加载")
                return True
            else:
                st.error("❌ 本地CSS加载失败")
                return False
        else:
            st.warning("⚠️ 本地资源不可用")
            return False

# 创建全局实例
resource_manager = LocalResourceManager()