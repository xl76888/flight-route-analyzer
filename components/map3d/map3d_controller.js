/**
 * 3D地图控制器
 * 负责Google Maps 3D API的初始化、航线绘制和交互控制
 */

class Map3DController {
  constructor() {
    this.map = null;
    this.isInitialized = false;
    this.markers = new Map();
    this.polylines = new Map();
    this.routeData = [];
    this.config = {
      apiKey: 'AIzaSyBoAqo1lCI2FAQIY7A0jTlXI79mC2SO4Kw', // 实际的API密钥
      mapId: '45c4f1595b0cd27f9feda952', // 实际的地图ID
      defaultCenter: { lat: 39.9042, lng: 116.4074, altitude: 0 },
      defaultZoom: 5,
      defaultTilt: 45,
      defaultRange: 1000000
    };
    
    // 航线样式配置
    this.routeStyles = {
      domestic: {
        color: { r: 0, g: 128, b: 255, a: 0.8 }, // 蓝色
        width: 3,
        altitude: 8000
      },
      international: {
        color: { r: 255, g: 165, b: 0, a: 0.8 }, // 橙色
        width: 4,
        altitude: 10000
      },
      cargo: {
        color: { r: 34, g: 139, b: 34, a: 0.8 }, // 绿色
        width: 2,
        altitude: 6000
      },
      highFrequency: {
        color: { r: 255, g: 0, b: 0, a: 0.9 }, // 红色
        width: 5,
        altitude: 12000
      }
    };
    
    // 机场标记样式
    this.airportStyles = {
      major: {
        color: { r: 255, g: 0, b: 0, a: 1 },
        scale: 1.2
      },
      regional: {
        color: { r: 0, g: 0, b: 255, a: 1 },
        scale: 1.0
      },
      cargo: {
        color: { r: 0, g: 128, b: 0, a: 1 },
        scale: 0.8
      }
    };
  }
  
  /**
   * 初始化3D地图
   */
  async initialize() {
    try {
      console.log('开始初始化3D地图控制器...');
      
      // 加载Google Maps API
      await this.loadGoogleMapsAPI();
      
      // 获取地图容器
      const mapElement = document.getElementById('map3d');
      if (!mapElement) {
        throw new Error('找不到地图容器元素');
      }
      
      this.map = mapElement;
      
      // 设置地图事件监听
      this.setupEventListeners();
      
      // 设置初始视角
      this.setInitialView();
      
      this.isInitialized = true;
      console.log('3D地图控制器初始化完成');
      
      return true;
    } catch (error) {
      console.error('3D地图初始化失败:', error);
      throw error;
    }
  }
  
  /**
   * 加载Google Maps API
   */
  async loadGoogleMapsAPI() {
    return new Promise((resolve, reject) => {
      // 检查API是否已加载
      if (window.google && window.google.maps) {
        resolve();
        return;
      }
      
      // 动态加载API
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${this.config.apiKey}&libraries=maps3d&v=beta`;
      script.async = true;
      script.defer = true;
      
      script.onload = () => {
        console.log('Google Maps API加载完成');
        resolve();
      };
      
      script.onerror = () => {
        reject(new Error('Google Maps API加载失败'));
      };
      
      document.head.appendChild(script);
    });
  }
  
  /**
   * 设置事件监听器
   */
  setupEventListeners() {
    if (!this.map) return;
    
    // 地图加载完成事件
    this.map.addEventListener('gmp-load', () => {
      console.log('3D地图加载完成');
      this.onMapLoaded();
    });
    
    // 地图错误事件
    this.map.addEventListener('gmp-error', (event) => {
      console.error('3D地图错误:', event);
      this.onMapError(event);
    });
    
    // 相机变化事件
    this.map.addEventListener('gmp-camera-changed', (event) => {
      this.onCameraChanged(event);
    });
  }
  
  /**
   * 设置初始视角
   */
  setInitialView() {
    if (!this.map) return;
    
    this.map.center = this.config.defaultCenter;
    this.map.zoom = this.config.defaultZoom;
    this.map.tilt = this.config.defaultTilt;
    this.map.range = this.config.defaultRange;
  }
  
  /**
   * 地图加载完成回调
   */
  onMapLoaded() {
    // 通知外部地图已准备就绪
    this.dispatchEvent('map-ready', { loaded: true });
  }
  
  /**
   * 地图错误回调
   */
  onMapError(event) {
    this.dispatchEvent('map-error', { error: event });
  }
  
  /**
   * 相机变化回调
   */
  onCameraChanged(event) {
    // 可以在这里处理相机变化逻辑
  }
  
  /**
   * 加载航线数据
   */
  loadRoutes(routes) {
    if (!this.isInitialized || !routes) {
      console.warn('地图未初始化或数据无效');
      return;
    }
    
    console.log(`开始加载 ${routes.length} 条航线`);
    
    // 清除现有数据
    this.clearAll();
    
    // 保存数据
    this.routeData = routes;
    
    // 绘制航线和机场
    this.drawRoutes(routes);
    this.drawAirports(routes);
    
    // 调整视角以适应所有航线
    this.fitBounds();
    
    console.log('航线加载完成');
  }
  
  /**
   * 绘制航线
   */
  drawRoutes(routes) {
    if (!window.google || !window.google.maps) {
      console.error('Google Maps API未加载');
      return;
    }
    
    routes.forEach((route, index) => {
      if (!this.isValidRoute(route)) {
        console.warn('无效航线数据:', route);
        return;
      }
      
      try {
        const polyline = this.createRoutePolyline(route, index);
        if (polyline) {
          this.polylines.set(`route_${index}`, polyline);
          this.map.appendChild(polyline);
        }
      } catch (error) {
        console.error('绘制航线失败:', error, route);
      }
    });
  }
  
  /**
   * 创建航线多段线
   */
  createRoutePolyline(route, index) {
    if (!window.google.maps.maps3d) {
      console.error('3D Maps库未加载');
      return null;
    }
    
    // 创建3D多段线元素
    const polyline = new google.maps.maps3d.Polyline3DElement();
    
    // 设置坐标点
    const coordinates = [
      {
        lat: parseFloat(route.start_lat),
        lng: parseFloat(route.start_lng),
        altitude: this.getRouteAltitude(route)
      },
      {
        lat: parseFloat(route.end_lat),
        lng: parseFloat(route.end_lng),
        altitude: this.getRouteAltitude(route)
      }
    ];
    
    polyline.coordinates = coordinates;
    
    // 设置样式
    const style = this.getRouteStyle(route);
    polyline.strokeColor = this.colorToHex(style.color);
    polyline.strokeWidth = style.width;
    
    // 设置透明度
    polyline.strokeOpacity = style.color.a;
    
    // 添加标签信息
    polyline.title = `${route.start_airport || '未知'} → ${route.end_airport || '未知'}`;
    
    return polyline;
  }
  
  /**
   * 绘制机场标记
   */
  drawAirports(routes) {
    if (!window.google || !window.google.maps) {
      console.error('Google Maps API未加载');
      return;
    }
    
    // 收集所有唯一机场
    const airports = new Map();
    
    routes.forEach(route => {
      if (this.isValidRoute(route)) {
        // 起点机场
        if (route.start_airport && route.start_lat && route.start_lng) {
          const key = route.start_airport;
          if (!airports.has(key)) {
            airports.set(key, {
              code: route.start_airport,
              name: route.start_airport_name || route.start_airport,
              lat: parseFloat(route.start_lat),
              lng: parseFloat(route.start_lng),
              type: this.getAirportType(route.start_airport),
              routes: 0,
              isOrigin: true,
              isDestination: false,
              isTransit: false,
              routeList: []
            });
          }
          const airport = airports.get(key);
          airport.routes++;
          airport.isOrigin = true;
          airport.routeList.push(route);
        }
        
        // 终点机场
        if (route.end_airport && route.end_lat && route.end_lng) {
          const key = route.end_airport;
          if (!airports.has(key)) {
            airports.set(key, {
              code: route.end_airport,
              name: route.end_airport_name || route.end_airport,
              lat: parseFloat(route.end_lat),
              lng: parseFloat(route.end_lng),
              type: this.getAirportType(route.end_airport),
              routes: 0,
              isOrigin: false,
              isDestination: true,
              isTransit: false,
              routeList: []
            });
          }
          const airport = airports.get(key);
          airport.routes++;
          airport.isDestination = true;
          airport.routeList.push(route);
        }
      }
    });
    
    // 检查中转机场（既是起点又是终点）
    airports.forEach((airport, key) => {
      if (airport.isOrigin && airport.isDestination) {
        airport.isTransit = true;
      }
    });
    
    // 绘制机场标记
    airports.forEach((airport, code) => {
      try {
        const marker = this.createAirportMarker(airport);
        if (marker) {
          this.markers.set(code, marker);
          this.map.appendChild(marker);
        }
      } catch (error) {
        console.error('绘制机场标记失败:', error, airport);
      }
    });
  }
  
  /**
   * 创建机场标记
   */
  createAirportMarker(airport) {
    if (!window.google.maps.maps3d) {
      console.error('3D Maps库未加载');
      return null;
    }
    
    // 创建3D标记元素
    const marker = new google.maps.maps3d.Marker3DElement();
    
    // 设置位置
    marker.position = {
      lat: airport.lat,
      lng: airport.lng,
      altitude: 0
    };
    
    // 设置样式
    const style = this.getAirportStyle(airport);
    marker.style = {
      color: style.color,
      scale: style.scale
    };
    
    // 确定机场角色
    let roleText = '';
    if (airport.isTransit) {
      roleText = '中转';
    } else if (airport.isOrigin && airport.isDestination) {
      roleText = '双向';
    } else if (airport.isOrigin) {
      roleText = '始发';
    } else if (airport.isDestination) {
      roleText = '目的';
    }
    
    // 检查进出口信息
    const hasImport = airport.routeList && airport.routeList.some(r => r.direction === '进口');
    const hasExport = airport.routeList && airport.routeList.some(r => r.direction === '出口');
    if (hasImport && hasExport) {
      roleText = '进出口';
    } else if (hasImport) {
      roleText = '进口';
    } else if (hasExport) {
      roleText = '出口';
    }
    
    // 设置标签
    marker.label = `${airport.code} [${roleText}]`;
    marker.title = `${airport.name} (${airport.code})\n航线数: ${airport.routes}\n角色: ${roleText}`;}]}}}
    
    return marker;
  }
  
  /**
   * 验证航线数据有效性
   */
  isValidRoute(route) {
    return route &&
           route.start_lat && route.start_lng &&
           route.end_lat && route.end_lng &&
           !isNaN(parseFloat(route.start_lat)) &&
           !isNaN(parseFloat(route.start_lng)) &&
           !isNaN(parseFloat(route.end_lat)) &&
           !isNaN(parseFloat(route.end_lng));
  }
  
  /**
   * 获取航线样式
   */
  getRouteStyle(route) {
    // 根据航线类型和频率确定样式
    if (route.frequency && route.frequency >= 10) {
      return this.routeStyles.highFrequency;
    }
    
    if (route.route_type === 'international') {
      return this.routeStyles.international;
    }
    
    if (route.aircraft_type && route.aircraft_type.includes('货')) {
      return this.routeStyles.cargo;
    }
    
    return this.routeStyles.domestic;
  }
  
  /**
   * 获取航线飞行高度
   */
  getRouteAltitude(route) {
    const style = this.getRouteStyle(route);
    return style.altitude;
  }
  
  /**
   * 获取机场类型
   */
  getAirportType(airportCode) {
    // 简单的机场类型判断逻辑
    const majorAirports = ['PEK', 'PVG', 'CAN', 'CTU', 'KMG', 'XIY', 'WUH'];
    const cargoAirports = ['EHU', 'NKG', 'CGO'];
    
    if (majorAirports.includes(airportCode)) {
      return 'major';
    }
    
    if (cargoAirports.includes(airportCode)) {
      return 'cargo';
    }
    
    return 'regional';
  }
  
  /**
   * 获取机场样式
   */
  getAirportStyle(airport) {
    return this.airportStyles[airport.type] || this.airportStyles.regional;
  }
  
  /**
   * 颜色对象转换为十六进制字符串
   */
  colorToHex(color) {
    const r = Math.round(color.r).toString(16).padStart(2, '0');
    const g = Math.round(color.g).toString(16).padStart(2, '0');
    const b = Math.round(color.b).toString(16).padStart(2, '0');
    return `#${r}${g}${b}`;
  }
  
  /**
   * 清除所有地图元素
   */
  clearAll() {
    // 清除航线
    this.polylines.forEach(polyline => {
      if (polyline.remove) {
        polyline.remove();
      }
    });
    this.polylines.clear();
    
    // 清除标记
    this.markers.forEach(marker => {
      if (marker.remove) {
        marker.remove();
      }
    });
    this.markers.clear();
  }
  
  /**
   * 调整视角以适应所有航线
   */
  fitBounds() {
    if (!this.routeData || this.routeData.length === 0) {
      return;
    }
    
    // 计算边界
    const bounds = this.calculateBounds(this.routeData);
    if (!bounds) return;
    
    // 计算中心点
    const center = {
      lat: (bounds.north + bounds.south) / 2,
      lng: (bounds.east + bounds.west) / 2,
      altitude: 0
    };
    
    // 计算合适的观察距离
    const range = this.calculateOptimalRange(bounds);
    
    // 飞行到新视角
    this.flyTo({
      center: center,
      heading: 0,
      tilt: 45,
      range: range
    });
  }
  
  /**
   * 计算数据边界
   */
  calculateBounds(routes) {
    if (!routes || routes.length === 0) return null;
    
    let north = -90, south = 90, east = -180, west = 180;
    
    routes.forEach(route => {
      if (this.isValidRoute(route)) {
        const startLat = parseFloat(route.start_lat);
        const startLng = parseFloat(route.start_lng);
        const endLat = parseFloat(route.end_lat);
        const endLng = parseFloat(route.end_lng);
        
        north = Math.max(north, startLat, endLat);
        south = Math.min(south, startLat, endLat);
        east = Math.max(east, startLng, endLng);
        west = Math.min(west, startLng, endLng);
      }
    });
    
    return { north, south, east, west };
  }
  
  /**
   * 计算最佳观察距离
   */
  calculateOptimalRange(bounds) {
    const latDiff = bounds.north - bounds.south;
    const lngDiff = bounds.east - bounds.west;
    const maxDiff = Math.max(latDiff, lngDiff);
    
    // 转换为米并添加缓冲区
    return Math.max(maxDiff * 111000 * 2.5, 100000);
  }
  
  /**
   * 飞行到指定视角
   */
  flyTo(camera, duration = 2000) {
    if (!this.map || !this.isInitialized) return;
    
    this.map.flyCameraTo({
      endCamera: camera,
      durationMillis: duration
    });
  }
  
  /**
   * 重置视角
   */
  resetView() {
    this.flyTo({
      center: this.config.defaultCenter,
      heading: 0,
      tilt: this.config.defaultTilt,
      range: this.config.defaultRange
    });
  }
  
  /**
   * 分发自定义事件
   */
  dispatchEvent(type, data) {
    const event = new CustomEvent(type, { detail: data });
    window.dispatchEvent(event);
    
    // 同时通过postMessage通知父页面
    if (window.parent) {
      window.parent.postMessage({
        type: `map3d-${type}`,
        data: data
      }, '*');
    }
  }
  
  /**
   * 获取当前统计信息
   */
  getStats() {
    const airports = new Set();
    this.routeData.forEach(route => {
      if (route.start_airport) airports.add(route.start_airport);
      if (route.end_airport) airports.add(route.end_airport);
    });
    
    return {
      routeCount: this.routeData.length,
      airportCount: airports.size,
      markerCount: this.markers.size,
      polylineCount: this.polylines.size
    };
  }
}

// 导出控制器类
window.Map3DController = Map3DController;