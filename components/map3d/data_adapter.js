/**
 * 数据适配器
 * 负责将Streamlit应用的航线数据转换为3D地图可用的格式
 */

class DataAdapter {
  constructor() {
    this.cache = new Map();
    this.airportCache = new Map();
    
    // 数据字段映射配置
    this.fieldMapping = {
      // 航线字段映射
      route: {
        startAirport: ['start_airport', 'origin_airport', 'departure_airport'],
        endAirport: ['end_airport', 'dest_airport', 'arrival_airport'],
        startLat: ['start_lat', 'origin_lat', 'departure_lat'],
        startLng: ['start_lng', 'origin_lng', 'departure_lng'],
        endLat: ['end_lat', 'dest_lat', 'arrival_lat'],
        endLng: ['end_lng', 'dest_lng', 'arrival_lng'],
        frequency: ['frequency', 'flight_count', 'count'],
        airline: ['airline', 'carrier', 'airline_code'],
        aircraftType: ['aircraft_type', 'plane_type', 'aircraft'],
        routeType: ['route_type', 'type', 'category']
      },
      
      // 机场字段映射
      airport: {
        code: ['airport_code', 'code', 'iata', 'icao'],
        name: ['airport_name', 'name', 'full_name'],
        city: ['city', 'city_name', 'location'],
        country: ['country', 'country_name', 'nation'],
        lat: ['lat', 'latitude', 'coord_lat'],
        lng: ['lng', 'longitude', 'coord_lng']
      }
    };
    
    // 航线类型识别规则
    this.routeTypeRules = {
      international: {
        keywords: ['国际', 'international', 'intl'],
        countryDiff: true // 起终点国家不同
      },
      domestic: {
        keywords: ['国内', 'domestic', 'dom'],
        countryDiff: false // 起终点国家相同
      },
      cargo: {
        keywords: ['货运', 'cargo', 'freight', '货机'],
        aircraftTypes: ['B747F', 'B777F', 'A330F', 'MD11F']
      },
      passenger: {
        keywords: ['客运', 'passenger', 'pax'],
        aircraftTypes: ['B737', 'B777', 'B787', 'A320', 'A330', 'A350']
      }
    };
    
    // 中国主要机场列表
    this.majorChineseAirports = [
      'PEK', 'PVG', 'CAN', 'CTU', 'KMG', 'XIY', 'WUH', 'CSX', 'SZX',
      'NKG', 'HGH', 'TSN', 'DLC', 'SHE', 'HAK', 'URC', 'LHW', 'CGO'
    ];
    
    // 货运枢纽机场
    this.cargoHubAirports = ['EHU', 'NKG', 'CGO', 'PVG', 'PEK', 'CAN'];
  }
  
  /**
   * 转换航线数据为3D地图格式
   * @param {Array} rawData - 原始航线数据
   * @param {Object} options - 转换选项
   * @returns {Array} 转换后的数据
   */
  convertRouteData(rawData, options = {}) {
    if (!Array.isArray(rawData)) {
      console.warn('输入数据不是数组格式');
      return [];
    }
    
    console.log(`开始转换 ${rawData.length} 条航线数据`);
    
    const converted = [];
    const errors = [];
    
    rawData.forEach((item, index) => {
      try {
        const route = this.convertSingleRoute(item, index);
        if (route) {
          converted.push(route);
        }
      } catch (error) {
        errors.push({ index, error: error.message, data: item });
      }
    });
    
    if (errors.length > 0) {
      console.warn(`转换过程中发现 ${errors.length} 个错误:`, errors);
    }
    
    console.log(`成功转换 ${converted.length} 条航线数据`);
    return converted;
  }
  
  /**
   * 转换单条航线数据
   * @param {Object} item - 单条原始数据
   * @param {number} index - 数据索引
   * @returns {Object|null} 转换后的航线对象
   */
  convertSingleRoute(item, index) {
    if (!item || typeof item !== 'object') {
      return null;
    }
    
    // 提取基础字段
    const route = {
      id: `route_${index}`,
      start_airport: this.extractField(item, this.fieldMapping.route.startAirport),
      end_airport: this.extractField(item, this.fieldMapping.route.endAirport),
      start_lat: this.extractNumericField(item, this.fieldMapping.route.startLat),
      start_lng: this.extractNumericField(item, this.fieldMapping.route.startLng),
      end_lat: this.extractNumericField(item, this.fieldMapping.route.endLat),
      end_lng: this.extractNumericField(item, this.fieldMapping.route.endLng),
      frequency: this.extractNumericField(item, this.fieldMapping.route.frequency, 1),
      airline: this.extractField(item, this.fieldMapping.route.airline),
      aircraft_type: this.extractField(item, this.fieldMapping.route.aircraftType),
      route_type: this.extractField(item, this.fieldMapping.route.routeType)
    };
    
    // 验证必需字段
    if (!this.isValidCoordinates(route.start_lat, route.start_lng) ||
        !this.isValidCoordinates(route.end_lat, route.end_lng)) {
      return null;
    }
    
    // 增强数据
    this.enhanceRouteData(route, item);
    
    return route;
  }
  
  /**
   * 提取字段值
   * @param {Object} item - 数据对象
   * @param {Array} fieldNames - 可能的字段名列表
   * @param {*} defaultValue - 默认值
   * @returns {*} 字段值
   */
  extractField(item, fieldNames, defaultValue = null) {
    for (const fieldName of fieldNames) {
      if (item.hasOwnProperty(fieldName) && item[fieldName] != null) {
        return item[fieldName];
      }
    }
    return defaultValue;
  }
  
  /**
   * 提取数值字段
   * @param {Object} item - 数据对象
   * @param {Array} fieldNames - 可能的字段名列表
   * @param {number} defaultValue - 默认值
   * @returns {number} 数值
   */
  extractNumericField(item, fieldNames, defaultValue = 0) {
    const value = this.extractField(item, fieldNames, defaultValue);
    const numValue = parseFloat(value);
    return isNaN(numValue) ? defaultValue : numValue;
  }
  
  /**
   * 验证坐标有效性
   * @param {number} lat - 纬度
   * @param {number} lng - 经度
   * @returns {boolean} 是否有效
   */
  isValidCoordinates(lat, lng) {
    return !isNaN(lat) && !isNaN(lng) &&
           lat >= -90 && lat <= 90 &&
           lng >= -180 && lng <= 180;
  }
  
  /**
   * 增强航线数据
   * @param {Object} route - 航线对象
   * @param {Object} originalItem - 原始数据
   */
  enhanceRouteData(route, originalItem) {
    // 确定航线类型
    route.route_type = this.determineRouteType(route, originalItem);
    
    // 计算距离
    route.distance = this.calculateDistance(
      route.start_lat, route.start_lng,
      route.end_lat, route.end_lng
    );
    
    // 确定航线等级
    route.level = this.determineRouteLevel(route);
    
    // 添加机场信息
    route.start_airport_info = this.getAirportInfo(route.start_airport);
    route.end_airport_info = this.getAirportInfo(route.end_airport);
    
    // 计算飞行高度（用于3D显示）
    route.flight_altitude = this.calculateFlightAltitude(route);
    
    // 确定显示样式
    route.display_style = this.determineDisplayStyle(route);
  }
  
  /**
   * 确定航线类型
   * @param {Object} route - 航线对象
   * @param {Object} originalItem - 原始数据
   * @returns {string} 航线类型
   */
  determineRouteType(route, originalItem) {
    // 如果已有类型，先检查
    if (route.route_type) {
      const type = route.route_type.toLowerCase();
      if (type.includes('国际') || type.includes('international')) {
        return 'international';
      }
      if (type.includes('国内') || type.includes('domestic')) {
        return 'domestic';
      }
    }
    
    // 根据机场代码判断
    const startIsChinese = this.isChineseAirport(route.start_airport);
    const endIsChinese = this.isChineseAirport(route.end_airport);
    
    if (startIsChinese && endIsChinese) {
      return 'domestic';
    } else if (startIsChinese || endIsChinese) {
      return 'international';
    }
    
    // 根据距离判断（超过3000公里可能是国际航线）
    if (route.distance > 3000) {
      return 'international';
    }
    
    return 'domestic';
  }
  
  /**
   * 判断是否为中国机场
   * @param {string} airportCode - 机场代码
   * @returns {boolean} 是否为中国机场
   */
  isChineseAirport(airportCode) {
    if (!airportCode) return false;
    
    // 中国机场代码通常以特定字母开头或在已知列表中
    const code = airportCode.toUpperCase();
    
    // 检查是否在主要机场列表中
    if (this.majorChineseAirports.includes(code)) {
      return true;
    }
    
    // 简单的启发式规则（可以根据实际情况完善）
    const chinesePatterns = [
      /^Z[A-Z]{2}$/, // 中国民航局分配的代码模式
      /^[A-Z]{3}$/ // 三字母代码，需要进一步验证
    ];
    
    return chinesePatterns.some(pattern => pattern.test(code));
  }
  
  /**
   * 计算两点间距离（公里）
   * @param {number} lat1 - 起点纬度
   * @param {number} lng1 - 起点经度
   * @param {number} lat2 - 终点纬度
   * @param {number} lng2 - 终点经度
   * @returns {number} 距离（公里）
   */
  calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // 地球半径（公里）
    const dLat = this.toRadians(lat2 - lat1);
    const dLng = this.toRadians(lng2 - lng1);
    
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
              Math.sin(dLng / 2) * Math.sin(dLng / 2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }
  
  /**
   * 角度转弧度
   * @param {number} degrees - 角度
   * @returns {number} 弧度
   */
  toRadians(degrees) {
    return degrees * (Math.PI / 180);
  }
  
  /**
   * 确定航线等级
   * @param {Object} route - 航线对象
   * @returns {string} 航线等级
   */
  determineRouteLevel(route) {
    if (route.frequency >= 20) {
      return 'high';
    } else if (route.frequency >= 10) {
      return 'medium';
    } else if (route.frequency >= 5) {
      return 'normal';
    } else {
      return 'low';
    }
  }
  
  /**
   * 获取机场信息
   * @param {string} airportCode - 机场代码
   * @returns {Object} 机场信息
   */
  getAirportInfo(airportCode) {
    if (!airportCode) return null;
    
    // 检查缓存
    if (this.airportCache.has(airportCode)) {
      return this.airportCache.get(airportCode);
    }
    
    // 基础信息
    const info = {
      code: airportCode,
      type: this.determineAirportType(airportCode),
      isChinese: this.isChineseAirport(airportCode),
      isCargoHub: this.cargoHubAirports.includes(airportCode.toUpperCase())
    };
    
    // 缓存结果
    this.airportCache.set(airportCode, info);
    
    return info;
  }
  
  /**
   * 确定机场类型
   * @param {string} airportCode - 机场代码
   * @returns {string} 机场类型
   */
  determineAirportType(airportCode) {
    if (!airportCode) return 'unknown';
    
    const code = airportCode.toUpperCase();
    
    if (this.majorChineseAirports.includes(code)) {
      return 'major';
    }
    
    if (this.cargoHubAirports.includes(code)) {
      return 'cargo';
    }
    
    return 'regional';
  }
  
  /**
   * 计算飞行高度（用于3D显示）
   * @param {Object} route - 航线对象
   * @returns {number} 飞行高度（米）
   */
  calculateFlightAltitude(route) {
    // 基础高度
    let altitude = 8000;
    
    // 根据距离调整
    if (route.distance > 5000) {
      altitude = 12000; // 长途航线
    } else if (route.distance > 2000) {
      altitude = 10000; // 中程航线
    } else if (route.distance < 500) {
      altitude = 6000;  // 短途航线
    }
    
    // 根据类型调整
    if (route.route_type === 'international') {
      altitude += 2000;
    }
    
    // 根据频率调整（高频航线飞得更高以便区分）
    if (route.frequency >= 20) {
      altitude += 3000;
    } else if (route.frequency >= 10) {
      altitude += 1500;
    }
    
    return altitude;
  }
  
  /**
   * 确定显示样式
   * @param {Object} route - 航线对象
   * @returns {Object} 显示样式
   */
  determineDisplayStyle(route) {
    const style = {
      color: this.getRouteColor(route),
      width: this.getRouteWidth(route),
      opacity: this.getRouteOpacity(route),
      animation: this.shouldAnimate(route)
    };
    
    return style;
  }
  
  /**
   * 获取航线颜色
   * @param {Object} route - 航线对象
   * @returns {Object} 颜色对象
   */
  getRouteColor(route) {
    // 根据类型确定基础颜色
    switch (route.route_type) {
      case 'international':
        return { r: 255, g: 165, b: 0, a: 0.8 }; // 橙色
      case 'domestic':
        return { r: 0, g: 128, b: 255, a: 0.8 }; // 蓝色
      default:
        return { r: 128, g: 128, b: 128, a: 0.8 }; // 灰色
    }
  }
  
  /**
   * 获取航线宽度
   * @param {Object} route - 航线对象
   * @returns {number} 线条宽度
   */
  getRouteWidth(route) {
    // 根据频率确定宽度
    if (route.frequency >= 20) {
      return 6;
    } else if (route.frequency >= 10) {
      return 4;
    } else if (route.frequency >= 5) {
      return 3;
    } else {
      return 2;
    }
  }
  
  /**
   * 获取航线透明度
   * @param {Object} route - 航线对象
   * @returns {number} 透明度
   */
  getRouteOpacity(route) {
    // 根据频率确定透明度
    const baseOpacity = 0.6;
    const frequencyBonus = Math.min(route.frequency * 0.02, 0.3);
    return Math.min(baseOpacity + frequencyBonus, 1.0);
  }
  
  /**
   * 判断是否需要动画
   * @param {Object} route - 航线对象
   * @returns {boolean} 是否需要动画
   */
  shouldAnimate(route) {
    // 高频航线使用动画
    return route.frequency >= 10;
  }
  
  /**
   * 过滤和排序数据
   * @param {Array} routes - 航线数据
   * @param {Object} filters - 过滤条件
   * @returns {Array} 过滤后的数据
   */
  filterAndSort(routes, filters = {}) {
    let filtered = [...routes];
    
    // 应用过滤器
    if (filters.routeType) {
      filtered = filtered.filter(route => route.route_type === filters.routeType);
    }
    
    if (filters.minFrequency) {
      filtered = filtered.filter(route => route.frequency >= filters.minFrequency);
    }
    
    if (filters.airline) {
      filtered = filtered.filter(route => 
        route.airline && route.airline.includes(filters.airline)
      );
    }
    
    if (filters.airport) {
      filtered = filtered.filter(route => 
        route.start_airport === filters.airport || 
        route.end_airport === filters.airport
      );
    }
    
    // 排序
    if (filters.sortBy) {
      filtered.sort((a, b) => {
        switch (filters.sortBy) {
          case 'frequency':
            return b.frequency - a.frequency;
          case 'distance':
            return b.distance - a.distance;
          case 'airline':
            return (a.airline || '').localeCompare(b.airline || '');
          default:
            return 0;
        }
      });
    }
    
    return filtered;
  }
  
  /**
   * 获取数据统计信息
   * @param {Array} routes - 航线数据
   * @returns {Object} 统计信息
   */
  getStatistics(routes) {
    if (!routes || routes.length === 0) {
      return {
        totalRoutes: 0,
        uniqueAirports: 0,
        totalFrequency: 0,
        averageDistance: 0,
        routeTypes: {},
        airlineCount: 0
      };
    }
    
    const airports = new Set();
    const airlines = new Set();
    const routeTypes = {};
    let totalFrequency = 0;
    let totalDistance = 0;
    
    routes.forEach(route => {
      // 统计机场
      if (route.start_airport) airports.add(route.start_airport);
      if (route.end_airport) airports.add(route.end_airport);
      
      // 统计航空公司
      if (route.airline) airlines.add(route.airline);
      
      // 统计航线类型
      const type = route.route_type || 'unknown';
      routeTypes[type] = (routeTypes[type] || 0) + 1;
      
      // 累计频率和距离
      totalFrequency += route.frequency || 0;
      totalDistance += route.distance || 0;
    });
    
    return {
      totalRoutes: routes.length,
      uniqueAirports: airports.size,
      totalFrequency: totalFrequency,
      averageDistance: routes.length > 0 ? totalDistance / routes.length : 0,
      routeTypes: routeTypes,
      airlineCount: airlines.size,
      averageFrequency: routes.length > 0 ? totalFrequency / routes.length : 0
    };
  }
  
  /**
   * 清除缓存
   */
  clearCache() {
    this.cache.clear();
    this.airportCache.clear();
  }
}

// 导出适配器类
window.DataAdapter = DataAdapter;