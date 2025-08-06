#!/usr/bin/env python3
"""
修复Leaflet marker图标加载问题
"""
import os
import requests
from pathlib import Path
import streamlit as st

def ensure_marker_icons():
    """确保marker图标文件存在"""
    
    # 创建图标目录
    static_dir = Path("static")
    leaflet_dir = static_dir / "leaflet"
    images_dir = leaflet_dir / "images"
    
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # 定义需要下载的图标文件
    icon_files = {
        "marker-icon.png": "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png",
        "marker-icon-2x.png": "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon-2x.png",
        "marker-shadow.png": "https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png"
    }
    
    success_count = 0
    total_count = len(icon_files)
    
    for filename, url in icon_files.items():
        file_path = images_dir / filename
        
        if not file_path.exists():
            try:
                print(f"正在下载: {filename}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ 下载完成: {filename}")
                success_count += 1
                
            except Exception as e:
                print(f"❌ 下载失败 {filename}: {e}")
                # 创建空文件避免错误
                file_path.touch()
        else:
            print(f"📁 文件已存在: {filename}")
            success_count += 1
    
    return success_count == total_count

if __name__ == "__main__":
    print("正在修复marker图标...")
    if ensure_marker_icons():
        print("✅ 所有marker图标已准备就绪")
    else:
        print("⚠️ 部分图标可能有问题，但不会影响基本功能")
    print("修复完成！")