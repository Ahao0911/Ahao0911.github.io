/**
 * 王韵豪个人主页 · main.js
 * 功能：移动端汉堡菜单、锚点平滑滚动、滚动时导航高亮、元素淡入动画。
 * 无任何外部依赖，纯原生 JavaScript。
 */
(function () {
  'use strict';

  var navbar = document.getElementById('navbar');
  var navToggle = document.getElementById('navToggle');
  var navMenu = document.getElementById('navMenu');
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.nav-link'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('main section[id]'));
  var revealEls = Array.prototype.slice.call(document.querySelectorAll('.reveal'));

  /* ---------- 1. 移动端汉堡菜单 ---------- */
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function () {
      var isOpen = navMenu.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      navToggle.setAttribute('aria-label', isOpen ? '关闭导航菜单' : '打开导航菜单');
    });

    // 点击任一导航链接后自动收起菜单
    navMenu.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        navMenu.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });

    // 点击页面其他区域时收起菜单
    document.addEventListener('click', function (e) {
      if (navMenu.classList.contains('open') && !navMenu.contains(e.target) && !navToggle.contains(e.target)) {
        navMenu.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });

    // 按 Esc 收起菜单
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navMenu.classList.contains('open')) {
        navMenu.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ---------- 2. 平滑滚动（原生 fallback） ---------- */
  function smoothScrollTo(targetId) {
    var target = document.getElementById(targetId);
    if (!target) {
      return;
    }
    var headerOffset = (navbar ? navbar.offsetHeight : 60) + 12;
    var targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerOffset;
    window.scrollTo({
      top: Math.max(targetPosition, 0),
      behavior: 'smooth'
    });
  }

  navLinks.forEach(function (link) {
    var href = link.getAttribute('href') || '';
    // 仅处理站内锚点链接 #xxx
    if (href.indexOf('#') === 0 && href.length > 1) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        smoothScrollTo(href.slice(1));
      });
    }
  });

  /* ---------- 3. 滚动时高亮当前 section 对应导航项 ---------- */
  function setActiveLink(id) {
    navLinks.forEach(function (link) {
      var href = link.getAttribute('href') || '';
      if (href === '#' + id) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  var scrollTicking = false;
  function onScroll() {
    if (scrollTicking) {
      return;
    }
    scrollTicking = true;
    window.requestAnimationFrame(function () {
      var scrollPos = window.pageYOffset;
      var headerOffset = (navbar ? navbar.offsetHeight : 60) + 40;
      var currentId = 'home';

      sections.forEach(function (section) {
        if (section.offsetTop - headerOffset <= scrollPos) {
          currentId = section.getAttribute('id');
        }
      });

      // 页面滚到底部时，高亮最后一个 section
      if (window.innerHeight + scrollPos >= document.documentElement.scrollHeight - 4) {
        currentId = sections.length > 0 ? sections[sections.length - 1].getAttribute('id') : currentId;
      }

      setActiveLink(currentId);
      scrollTicking = false;
    });
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });

  /* ---------- 4. 元素进入视口淡入 ---------- */
  if ('IntersectionObserver' in window) {
    var revealObserver = new IntersectionObserver(
      function (entries, observer) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('in-view');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
    );

    revealEls.forEach(function (el) {
      revealObserver.observe(el);
    });
  } else {
    // 旧浏览器直接全部显示
    revealEls.forEach(function (el) {
      el.classList.add('in-view');
    });
  }

  /* ---------- 初始化 ---------- */
  function init() {
    onScroll();
    // 保证首屏内容可见
    revealEls.forEach(function (el) {
      var rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight) {
        el.classList.add('in-view');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

/* QQ 一键复制 */
(function () {
  var card = document.getElementById('qq-card');
  if (!card) { return; }
  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
  }
  function doCopy() {
    var valEl = card.querySelector('.contact-value');
    var labelEl = card.querySelector('.contact-label');
    var text = valEl ? valEl.textContent.trim() : '';
    var done = function () {
      var old = labelEl.textContent;
      labelEl.textContent = '已复制';
      setTimeout(function () { labelEl.textContent = old; }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(function () { fallbackCopy(text); done(); });
    } else {
      fallbackCopy(text);
      done();
    }
  }
  card.addEventListener('click', doCopy);
  card.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); doCopy(); }
  });
})();
