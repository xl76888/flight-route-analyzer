# 双向航线检测分析报告

## 问题概述

在航线可视化工具中，用户发现双向航线检测功能似乎没有正常工作，地图上没有显示双向航线的特殊标识。

## 问题分析过程

### 1. 数据结构分析

通过分析 `data/大陆航司全货机航线.xlsx` 文件，发现：
- 原始数据包含 "出口航线" 和 "进口航线" 两列
- 数据通过 `fix_parser.py` 解析为标准格式
- 每条记录都有明确的 `direction` 字段（'出口' 或 '进口'）

### 2. 双向航线统计

**实际数据统计结果：**
- 总航线记录数：1,085 条
- 唯一航线数：402 条
- **双向航线对数：175 对**
- 出口航线：542 条
- 进口航线：543 条

### 3. 检测逻辑验证

通过创建 `fix_bidirectional_detection.py` 脚本验证发现：
- `web_app.py` 中的双向航线检测逻辑是**正确的**
- 检测到 1,013 条双向航线记录（包括正向和反向）
- 实际双向航线对数为 175 对

### 4. 双向航线示例

部分双向航线对包括：
- 成都双流 ↔ 阿勒马克图姆
- 成都双流 ↔ 法兰克福
- 浦东 ↔ 芝加哥
- 深圳 ↔ 安克雷奇
- 杭州 ↔ 列日
- 等等...

## 检测逻辑说明

### route_stats 构建

```python
route_stats = {}
for idx, row in filtered.iterrows():
    route_key = f"{row['origin']}-{row['destination']}"
    if route_key not in route_stats:
        route_stats[route_key] = {'count': 0, 'airlines': set(), 'directions': set()}
    route_stats[route_key]['count'] += 1
    route_stats[route_key]['airlines'].add(row['airline'])
    route_stats[route_key]['directions'].add(row.get('direction', '出口'))
```

### 双向航线检测

```python
route_key = f"{route.get('origin', '')}-{route.get('destination', '')}"
reverse_route_key = f"{route.get('destination', '')}-{route.get('origin', '')}"
is_bidirectional = reverse_route_key in route_stats
```

## 结论

1. **双向航线检测功能正常工作**
2. 数据中确实存在 **175 对双向航线**
3. 检测逻辑能够正确识别双向航线
4. 在 3D 地图和 2D 地图中都会标记 `is_bidirectional` 字段

## 用户界面显示

双向航线在地图上的显示特征：
- 在航线数据中包含 `is_bidirectional: true` 字段
- 在 "往返航线视图" 中可以查看详细的双向航线配对信息
- 统计面板会显示双向航线对的数量

## 建议

1. 在地图图例中添加双向航线的说明
2. 考虑为双向航线使用不同的颜色或线型
3. 在航线详情弹窗中显示是否为双向航线

---

**报告生成时间：** 2024年
**分析工具：** fix_bidirectional_detection.py
**数据源：** data/大陆航司全货机航线.xlsx