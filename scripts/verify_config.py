#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps API 配置验证脚本
用于检查API密钥配置状态和安全性
"""

import os
import sys
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import streamlit as st
    from config.google_maps_config import google_maps_config
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在项目虚拟环境中运行此脚本")
    sys.exit(1)

def check_secrets_file():
    """检查secrets.toml文件"""
    secrets_path = project_root / ".streamlit" / "secrets.toml"
    
    print("\n🔍 检查Streamlit Secrets配置...")
    
    if not secrets_path.exists():
        print("❌ secrets.toml文件不存在")
        return False
    
    print(f"✅ secrets.toml文件存在: {secrets_path}")
    
    # 检查文件权限
    try:
        with open(secrets_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "GOOGLE_MAPS_API_KEY" in content:
                print("✅ 找到GOOGLE_MAPS_API_KEY配置")
            else:
                print("❌ 未找到GOOGLE_MAPS_API_KEY配置")
                return False
                
            if "GOOGLE_MAPS_MAP_ID" in content:
                print("✅ 找到GOOGLE_MAPS_MAP_ID配置")
            else:
                print("⚠️ 未找到GOOGLE_MAPS_MAP_ID配置（可选）")
                
    except Exception as e:
        print(f"❌ 读取secrets.toml失败: {e}")
        return False
    
    return True

def check_gitignore():
    """检查.gitignore配置"""
    gitignore_path = project_root / ".gitignore"
    
    print("\n🔍 检查.gitignore安全配置...")
    
    if not gitignore_path.exists():
        print("⚠️ .gitignore文件不存在")
        return False
    
    try:
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        security_patterns = [
            ".streamlit/secrets.toml",
            ".env",
            "api_keys"
        ]
        
        missing_patterns = []
        for pattern in security_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"⚠️ .gitignore缺少安全配置: {', '.join(missing_patterns)}")
        else:
            print("✅ .gitignore安全配置完整")
            
    except Exception as e:
        print(f"❌ 读取.gitignore失败: {e}")
        return False
    
    return True

def validate_api_key(api_key):
    """验证API密钥格式和有效性"""
    print("\n🔍 验证API密钥...")
    
    # 检查格式
    if not api_key or api_key == "YOUR_GOOGLE_MAPS_API_KEY":
        print("❌ API密钥未配置或使用默认占位符")
        return False
    
    if not api_key.startswith("AIza"):
        print("❌ API密钥格式不正确（应以'AIza'开头）")
        return False
    
    if len(api_key) != 39:
        print(f"⚠️ API密钥长度异常（当前: {len(api_key)}，标准: 39）")
    
    print(f"✅ API密钥格式正确: {api_key[:10]}...{api_key[-4:]}")
    
    # 测试API可用性
    try:
        test_url = f"https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=maps3d"
        response = requests.head(test_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ API密钥验证成功")
            return True
        else:
            print(f"❌ API密钥验证失败 (HTTP {response.status_code})")
            return False
            
    except requests.RequestException as e:
        print(f"⚠️ 网络测试失败: {e}")
        print("请检查网络连接或手动验证API密钥")
        return None

def check_environment():
    """检查运行环境"""
    print("\n🔍 检查运行环境...")
    
    # Python版本
    python_version = sys.version.split()[0]
    print(f"Python版本: {python_version}")
    
    # 虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 运行在虚拟环境中")
    else:
        print("⚠️ 未检测到虚拟环境")
    
    # 必要的包
    required_packages = ['streamlit', 'requests', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少必要包: {', '.join(missing_packages)}")
        return False
    else:
        print("✅ 所有必要包已安装")
    
    return True

def main():
    """主函数"""
    print("🚀 Google Maps API 配置验证")
    print("=" * 50)
    
    # 检查环境
    env_ok = check_environment()
    
    # 检查配置文件
    secrets_ok = check_secrets_file()
    gitignore_ok = check_gitignore()
    
    # 验证API密钥
    api_key_ok = None
    if secrets_ok:
        try:
            api_key = google_maps_config.api_key
            api_key_ok = validate_api_key(api_key)
        except Exception as e:
            print(f"❌ 获取API密钥失败: {e}")
            api_key_ok = False
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 配置验证总结")
    print("=" * 50)
    
    checks = [
        ("运行环境", env_ok),
        ("Secrets配置", secrets_ok),
        ("安全配置", gitignore_ok),
        ("API密钥", api_key_ok)
    ]
    
    all_passed = True
    for name, status in checks:
        if status is True:
            print(f"✅ {name}: 通过")
        elif status is False:
            print(f"❌ {name}: 失败")
            all_passed = False
        else:
            print(f"⚠️ {name}: 警告")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有检查通过！3D地图功能已就绪")
        print("\n💡 下一步:")
        print("1. 启动应用: streamlit run web_app.py")
        print("2. 在侧边栏选择'3D地图'")
        print("3. 上传航线数据并体验3D可视化")
    else:
        print("⚠️ 存在配置问题，请根据上述提示进行修复")
        print("\n📖 参考文档: 3D_MAP_SETUP.md")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 未预期错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)