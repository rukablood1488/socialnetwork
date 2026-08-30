(function () {

  function initShareModal(modalEl) {
    var content = modalEl.querySelector('.share-modal-content');
    if (!content) return;

    var shareUrl     = content.dataset.shareUrl;
    var csrfInput    = content.querySelector('input[name=csrfmiddlewaretoken]');
    var searchWrap   = content.querySelector('.share-search-wrap');
    var searchInput  = content.querySelector('.share-search-input');
    var avatarRow    = content.querySelector('.share-avatar-row');
    var avatarBtns   = Array.prototype.slice.call(content.querySelectorAll('.share-avatar-btn'));
    var messageRow   = content.querySelector('.share-message-row');
    var messageInput = content.querySelector('.share-message-input');
    var sendBtn      = content.querySelector('.share-send-btn');
    var confirmEl    = content.querySelector('.share-confirm');

    if (!avatarBtns.length || !sendBtn || !messageRow) return;

    var selected = new Set();

    function syncMessageRow() {
      messageRow.classList.toggle('is-visible', selected.size > 0);
      sendBtn.disabled = selected.size === 0;
    }

    avatarBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = btn.dataset.chatId;
        if (selected.has(id)) {
          selected.delete(id);
          btn.classList.remove('is-selected');
        } else {
          selected.add(id);
          btn.classList.add('is-selected');
        }
        syncMessageRow();
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', function () {
        var q = searchInput.value.trim().toLowerCase();
        avatarBtns.forEach(function (btn) {
          btn.hidden = !(!q || btn.dataset.name.indexOf(q) !== -1);
        });
      });
    }

    function resetState() {
      selected.clear();
      avatarBtns.forEach(function (btn) {
        btn.classList.remove('is-selected');
        btn.hidden = false;
      });
      if (searchInput) searchInput.value = '';
      if (messageInput) messageInput.value = '';
      messageRow.classList.remove('is-visible');
      sendBtn.disabled = true;
      sendBtn.textContent = 'Надіслати';
      confirmEl.classList.remove('is-visible');
      if (avatarRow) avatarRow.hidden = false;
      if (searchWrap) searchWrap.hidden = false;
    }

    function showConfirmation() {
      if (avatarRow) avatarRow.hidden = true;
      if (searchWrap) searchWrap.hidden = true;
      messageRow.classList.remove('is-visible');
      confirmEl.classList.add('is-visible');

      window.setTimeout(function () {
        if (window.bootstrap && window.bootstrap.Modal) {
          window.bootstrap.Modal.getOrCreateInstance(modalEl).hide();
        }
      }, 1100);
    }

    function sendShare() {
      if (!selected.size || sendBtn.disabled) return;
      sendBtn.disabled = true;
      sendBtn.textContent = 'Надсилаємо…';

      var formData = new FormData();
      formData.append('csrfmiddlewaretoken', csrfInput ? csrfInput.value : '');
      formData.append('text', messageInput ? messageInput.value.trim() : '');
      selected.forEach(function (id) { formData.append('chat_ids', id); });

      fetch(shareUrl, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData,
        credentials: 'same-origin',
      })
        .then(function (res) {
          if (!res.ok) throw new Error('share request failed');
          showConfirmation();
        })
        .catch(function () {
          sendBtn.disabled = false;
          sendBtn.textContent = 'Надіслати';
        });
    }

    sendBtn.addEventListener('click', sendShare);


    modalEl.addEventListener('hidden.bs.modal', resetState);
  }

  document.querySelectorAll('[id^="share-modal-"]').forEach(initShareModal);

})();