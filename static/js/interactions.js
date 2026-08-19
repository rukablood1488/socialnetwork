(function () {

  var REDUCE_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var ANIM_DELAY = REDUCE_MOTION ? 0 : 260;

  function submitAfter(form, delay) {
    if (!delay) { form.submit(); return; }
    window.setTimeout(function () { form.submit(); }, delay);
  }

  
  document.querySelectorAll('form.like-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var btn = form.querySelector('.like-btn');
      if (!btn || form.dataset.animating === '1') return;

      e.preventDefault();
      form.dataset.animating = '1';

      var willLike = !btn.classList.contains('is-liked');
      btn.classList.toggle('is-liked', willLike);

      if (willLike) {
        var burst = form.querySelector('.like-burst');
        if (burst) {
          burst.classList.remove('is-active');
         
          void burst.offsetWidth;
          burst.classList.add('is-active');
        }
      }

      submitAfter(form, ANIM_DELAY);
    });
  });

  
  document.querySelectorAll('form.repost-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var btn = form.querySelector('.repost-btn');
      if (!btn || form.dataset.animating === '1') return;

      e.preventDefault();
      form.dataset.animating = '1';
      btn.classList.toggle('is-reposted');
      submitAfter(form, ANIM_DELAY);
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
      if (overlay) {
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
