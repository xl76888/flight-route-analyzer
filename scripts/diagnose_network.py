#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps API 网络连接诊断脚本
用于排查API加载问题和网络连接状态
"""

import os
import sys
import requests
import socket
import time
from pathlib import Path
from urllib.parse import urlparse

# 配置代理设置
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from config.google_maps_config import get_api_key, get_map_id
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在项目虚拟环境中运行此脚本")
    sys.exit(1)

def test_dns_resolution():
    """测试DNS解析"""
    print("\n🔍 测试DNS解析...")
    
    test_domains = [
        "maps.googleapis.com",
        "maps.google.com",
        "google.com"
    ]
    
    results = []
    for domain in test_domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"✅ {domain} -> {ip}")
            results.append(True)
        except socket.gaierror as e:
            print(f"❌ {domain} -> DNS解析失败: {e}")
            results.append(False)
    
    return all(results)

def test_network_connectivity():
    """测试网络连通性"""
    print("\n🔍 测试网络连通性...")
    
    test_urls = [
        "https://www.google.com",
        "https://maps.googleapis.com",
        "https://maps.google.com"
    ]
    
    results = []
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10, proxies=proxies)
            if response.status_code == 200:
                print(f"✅ {url} -> HTTP {response.status_code}")
                results.append(True)
            else:
                print(f"⚠️ {url} -> HTTP {response.status_code}")
                results.append(False)
        except requests.RequestException as e:
            print(f"❌ {url} -> 连接失败: {e}")
            results.append(False)
    
    return any(results)

def test_google_maps_api():
    """测试Google Maps API"""
    print("\n🔍 测试Google Maps API...")
    
    api_key = get_api_key()
    map_id = get_map_id()
    
    print(f"API密钥: {api_key[:10]}...{api_key[-4:]}")
    print(f"地图ID: {map_id}")
    
    # 测试JavaScript API加载
    js_api_url = f"https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=maps3d"
    
    try:
        response = requests.head(js_api_url, timeout=15, proxies=proxies)
        if response.status_code == 200:
            print(f"✅ JavaScript API -> HTTP {response.status_code}")
            return True
        else:
            print(f"❌ JavaScript API -> HTTP {response.status_code}")
            if response.status_code == 403:
                print("   可能原因: API密钥无效或权限不足")
            elif response.status_code == 400:
                print("   可能原因: 请求参数错误")
            return False
    except requests.RequestException as e:
        print(f"❌ JavaScript API -> 请求失败: {e}")
        return False

def test_proxy_settings():
    """检查代理设置"""
    print("\n🔍 检查代理设置...")
    
    # 检查环境变量中的代理设置
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxy_found = False
    
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"🔧 发现代理设置: {var} = {value}")
            proxy_found = True
    
    if not proxy_found:
        print("ℹ️ 未发现环境变量代理设置")
    
    # 检查Git代理设置
    try:
        import subprocess
        result = subprocess.run(['git', 'config', '--global', '--get', 'http.proxy'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            print(f"🔧 Git HTTP代理: {result.stdout.strip()}")
            proxy_found = True
        
        result = subprocess.run(['git', 'config', '--global', '--get', 'https.proxy'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            print(f"🔧 Git HTTPS代理: {result.stdout.strip()}")
            proxy_found = True
    except Exception as e:
        print(f"⚠️ 检查Git代理设置失败: {e}")
    
    return proxy_found

def test_firewall_ports():
    """测试防火墙端口"""
    print("\n🔍 测试防火墙端口...")
    
    test_ports = [
        ("maps.googleapis.com", 443),
        ("google.com", 443),
        ("google.com", 80)
    ]
    
    results = []
    for host, port in test_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {host}:{port} -> 连接成功")
                results.append(True)
            else:
                print(f"❌ {host}:{port} -> 连接失败 (错误码: {result})")
                results.append(False)
        except Exception as e:
            print(f"❌ {host}:{port} -> 测试失败: {e}")
            results.append(False)
    
    return any(results)

def get_system_info():
    """获取系统信息"""
    print("\n🔍 系统信息...")
    
    import platform
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version.split()[0]}")
    
    # 检查网络适配器
    try:
        import subprocess
        if platform.system() == "Windows":
            result = subprocess.run(['ipconfig', '/all'], 
                                  capture_output=True, text=True, timeout=10)
            if "DNS" in result.stdout:
                print("✅ 网络适配器配置正常")
            else:
                print("⚠️ 网络适配器配置可能有问题")
    except Exception as e:
        print(f"⚠️ 无法获取网络适配器信息: {e}")

def provide_solutions(test_results):
    """提供解决方案"""
    print("\n" + "=" * 50)
    print("💡 问题诊断和解决方案")
    print("=" * 50)
    
    dns_ok, network_ok, api_ok, proxy_found, ports_ok = test_results
    
    if not dns_ok:
        print("\n🔧 DNS解析问题解决方案:")
        print("1. 更换DNS服务器:")
        print("   - 8.8.8.8 (Google DNS)")
        print("   - 114.114.114.114 (国内DNS)")
        print("2. 刷新DNS缓存:")
        print("   Windows: ipconfig /flushdns")
        print("   Linux: sudo systemctl restart systemd-resolved")
    
    if not network_ok:
        print("\n🔧 网络连接问题解决方案:")
        print("1. 检查网络连接是否正常")
        print("2. 尝试使用VPN或代理")
        print("3. 检查防火墙设置")
        print("4. 联系网络管理员")
    
    if not api_ok:
        print("\n🔧 Google Maps API问题解决方案:")
        print("1. 验证API密钥是否正确")
        print("2. 检查API密钥权限和限制")
        print("3. 确认已启用必要的API服务:")
        print("   - Maps JavaScript API")
        print("   - Maps 3D API")
        print("4. 检查API配额是否用完")
        print("5. 验证地图ID是否正确")
    
    if proxy_found:
        print("\n🔧 代理设置建议:")
        print("1. 确认代理服务器正常工作")
        print("2. 检查代理认证信息")
        print("3. 尝试临时禁用代理测试")
    
    if not ports_ok:
        print("\n🔧 端口连接问题解决方案:")
        print("1. 检查防火墙设置")
        print("2. 确认端口443和80未被阻止")
        print("3. 联系网络管理员开放必要端口")
    
    print("\n🌐 浏览器端解决方案:")
    print("1. 清除浏览器缓存和Cookie")
    print("2. 禁用浏览器扩展")
    print("3. 尝试无痕模式")
    print("4. 检查浏览器控制台错误信息")
    print("5. 确保浏览器支持WebGL")

def main():
    """主函数"""
    print("🚀 Google Maps API 网络连接诊断")
    print("=" * 50)
    
    # 执行各项测试
    dns_ok = test_dns_resolution()
    network_ok = test_network_connectivity()
    api_ok = test_google_maps_api()
    proxy_found = test_proxy_settings()
    ports_ok = test_firewall_ports()
    
    # 获取系统信息
    get_system_info()
    
    # 总结测试结果
    print("\n" + "=" * 50)
    print("📋 诊断结果总结")
    print("=" * 50)
    
    tests = [
        ("DNS解析", dns_ok),
        ("网络连通性", network_ok),
        ("Google Maps API", api_ok),
        ("端口连接", ports_ok)
    ]
    
    all_passed = True
    for name, status in tests:
        if status:
            print(f"✅ {name}: 正常")
        else:
            print(f"❌ {name}: 异常")
            all_passed = False
    
    if proxy_found:
        print(f"🔧 代理设置: 已检测到")
    
    # 提供解决方案
    provide_solutions((dns_ok, network_ok, api_ok, proxy_found, ports_ok))
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 网络连接正常！如果仍有问题，请检查浏览器端设置")
    else:
        print("⚠️ 发现网络连接问题，请根据上述建议进行排查")
    
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