(function () {
  const composition = document.getElementById('landing-composition');
  if (!composition) return;

  const items = composition.querySelectorAll('.landing-card, .floating-bubble');
  if (!items.length) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion) return;

  const strengths = Array.from(items).map(function (_, i) {
    return 6 + (i % 3) * 4;
  });

  let rafId = null;
  let targetX = 0;
  let targetY = 0;

  function handleMouseMove(e) {
    const rect = composition.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;

    targetX = (e.clientX - cx) / (rect.width / 2);
    targetY = (e.clientY - cy) / (rect.height / 2);

    if (!rafId) {
      rafId = requestAnimationFrame(applyParallax);
    }
  }

  function applyParallax() {
    items.forEach(function (el, i) {
      const strength = strengths[i];
      const x = (targetX * strength).toFixed(1);
      const y = (targetY * strength).toFixed(1);

      el.style.setProperty('--parallax-x', x + 'px');
      el.style.setProperty('--parallax-y', y + 'px');
      el.style.translate = x + 'px ' + y + 'px';
    });
    rafId = null;
  }

  if (window.matchMedia('(min-width: 900px)').matches) {
    document.addEventListener('mousemove', handleMouseMove);
  }
})();
