#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D Maps API配置验证脚本
用于检查Google Cloud Console中的API配置是否正确
"""

import requests
import json
import os
from pathlib import Path

def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / '.streamlit' / 'secrets.toml'
    
    if not config_path.exists():
        print("❌ 配置文件不存在：.streamlit/secrets.toml")
        return None
    
    # 简单解析TOML文件
    config = {}
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"')
                config[key] = value
    
    return config

def check_api_key_format(api_key):
    """检查API密钥格式"""
    print("\n🔑 检查API密钥格式...")
    
    if not api_key:
        print("❌ API密钥为空")
        return False
    
    if not api_key.startswith('AIza'):
        print("❌ API密钥格式错误（应以'AIza'开头）")
        return False
    
    if len(api_key) < 35:
        print("❌ API密钥长度不足")
        return False
    
    print("✅ API密钥格式正确")
    return True

def check_maps_js_api(api_key):
    """检查Maps JavaScript API是否可用"""
    print("\n🗺️ 检查Maps JavaScript API...")
    
    test_url = f"https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=maps3d&v=beta"
    
    try:
        response = requests.head(test_url, timeout=10)
        if response.status_code == 200:
            print("✅ Maps JavaScript API可用")
            return True
        else:
            print(f"❌ Maps JavaScript API请求失败 (HTTP {response.status_code})")
            if response.status_code == 403:
                print("   可能原因：API密钥无效或权限不足")
            elif response.status_code == 400:
                print("   可能原因：请求参数错误")
            return False
    except requests.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False

def check_3d_maps_support(api_key):
    """检查3D Maps支持"""
    print("\n🏗️ 检查3D Maps API支持...")
    
    # 测试3D Maps特定的API端点
    test_url = f"https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=maps3d&v=beta&callback=test"
    
    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            content = response.text
            if 'maps3d' in content.lower() or 'gmp-map-3d' in content.lower():
                print("✅ 3D Maps API库可用")
                return True
            else:
                print("⚠️ 3D Maps API库可能未启用")
                return False
        else:
            print(f"❌ 3D Maps API请求失败 (HTTP {response.status_code})")
            return False
    except requests.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False

def check_map_id_format(map_id):
    """检查地图ID格式"""
    print("\n🆔 检查地图ID格式...")
    
    if not map_id:
        print("❌ 地图ID为空")
        return False
    
    if len(map_id) < 10:
        print("❌ 地图ID长度不足")
        return False
    
    print("✅ 地图ID格式正确")
    return True

def generate_cloud_console_checklist():
    """生成Google Cloud Console检查清单"""
    print("\n📋 Google Cloud Console配置检查清单：")
    print("\n请确保在Google Cloud Console中完成以下配置：")
    print("\n1. 启用必要的API：")
    print("   ✓ Maps JavaScript API")
    print("   ✓ Maps 3D API (Beta)")
    print("   ✓ Geocoding API (可选)")
    print("\n2. API密钥配置：")
    print("   ✓ 创建API密钥")
    print("   ✓ 设置HTTP referrer限制（推荐）")
    print("   ✓ 限制API密钥只能访问必要的API")
    print("\n3. 计费设置：")
    print("   ✓ 启用计费账户")
    print("   ✓ 设置使用配额和预算提醒")
    print("\n4. 地图ID配置：")
    print("   ✓ 在Maps Management中创建地图ID")
    print("   ✓ 配置地图样式（可选）")
    print("\n5. 3D Maps特定设置：")
    print("   ✓ 确保项目有权访问3D Maps Beta功能")
    print("   ✓ 检查地区支持（3D Maps在某些地区可能不可用）")

def main():
    """主函数"""
    print("🔍 3D Maps API配置验证")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    if not config:
        return
    
    api_key = config.get('GOOGLE_MAPS_API_KEY')
    map_id = config.get('GOOGLE_MAPS_MAP_ID')
    
    # 执行检查
    checks = [
        check_api_key_format(api_key),
        check_map_id_format(map_id),
        check_maps_js_api(api_key),
        check_3d_maps_support(api_key)
    ]
    
    # 总结结果
    print("\n" + "=" * 50)
    print("📊 检查结果总结：")
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ 所有检查通过 ({passed}/{total})")
        print("\n🎉 配置看起来正确！如果3D地图仍无法加载，请检查：")
        print("   - 浏览器WebGL支持")
        print("   - 网络连接")
        print("   - 控制台错误信息")
    else:
        print(f"❌ 部分检查失败 ({passed}/{total})")
        generate_cloud_console_checklist()
    
    print("\n💡 提示：")
    print("   - 3D Maps目前处于Beta阶段，免费使用")
    print("   - 确保浏览器支持WebGL")
    print("   - 检查网络防火墙设置")

if __name__ == '__main__':
    main()