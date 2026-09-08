/**
 * ahaos-perf.js — 博客轻量性能增强
 *
 * 在 DOMContentLoaded 后为未声明加载策略的 <img> 统一启用原生懒加载：
 *   - 已带 loading 属性的图片保持不变；
 *   - fetchpriority="high" 的首屏关键图被排除，不做降级；
 *   - 前 2 张图片（头像 / logo / 首屏首图）豁免，避免首屏延迟；
 *   - 其余图片统一设置 loading="lazy" + decoding="async"。
 *
 * 无任何第三方依赖，IIFE 包裹，DOM API 降级安全。
 */
(function () {
  'use strict';

  /* 首屏豁免数量：头像 / logo 等关键首图不懒加载 */
  var ABOVE_THE_FOLD_EXEMPT = 2;

  function enhanceImages() {
    var images = document.querySelectorAll('img');
    var processed = 0;

    for (var i = 0; i < images.length; i += 1) {
      var img = images[i];

      // 已有明确加载策略的图片不干预
      if (img.hasAttribute('loading')) {
        continue;
      }

      // 高优先级关键图排除，避免被降级为懒加载
      var fetchPriority = (img.getAttribute('fetchpriority') || '').toLowerCase();
      if (fetchPriority === 'high') {
        continue;
      }

      // 前两张（头像/logo/首图）豁免
      if (processed < ABOVE_THE_FOLD_EXEMPT) {
        processed += 1;
        continue;
      }

      try {
        img.setAttribute('loading', 'lazy');
        img.setAttribute('decoding', 'async');
      } catch (err) {
        /* 忽略个别异常图片节点，保证整体脚本健壮 */
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceImages);
  } else {
    enhanceImages();
  }
})();
