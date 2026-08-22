(function () {

  var REDUCE_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function getCount(btn) {
    var el = btn.querySelector('.like-count, .repost-count');
    if (!el) return null;
    var n = parseInt(el.textContent.trim(), 10);
    return isNaN(n) ? null : n;
  }

  function setCount(btn, value) {
    var el = btn.querySelector('.like-count, .repost-count');
    if (el) el.textContent = Math.max(0, value);
  }

  function postInBackground(form) {
    return fetch(form.action, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: new FormData(form),
      credentials: 'same-origin',
    });
  }


  document.querySelectorAll('form.like-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var btn = form.querySelector('.like-btn');
      e.preventDefault();
      if (!btn || form.dataset.busy === '1') return;
      form.dataset.busy = '1';

      var willLike = !btn.classList.contains('is-liked');
      var before = getCount(btn);

      btn.classList.toggle('is-liked', willLike);
      if (before !== null) setCount(btn, before + (willLike ? 1 : -1));

      if (willLike && !REDUCE_MOTION) {
        var burst = form.querySelector('.like-burst');
        if (burst) {
          burst.classList.remove('is-active');
          void burst.offsetWidth; 
          burst.classList.add('is-active');
        }
      }

      postInBackground(form)
        .catch(function () {
          // мережа підвела — повертаємо як було
          btn.classList.toggle('is-liked', !willLike);
          if (before !== null) setCount(btn, before);
        })
        .finally(function () {
          form.dataset.busy = '0';
        });
    });
  });

 
  document.querySelectorAll('form.repost-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var btn = form.querySelector('.repost-btn');
      e.preventDefault();
      if (!btn || form.dataset.busy === '1') return;
      form.dataset.busy = '1';

      var willRepost = !btn.classList.contains('is-reposted');
      var before = getCount(btn);

      btn.classList.toggle('is-reposted', willRepost);
      if (before !== null) setCount(btn, before + (willRepost ? 1 : -1));

      postInBackground(form)
        .catch(function () {
          btn.classList.toggle('is-reposted', !willRepost);
          if (before !== null) setCount(btn, before);
        })
        .finally(function () {
          form.dataset.busy = '0';
        });
    });
  });

  
  document.querySelectorAll('[data-dbltap-like]').forEach(function (media) {
    var card = media.closest('[data-post-card]');
    if (!card) return;
    var likeForm = card.querySelector('form.like-form');
    if (!likeForm) return;

    media.addEventListener('dblclick', function () {
      var btn = likeForm.querySelector('.like-btn');
      var alreadyLiked = btn && btn.classList.contains('is-liked');

      var overlay = media.querySelector('.dbltap-heart');
      if (overlay && !REDUCE_MOTION) {
        overlay.classList.remove('is-active');
        void overlay.offsetWidth;
        overlay.classList.add('is-active');
      }

      if (!alreadyLiked) {
        likeForm.requestSubmit ? likeForm.requestSubmit() : likeForm.submit();
      }
    });
  });

  
  document.querySelectorAll('.alert.alert-dismissible').forEach(function (alertEl) {
    window.setTimeout(function () {
      if (window.bootstrap && window.bootstrap.Alert) {
        var instance = window.bootstrap.Alert.getOrCreateInstance(alertEl);
        instance.close();
      } else {
        alertEl.classList.remove('show');
      }
    }, 5000);
  });

  
  document.querySelectorAll('[data-collapse-chevron]').forEach(function (btn) {
    var targetSelector = btn.getAttribute('data-bs-target');
    var target = targetSelector ? document.querySelector(targetSelector) : null;
    if (!target) return;
    target.addEventListener('shown.bs.collapse', function () { btn.classList.add('is-open'); });
    target.addEventListener('hidden.bs.collapse', function () { btn.classList.remove('is-open'); });
  });

})();