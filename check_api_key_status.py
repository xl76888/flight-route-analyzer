#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps API密钥状态检查工具
自动诊断API密钥失效原因并提供解决方案
"""

import requests
import json
import time
from datetime import datetime
import os
from pathlib import Path

class APIKeyChecker:
    def __init__(self):
        self.config_file = Path(".streamlit/secrets.toml")
        self.api_key = None
        self.map_id = None
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "api_key_status": "unknown",
            "billing_status": "unknown",
            "quota_status": "unknown",
            "services_status": {},
            "recommendations": [],
            "errors": []
        }
    
    def load_config(self):
        """加载API配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单解析TOML格式
                    for line in content.split('\n'):
                        if 'GOOGLE_MAPS_API_KEY' in line and '=' in line:
                            self.api_key = line.split('=')[1].strip().strip('"\'')
                        elif 'GOOGLE_MAPS_MAP_ID' in line and '=' in line:
                            self.map_id = line.split('=')[1].strip().strip('"\'')
                
                if self.api_key:
                    print(f"✅ 成功加载API密钥: {self.api_key[:10]}...")
                    return True
                else:
                    self.results["errors"].append("配置文件中未找到有效的API密钥")
                    return False
            else:
                self.results["errors"].append("配置文件不存在")
                return False
        except Exception as e:
            self.results["errors"].append(f"加载配置失败: {str(e)}")
            return False
    
    def check_api_key_format(self):
        """检查API密钥格式"""
        print("\n🔍 检查API密钥格式...")
        
        if not self.api_key:
            self.results["errors"].append("API密钥为空")
            return False
        
        # Google Maps API密钥格式检查
        if not self.api_key.startswith('AIza'):
            self.results["errors"].append("API密钥格式错误：应以'AIza'开头")
            self.results["recommendations"].append("重新生成有效的Google Maps API密钥")
            return False
        
        if len(self.api_key) != 39:
            self.results["errors"].append(f"API密钥长度错误：当前{len(self.api_key)}字符，应为39字符")
            self.results["recommendations"].append("检查API密钥是否完整复制")
            return False
        
        print("✅ API密钥格式正确")
        return True
    
    def test_maps_javascript_api(self):
        """测试Maps JavaScript API可用性"""
        print("\n🗺️ 测试Maps JavaScript API...")
        
        try:
            # 测试Geocoding API（Maps JavaScript API的一部分）
            url = f"https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': 'Beijing, China',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                if data.get('status') == 'OK':
                    print("✅ Maps JavaScript API 正常工作")
                    self.results["services_status"]["maps_javascript_api"] = "active"
                    return True
                elif data.get('status') == 'REQUEST_DENIED':
                    error_msg = data.get('error_message', '未知错误')
                    print(f"❌ API请求被拒绝: {error_msg}")
                    self.results["errors"].append(f"API请求被拒绝: {error_msg}")
                    
                    # 分析具体错误原因
                    if 'billing' in error_msg.lower():
                        self.results["recommendations"].append("启用Google Cloud计费账户")
                    elif 'key' in error_msg.lower():
                        self.results["recommendations"].append("检查API密钥权限设置")
                    
                    return False
                elif data.get('status') == 'OVER_QUERY_LIMIT':
                    print("❌ 超出配额限制")
                    self.results["errors"].append("API配额已用完")
                    self.results["recommendations"].append("增加API配额限制或等待配额重置")
                    return False
                else:
                    print(f"⚠️ API返回状态: {data.get('status')}")
                    self.results["errors"].append(f"API状态异常: {data.get('status')}")
                    return False
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                self.results["errors"].append(f"HTTP请求失败: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
            self.results["errors"].append("网络请求超时")
            self.results["recommendations"].append("检查网络连接")
            return False
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            self.results["errors"].append(f"API测试异常: {str(e)}")
            return False
    
    def test_3d_maps_api(self):
        """测试3D Maps API可用性"""
        print("\n🏔️ 测试3D Maps API...")
        
        try:
            # 测试Maps JavaScript API的3D功能
            # 通过检查API密钥是否能访问高级功能
            url = f"https://maps.googleapis.com/maps/api/elevation/json"
            params = {
                'locations': '39.7391536,-104.9847034',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200 and data.get('status') == 'OK':
                print("✅ 3D Maps相关API正常工作")
                self.results["services_status"]["3d_maps_api"] = "active"
                return True
            else:
                print(f"⚠️ 3D Maps API状态: {data.get('status', 'unknown')}")
                self.results["services_status"]["3d_maps_api"] = "limited"
                return False
                
        except Exception as e:
            print(f"❌ 3D Maps API测试失败: {str(e)}")
            self.results["services_status"]["3d_maps_api"] = "error"
            return False
    
    def check_quota_status(self):
        """检查配额状态"""
        print("\n📊 检查配额状态...")
        
        try:
            # 通过多次小请求测试配额
            test_count = 3
            success_count = 0
            
            for i in range(test_count):
                url = f"https://maps.googleapis.com/maps/api/geocode/json"
                params = {
                    'address': f'Test {i}',
                    'key': self.api_key
                }
                
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') in ['OK', 'ZERO_RESULTS']:
                        success_count += 1
                    elif data.get('status') == 'OVER_QUERY_LIMIT':
                        print("❌ 配额已用完")
                        self.results["quota_status"] = "exceeded"
                        self.results["recommendations"].append("增加API配额或等待配额重置")
                        return False
                
                time.sleep(0.5)  # 避免触发速率限制
            
            if success_count == test_count:
                print("✅ 配额状态正常")
                self.results["quota_status"] = "normal"
                return True
            else:
                print(f"⚠️ 配额可能受限 ({success_count}/{test_count} 成功)")
                self.results["quota_status"] = "limited"
                return False
                
        except Exception as e:
            print(f"❌ 配额检查失败: {str(e)}")
            self.results["quota_status"] = "error"
            return False
    
    def analyze_billing_status(self):
        """分析计费状态"""
        print("\n💳 分析计费状态...")
        
        # 基于API响应分析计费状态
        has_billing_errors = any('billing' in error.lower() for error in self.results["errors"])
        has_quota_issues = self.results["quota_status"] in ["exceeded", "limited"]
        
        if has_billing_errors:
            self.results["billing_status"] = "disabled"
            self.results["recommendations"].append("启用Google Cloud计费账户")
            print("❌ 计费账户未启用或无效")
        elif has_quota_issues:
            self.results["billing_status"] = "limited"
            self.results["recommendations"].append("检查计费账户设置和配额限制")
            print("⚠️ 计费账户可能有限制")
        else:
            self.results["billing_status"] = "active"
            print("✅ 计费状态正常")
    
    def generate_recommendations(self):
        """生成修复建议"""
        print("\n💡 生成修复建议...")
        
        # 去重建议
        recommendations = list(set(self.results["recommendations"]))
        
        # 添加通用建议
        if self.results["errors"]:
            recommendations.extend([
                "检查Google Cloud Console中的API密钥设置",
                "验证项目是否关联到有效的计费账户",
                "确认所需的API服务已启用"
            ])
        
        self.results["recommendations"] = list(set(recommendations))
        
        # 设置总体状态
        if not self.results["errors"]:
            self.results["api_key_status"] = "healthy"
        elif len(self.results["errors"]) <= 2:
            self.results["api_key_status"] = "warning"
        else:
            self.results["api_key_status"] = "critical"
    
    def save_report(self):
        """保存诊断报告"""
        report_file = Path("api_key_diagnostic_report.json")
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            print(f"\n📄 诊断报告已保存: {report_file.absolute()}")
            return True
        except Exception as e:
            print(f"❌ 保存报告失败: {str(e)}")
            return False
    
    def print_summary(self):
        """打印诊断摘要"""
        print("\n" + "="*50)
        print("📋 API密钥诊断摘要")
        print("="*50)
        
        # 状态概览
        status_emoji = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "❌",
            "unknown": "❓"
        }
        
        print(f"🔑 API密钥状态: {status_emoji.get(self.results['api_key_status'], '❓')} {self.results['api_key_status'].upper()}")
        print(f"💳 计费状态: {status_emoji.get(self.results['billing_status'], '❓')} {self.results['billing_status'].upper()}")
        print(f"📊 配额状态: {status_emoji.get(self.results['quota_status'], '❓')} {self.results['quota_status'].upper()}")
        
        # 服务状态
        if self.results["services_status"]:
            print("\n🛠️ 服务状态:")
            for service, status in self.results["services_status"].items():
                emoji = "✅" if status == "active" else "⚠️" if status == "limited" else "❌"
                print(f"  {emoji} {service}: {status}")
        
        # 错误列表
        if self.results["errors"]:
            print("\n❌ 发现的问题:")
            for i, error in enumerate(self.results["errors"], 1):
                print(f"  {i}. {error}")
        
        # 修复建议
        if self.results["recommendations"]:
            print("\n💡 修复建议:")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"  {i}. {rec}")
        
        # 快速链接
        print("\n🔗 有用链接:")
        print("  • Google Cloud Console: https://console.cloud.google.com")
        print("  • API密钥管理: https://console.cloud.google.com/apis/credentials")
        print("  • 计费设置: https://console.cloud.google.com/billing")
        print("  • API配额: https://console.cloud.google.com/apis/quotas")
        
        print("\n" + "="*50)
    
    def run_full_check(self):
        """运行完整检查"""
        print("🔍 Google Maps API密钥状态检查工具")
        print("="*50)
        
        # 步骤1: 加载配置
        if not self.load_config():
            print("❌ 无法加载配置，检查终止")
            return False
        
        # 步骤2: 检查密钥格式
        self.check_api_key_format()
        
        # 步骤3: 测试API服务
        self.test_maps_javascript_api()
        self.test_3d_maps_api()
        
        # 步骤4: 检查配额
        self.check_quota_status()
        
        # 步骤5: 分析计费状态
        self.analyze_billing_status()
        
        # 步骤6: 生成建议
        self.generate_recommendations()
        
        # 步骤7: 保存报告
        self.save_report()
        
        # 步骤8: 显示摘要
        self.print_summary()
        
        return True

def main():
    """主函数"""
    checker = APIKeyChecker()
    
    try:
        success = checker.run_full_check()
        
        if success:
            print("\n✅ 诊断完成！")
            if checker.results["api_key_status"] == "healthy":
                print("🎉 您的API密钥状态良好！")
            else:
                print("⚠️ 发现问题，请查看上述建议进行修复。")
        else:
            print("\n❌ 诊断过程中出现错误，请检查配置文件。")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断了检查过程")
    except Exception as e:
        print(f"\n❌ 检查过程中发生意外错误: {str(e)}")

if __name__ == "__main__":
    main()