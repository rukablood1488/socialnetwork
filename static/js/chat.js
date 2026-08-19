(function () {

  const messagesBox = document.getElementById('messages-box');

  if (messagesBox) {
    const pollUrl = messagesBox.dataset.pollUrl;
    const POLL_INTERVAL = 3000;

    function scrollToBottom() {
      messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    scrollToBottom();

    function pollMessages() {
      fetch(pollUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(function (res) { return res.text(); })
        .then(function (html) {
          const wasNearBottom =
            messagesBox.scrollHeight - messagesBox.scrollTop - messagesBox.clientHeight < 80;

          const currentCount = messagesBox.querySelectorAll('[data-message-id]').length;
          messagesBox.innerHTML = html;
          const newCount = messagesBox.querySelectorAll('[data-message-id]').length;

          if (wasNearBottom || newCount > currentCount) {
            scrollToBottom();
          }
        })
        .catch(function () {});
    }

    setInterval(pollMessages, POLL_INTERVAL);
  }

  const sidebarSearch  = document.getElementById('sidebar-chat-search');
  const sidebarResults = document.getElementById('sidebar-search-results');

  if (sidebarSearch && sidebarResults) {
    const suggestUrl = sidebarSearch.dataset.mentionUrl;
    let debounceTimer = null;

    sidebarSearch.addEventListener('input', function () {
      const query = sidebarSearch.value.trim();
      clearTimeout(debounceTimer);

      if (!query) {
        sidebarResults.innerHTML = '';
        sidebarResults.classList.add('d-none');
        return;
      }

      debounceTimer = setTimeout(function () {
        fetch(suggestUrl + '?q=' + encodeURIComponent(query), {
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
          .then(function (res) { return res.json(); })
          .then(function (data) { renderSidebarResults(data.results); })
          .catch(function () { sidebarResults.classList.add('d-none'); });
      }, 200);
    });

    function renderSidebarResults(users) {
      sidebarResults.innerHTML = '';

      if (!users.length) {
        sidebarResults.classList.add('d-none');
        return;
      }

      users.forEach(function (u) {
        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'list-group-item list-group-item-action d-flex align-items-center gap-2';

        if (u.avatar_url) {
          const img = document.createElement('img');
          img.src = u.avatar_url;
          img.width = 28;
          img.height = 28;
          img.className = 'rounded-circle';
          img.style.objectFit = 'cover';
          item.appendChild(img);
        } else {
          const placeholder = document.createElement('div');
          placeholder.className = 'rounded-circle bg-secondary d-flex align-items-center justify-content-center text-white';
          placeholder.style.width = '28px';
          placeholder.style.height = '28px';
          placeholder.style.fontSize = '0.7rem';
          placeholder.textContent = u.username.charAt(0).toUpperCase();
          item.appendChild(placeholder);
        }

        const label = document.createElement('span');
        label.textContent = '@' + u.username;
        item.appendChild(label);

        item.addEventListener('click', function () {
          openChatWith(u.id);
        });

        sidebarResults.appendChild(item);
      });

      sidebarResults.classList.remove('d-none');
    }

    function openChatWith(userId) {
      const csrfInput = document.querySelector('#csrf-form input[name=csrfmiddlewaretoken]');

      const form = document.createElement('form');
      form.method = 'post';
      form.action = '/chat/create/' + userId + '/';

      const csrf = document.createElement('input');
      csrf.type = 'hidden';
      csrf.name = 'csrfmiddlewaretoken';
      csrf.value = csrfInput ? csrfInput.value : '';
      form.appendChild(csrf);

      document.body.appendChild(form);
      form.submit();
    }

    document.addEventListener('click', function (e) {
      if (e.target !== sidebarSearch && !sidebarResults.contains(e.target)) {
        sidebarResults.classList.add('d-none');
      }
    });
  }
})();
