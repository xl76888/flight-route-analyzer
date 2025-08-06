#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google服务网络连接测试工具
测试各种Google Maps相关服务的网络可达性
"""

import requests
import socket
import time
from datetime import datetime
import json
from pathlib import Path

class GoogleConnectivityTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "dns_resolution": {},
            "http_connectivity": {},
            "api_endpoints": {},
            "recommendations": []
        }
        
        # 测试的Google服务端点
        self.test_endpoints = {
            "maps_api": "https://maps.googleapis.com/maps/api/geocode/json",
            "maps_js_api": "https://maps.googleapis.com/maps/api/js",
            "fonts_api": "https://fonts.googleapis.com",
            "google_main": "https://www.google.com",
            "googleapis_main": "https://googleapis.com"
        }
        
        # 需要DNS解析测试的域名
        self.dns_hosts = [
            "maps.googleapis.com",
            "fonts.googleapis.com",
            "www.google.com",
            "googleapis.com"
        ]
    
    def test_dns_resolution(self):
        """测试DNS解析"""
        print("\n🔍 测试DNS解析...")
        
        for host in self.dns_hosts:
            try:
                start_time = time.time()
                ip_addresses = socket.gethostbyname_ex(host)[2]
                resolve_time = (time.time() - start_time) * 1000
                
                self.results["dns_resolution"][host] = {
                    "status": "success",
                    "ip_addresses": ip_addresses,
                    "resolve_time_ms": round(resolve_time, 2)
                }
                
                print(f"✅ {host}: {ip_addresses[0]} ({resolve_time:.1f}ms)")
                
            except socket.gaierror as e:
                self.results["dns_resolution"][host] = {
                    "status": "failed",
                    "error": str(e)
                }
                print(f"❌ {host}: DNS解析失败 - {str(e)}")
            except Exception as e:
                self.results["dns_resolution"][host] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"⚠️ {host}: 解析异常 - {str(e)}")
    
    def test_http_connectivity(self):
        """测试HTTP连接性"""
        print("\n🌐 测试HTTP连接性...")
        
        for name, url in self.test_endpoints.items():
            try:
                start_time = time.time()
                response = requests.head(url, timeout=10, allow_redirects=True)
                response_time = (time.time() - start_time) * 1000
                
                self.results["http_connectivity"][name] = {
                    "status": "success",
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                    "headers": dict(response.headers)
                }
                
                status_emoji = "✅" if response.status_code < 400 else "⚠️"
                print(f"{status_emoji} {name}: {response.status_code} ({response_time:.1f}ms)")
                
            except requests.exceptions.Timeout:
                self.results["http_connectivity"][name] = {
                    "status": "timeout",
                    "error": "请求超时"
                }
                print(f"⏱️ {name}: 连接超时")
                
            except requests.exceptions.ConnectionError as e:
                self.results["http_connectivity"][name] = {
                    "status": "connection_error",
                    "error": str(e)
                }
                print(f"❌ {name}: 连接错误 - {str(e)[:100]}...")
                
            except Exception as e:
                self.results["http_connectivity"][name] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"⚠️ {name}: 未知错误 - {str(e)[:100]}...")
    
    def test_api_endpoints(self):
        """测试具体的API端点"""
        print("\n🔧 测试API端点功能...")
        
        # 测试Geocoding API
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': 'Beijing, China',
                'key': 'test_key'  # 使用测试密钥
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                if data.get('status') == 'REQUEST_DENIED':
                    self.results["api_endpoints"]["geocoding"] = {
                        "status": "api_key_required",
                        "message": "API需要有效密钥，但连接正常"
                    }
                    print("✅ Geocoding API: 连接正常，需要有效API密钥")
                else:
                    self.results["api_endpoints"]["geocoding"] = {
                        "status": "success",
                        "response_status": data.get('status')
                    }
                    print(f"✅ Geocoding API: 响应状态 {data.get('status')}")
            else:
                self.results["api_endpoints"]["geocoding"] = {
                    "status": "http_error",
                    "status_code": response.status_code
                }
                print(f"⚠️ Geocoding API: HTTP {response.status_code}")
                
        except Exception as e:
            self.results["api_endpoints"]["geocoding"] = {
                "status": "error",
                "error": str(e)
            }
            print(f"❌ Geocoding API: 测试失败 - {str(e)}")
        
        # 测试Maps JavaScript API加载
        try:
            url = "https://maps.googleapis.com/maps/api/js"
            params = {'key': 'test_key'}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                self.results["api_endpoints"]["maps_js"] = {
                    "status": "success",
                    "content_type": response.headers.get('content-type', '')
                }
                print("✅ Maps JavaScript API: 加载正常")
            else:
                self.results["api_endpoints"]["maps_js"] = {
                    "status": "http_error",
                    "status_code": response.status_code
                }
                print(f"⚠️ Maps JavaScript API: HTTP {response.status_code}")
                
        except Exception as e:
            self.results["api_endpoints"]["maps_js"] = {
                "status": "error",
                "error": str(e)
            }
            print(f"❌ Maps JavaScript API: 测试失败 - {str(e)}")
    
    def analyze_results(self):
        """分析测试结果并生成建议"""
        print("\n📊 分析测试结果...")
        
        # 统计成功率
        dns_success = sum(1 for result in self.results["dns_resolution"].values() 
                         if result["status"] == "success")
        dns_total = len(self.results["dns_resolution"])
        
        http_success = sum(1 for result in self.results["http_connectivity"].values() 
                          if result["status"] == "success")
        http_total = len(self.results["http_connectivity"])
        
        api_success = sum(1 for result in self.results["api_endpoints"].values() 
                         if result["status"] in ["success", "api_key_required"])
        api_total = len(self.results["api_endpoints"])
        
        # 生成总体状态
        if dns_success == dns_total and http_success >= http_total * 0.8 and api_success >= api_total * 0.8:
            self.results["overall_status"] = "excellent"
        elif dns_success >= dns_total * 0.8 and http_success >= http_total * 0.6:
            self.results["overall_status"] = "good"
        elif dns_success >= dns_total * 0.5:
            self.results["overall_status"] = "limited"
        else:
            self.results["overall_status"] = "poor"
        
        # 生成建议
        recommendations = []
        
        if dns_success < dns_total:
            recommendations.append("检查DNS设置，考虑使用公共DNS（如8.8.8.8）")
        
        if http_success < http_total * 0.8:
            recommendations.append("检查防火墙设置，确保允许HTTPS连接")
            recommendations.append("如果在企业网络中，联系网络管理员检查代理设置")
        
        timeout_count = sum(1 for result in self.results["http_connectivity"].values() 
                           if result["status"] == "timeout")
        if timeout_count > 0:
            recommendations.append("网络延迟较高，考虑使用VPN或更换网络")
        
        if api_success < api_total:
            recommendations.append("API端点访问受限，检查API密钥配置")
        
        if not recommendations:
            recommendations.append("网络连接状态良好，Google Maps API应该能正常工作")
        
        self.results["recommendations"] = recommendations
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("📋 Google服务网络连接测试报告")
        print("="*60)
        
        # 总体状态
        status_emoji = {
            "excellent": "🟢",
            "good": "🟡",
            "limited": "🟠",
            "poor": "🔴"
        }
        
        print(f"\n🌐 总体连接状态: {status_emoji.get(self.results['overall_status'], '❓')} {self.results['overall_status'].upper()}")
        
        # DNS解析结果
        print("\n🔍 DNS解析结果:")
        for host, result in self.results["dns_resolution"].items():
            if result["status"] == "success":
                print(f"  ✅ {host}: {result['ip_addresses'][0]} ({result['resolve_time_ms']}ms)")
            else:
                print(f"  ❌ {host}: {result.get('error', '失败')}")
        
        # HTTP连接结果
        print("\n🌐 HTTP连接结果:")
        for name, result in self.results["http_connectivity"].items():
            if result["status"] == "success":
                print(f"  ✅ {name}: HTTP {result['status_code']} ({result['response_time_ms']}ms)")
            elif result["status"] == "timeout":
                print(f"  ⏱️ {name}: 连接超时")
            else:
                print(f"  ❌ {name}: {result.get('error', '连接失败')[:50]}...")
        
        # API端点结果
        print("\n🔧 API端点测试:")
        for name, result in self.results["api_endpoints"].items():
            if result["status"] == "success":
                print(f"  ✅ {name}: 正常工作")
            elif result["status"] == "api_key_required":
                print(f"  🔑 {name}: 需要有效API密钥（连接正常）")
            else:
                print(f"  ❌ {name}: {result.get('error', '测试失败')[:50]}...")
        
        # 建议
        print("\n💡 建议:")
        for i, rec in enumerate(self.results["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*60)
    
    def save_report(self):
        """保存测试报告"""
        report_file = Path("google_connectivity_report.json")
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            print(f"\n📄 详细报告已保存: {report_file.absolute()}")
            return True
        except Exception as e:
            print(f"❌ 保存报告失败: {str(e)}")
            return False
    
    def run_full_test(self):
        """运行完整的连接测试"""
        print("🌐 Google服务网络连接测试工具")
        print("="*60)
        
        # 执行各项测试
        self.test_dns_resolution()
        self.test_http_connectivity()
        self.test_api_endpoints()
        
        # 分析结果
        self.analyze_results()
        
        # 显示摘要
        self.print_summary()
        
        # 保存报告
        self.save_report()
        
        return self.results["overall_status"]

def main():
    """主函数"""
    tester = GoogleConnectivityTester()
    
    try:
        status = tester.run_full_test()
        
        print("\n✅ 测试完成！")
        
        if status == "excellent":
            print("🎉 网络连接状态优秀，Google Maps API应该能完美工作！")
        elif status == "good":
            print("👍 网络连接状态良好，Google Maps API应该能正常工作。")
        elif status == "limited":
            print("⚠️ 网络连接受限，可能影响Google Maps API的性能。")
        else:
            print("❌ 网络连接存在问题，需要解决网络配置。")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断了测试过程")
    except Exception as e:
        print(f"\n❌ 测试过程中发生意外错误: {str(e)}")

if __name__ == "__main__":
    main()