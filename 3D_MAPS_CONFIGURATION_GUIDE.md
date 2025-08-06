# 3D Maps API 配置完整指南

## 📋 概述

本指南详细说明了如何正确配置Google Maps 3D API，解决3D地图加载问题。

## ✅ 已完成的配置更新

### 1. 代码配置更新

根据Google官方文档要求，已更新所有`gmp-map-3d`元素：

**更新前：**
```html
<gmp-map-3d id="map3d" 
            center="39.9042,116.4074" 
            zoom="5" 
            map-id="45c4f1595b0cd27f9feda952">
</gmp-map-3d>
```

**更新后：**
```html
<gmp-map-3d id="map3d" 
            center="39.9042,116.4074" 
            zoom="5" 
            map-id="45c4f1595b0cd27f9feda952"
            mode="HYBRID">
</gmp-map-3d>
```

**已更新的文件：**
- `components/map3d/map3d_component.html`
- `fix_3d_map_cdn.py`
- `map3d_integration.py`
- `test_3d_map_simple.html`
- `debug_3d_map.html`

### 2. 浏览器优化

**Edge浏览器flags已启用：**
- ✅ GPU rasterization: Enabled
- ✅ Override software rendering list: 已启用
- ✅ Experimental Web Platform features: 已启用

### 3. 测试工具

**已创建的测试页面：**
- `webgl_test.html` - WebGL支持测试
- `test_3d_map_updated.html` - 更新后的3D地图测试
- `debug_3d_map.html` - 调试工具（已更新）

## 🔧 Google Cloud Console 配置要求

### 必须启用的API

1. **Maps JavaScript API**
   - 在Google Cloud Console中搜索"Maps JavaScript API"
   - 点击"启用"

2. **Maps 3D API (Beta)**
   - 搜索"Maps 3D API"或"Photorealistic 3D Maps"
   - 确保启用Beta版本

3. **可选API**
   - Geocoding API
   - Places API

### API密钥配置

1. **创建API密钥**
   ```
   Google Cloud Console → API和服务 → 凭据 → 创建凭据 → API密钥
   ```

2. **设置API密钥限制**
   - 应用程序限制：HTTP referrers
   - 添加网站限制：`localhost:*`、`127.0.0.1:*`
   - API限制：选择需要的API

3. **API密钥权限**
   ```
   ✓ Maps JavaScript API
   ✓ Maps 3D API
   ✓ Geocoding API (可选)
   ```

### 计费设置

1. **启用计费账户**
   - Google Cloud Console → 结算
   - 关联有效的付款方式

2. **设置配额和预算**
   - 设置每日使用限制
   - 配置预算提醒

## 🔍 故障排查步骤

### 1. 检查WebGL支持

**打开WebGL测试页面：**
```
file:///D:/flight_tool/webgl_test.html
```

**预期结果：**
- ✅ WebGL 1.0 支持
- ✅ WebGL 2.0 支持（推荐）
- ✅ 硬件加速已启用

### 2. 测试3D地图配置

**打开更新后的测试页面：**
```
file:///D:/flight_tool/test_3d_map_updated.html
```

**检查项目：**
- API加载状态
- 3D地图元素配置
- 控制台错误信息

### 3. 验证API配置

**运行验证脚本：**
```bash
python scripts/verify_3d_api_config.py
```

### 4. 检查网络连接

**常见网络问题：**
- 防火墙阻止Google Maps API
- 代理服务器配置
- DNS解析问题

**测试方法：**
```bash
# 测试API连接
curl -I "https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY"
```

## 🚨 常见错误及解决方案

### 错误1：3D地图加载超时

**原因：**
- 缺少`mode`属性
- WebGL不支持
- API权限不足

**解决方案：**
1. 确认已添加`mode="HYBRID"`
2. 检查WebGL支持
3. 验证API密钥权限

### 错误2：API连接失败

**原因：**
- 网络连接问题
- API密钥无效
- 计费账户未启用

**解决方案：**
1. 检查网络连接
2. 验证API密钥
3. 确认计费状态

### 错误3：地图显示为灰色

**原因：**
- 地图ID无效
- API权限不足
- 地区不支持3D Maps

**解决方案：**
1. 验证地图ID
2. 检查API权限
3. 尝试其他地区坐标

## 📊 配置验证清单

### Google Cloud Console
- [ ] Maps JavaScript API已启用
- [ ] Maps 3D API (Beta)已启用
- [ ] API密钥已创建
- [ ] API密钥权限正确
- [ ] 计费账户已启用
- [ ] 地图ID已配置

### 代码配置
- [ ] 所有`gmp-map-3d`元素包含`mode`属性
- [ ] API密钥正确配置
- [ ] 地图ID正确配置
- [ ] 脚本加载顺序正确

### 浏览器设置
- [ ] WebGL支持已启用
- [ ] 硬件加速已启用
- [ ] Edge flags已优化
- [ ] 控制台无错误信息

## 🔗 有用的链接

- [Google Maps Platform 3D Maps文档](https://developers.google.com/maps/documentation/javascript/3d-maps)
- [Google Cloud Console](https://console.cloud.google.com/)
- [WebGL支持检测](https://get.webgl.org/)
- [Google Maps Platform API Checker](https://chrome.google.com/webstore/detail/google-maps-platform-api/mlikepnkghhlnkgeejmlkfeheihlehne)

## 📞 支持

如果问题仍然存在，请：

1. 检查浏览器控制台的详细错误信息
2. 验证Google Cloud Console中的所有设置
3. 确认网络连接和防火墙设置
4. 联系Google Maps Platform支持

---

**最后更新：** 2024年1月
**版本：** 1.0
**状态：** 配置已完成，等待测试验证