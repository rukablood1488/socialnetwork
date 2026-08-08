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

        const avatar = u.avatar_url
          ? '<img src="' + u.avatar_url + '" width="28" height="28" class="rounded-circle" style="object-fit:cover;">'
          : '<div class="rounded-circle bg-secondary d-flex align-items-center justify-content-center text-white" ' +
            'style="width:28px;height:28px;font-size:0.7rem;">' + u.username.charAt(0).toUpperCase() + '</div>';

        item.innerHTML = avatar + '<span>@' + u.username + '</span>';

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