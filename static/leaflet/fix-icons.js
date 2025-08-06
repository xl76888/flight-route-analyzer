
// Leaflet 图标路径修复脚本
(function() {
    // 等待 Leaflet 加载完成
    function fixLeafletIcons() {
        if (typeof L !== 'undefined' && L.Icon && L.Icon.Default) {
            // 设置图标基础路径
            L.Icon.Default.imagePath = './static/leaflet/images/';
            
            // 明确设置每个图标的 URL
            L.Icon.Default.prototype.options.iconUrl = './static/leaflet/images/marker-icon.png';
            L.Icon.Default.prototype.options.iconRetinaUrl = './static/leaflet/images/marker-icon-2x.png';
            L.Icon.Default.prototype.options.shadowUrl = './static/leaflet/images/marker-shadow.png';
            
            console.log('✅ Leaflet 图标路径已修复');
            return true;
        }
        return false;
    }
    
    // 立即尝试修复
    if (!fixLeafletIcons()) {
        // 如果 Leaflet 还未加载，等待 DOM 加载完成后再试
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fixLeafletIcons);
        } else {
            // 延迟执行
            setTimeout(fixLeafletIcons, 100);
        }
    }
})();
