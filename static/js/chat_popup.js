(function () {
  const trigger = document.getElementById('chat-popup-trigger');
  const popup = document.getElementById('chat-popup');

  if (!trigger || !popup) return;

  const title    = document.getElementById('chat-popup-title');
  const backBtn  = document.getElementById('chat-popup-back');
  const closeBtn = document.getElementById('chat-popup-close');
  const body     = document.getElementById('chat-popup-body');

  const listUrl = popup.dataset.listUrl;
  const conversationUrlBase = popup.dataset.conversationUrlBase;

  const LOADING_HTML =
    '<div class="p-3 d-flex flex-column gap-2">' +
    '<div class="skeleton" style="height:52px;border-radius:12px;"></div>' +
    '<div class="skeleton" style="height:52px;border-radius:12px;"></div>' +
    '<div class="skeleton" style="height:52px;border-radius:12px;"></div>' +
    '</div>';

  let pollTimer = null;
  let currentChatId = null;

  function getCsrfToken() {
    const input = document.querySelector('#popup-csrf-form input[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  function openPopup() {
    popup.classList.remove('d-none');
    popup.classList.add('pop-in');
    trigger.classList.add('d-none');
    loadList();
  }

  function closePopup() {
    popup.classList.add('d-none');
    popup.classList.remove('pop-in');
    trigger.classList.remove('d-none');
    stopPolling();
    currentChatId = null;
  }

  function showListHeader() {
    title.textContent = 'Повідомлення';
    backBtn.classList.add('d-none');
  }

  function showConversationHeader(name) {
    title.textContent = name;
    backBtn.classList.remove('d-none');
  }

  function loadList() {
    stopPolling();
    currentChatId = null;
    showListHeader();
    body.innerHTML = LOADING_HTML;

    fetch(listUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (res) { return res.text(); })
      .then(function (html) {
        body.innerHTML = html;
      })
      .catch(function () {
        body.innerHTML = '<p class="text-muted small text-center p-4">Не вдалося завантажити чати.</p>';
      });
  }

  function openConversation(chatId, chatName) {
    stopPolling();
    currentChatId = chatId;
    showConversationHeader(chatName);
    body.innerHTML = LOADING_HTML;

    const url = conversationUrlBase.replace('0', chatId);

    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (res) { return res.text(); })
      .then(function (html) {
        body.innerHTML = html;
        scrollMessagesToBottom();
        startPolling();
      })
      .catch(function () {
        body.innerHTML = '<p class="text-muted small text-center p-4">Не вдалося відкрити чат.</p>';
      });
  }

  function scrollMessagesToBottom() {
    const box = document.getElementById('popup-messages');
    if (box) box.scrollTop = box.scrollHeight;
  }

  function startPolling() {
    pollTimer = setInterval(function () {
      const box = document.getElementById('popup-messages');
      if (!box || !currentChatId) return;

      fetch(box.dataset.pollUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(function (res) { return res.text(); })
        .then(function (html) {
          const wasNearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 60;
          box.innerHTML = html;
          if (wasNearBottom) scrollMessagesToBottom();
        })
        .catch(function () {});
    }, 3000);
  }

  function sendMessage(form) {
    const input = form.querySelector('input[name="text"]');
    const text = input.value.trim();
    if (!text) return;

    const formData = new FormData();
    formData.append('text', text);
    formData.append('csrfmiddlewaretoken', getCsrfToken());

    input.value = '';
    input.disabled = true;

    fetch(form.dataset.sendUrl, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: formData,
    })
      .then(function () {
        const box = document.getElementById('popup-messages');
        if (!box) return;
        return fetch(box.dataset.pollUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
          .then(function (res) { return res.text(); })
          .then(function (html) {
            box.innerHTML = html;
            scrollMessagesToBottom();
          });
      })
      .finally(function () {
        input.disabled = false;
        input.focus();
      });
  }



  trigger.addEventListener('click', function (e) {
    e.preventDefault();
    openPopup();
  });

  closeBtn.addEventListener('click', closePopup);

  backBtn.addEventListener('click', loadList);


  body.addEventListener('click', function (e) {
    const item = e.target.closest('.chat-popup-item');
    if (item) {
      openConversation(item.dataset.chatId, item.dataset.chatName);
    }
  });

  body.addEventListener('submit', function (e) {
    const form = e.target.closest('#popup-send-form');
    if (form) {
      e.preventDefault();
      sendMessage(form);
    }
  });
})();
