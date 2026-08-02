(function () {

  const messagesBox = document.getElementById('messages-box');

  if (messagesBox) {
    const pollUrl = messagesBox.dataset.pollUrl;
    const POLL_INTERVAL = 3000; // 3 секунди

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


  const participantSearch = document.getElementById('participant-search');
  const participantResults = document.getElementById('participant-results');
  const selectedList = document.getElementById('selected-participants');
  const hiddenInputsBox = document.getElementById('participant-hidden-inputs');

  if (participantSearch && participantResults && selectedList && hiddenInputsBox) {
    const suggestUrl = participantSearch.dataset.mentionUrl;
    const selected = new Map();
    let debounceTimer = null;

    participantSearch.addEventListener('input', function () {
      const query = participantSearch.value.trim();
      clearTimeout(debounceTimer);

      if (!query) {
        participantResults.innerHTML = '';
        participantResults.classList.add('d-none');
        return;
      }

      debounceTimer = setTimeout(function () {
        fetch(suggestUrl + '?q=' + encodeURIComponent(query), {
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
          .then(function (res) { return res.json(); })
          .then(function (data) { renderResults(data.results); })
          .catch(function () { participantResults.classList.add('d-none'); });
      }, 200);
    });

    function renderResults(results) {
      participantResults.innerHTML = '';

      const filtered = results.filter(function (u) { return !selected.has(u.username); });

      if (!filtered.length) {
        participantResults.classList.add('d-none');
        return;
      }

      filtered.forEach(function (u) {
        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'list-group-item list-group-item-action d-flex align-items-center gap-2';
        item.innerHTML = avatarHtml(u) + '<span>' + u.username + '</span>';
        item.addEventListener('click', function () {
          addParticipant(u);
          participantSearch.value = '';
          participantResults.innerHTML = '';
          participantResults.classList.add('d-none');
        });
        participantResults.appendChild(item);
      });

      participantResults.classList.remove('d-none');
    }

    function avatarHtml(u) {
      if (u.avatar_url) {
        return '<img src="' + u.avatar_url + '" width="28" height="28" class="rounded-circle" style="object-fit:cover;">';
      }
      return '<div class="rounded-circle bg-secondary d-flex align-items-center justify-content-center text-white" ' +
        'style="width:28px;height:28px;font-size:0.75rem;">' + u.username.charAt(0).toUpperCase() + '</div>';
    }

    function addParticipant(u) {
      selected.set(u.username, u);
      renderSelected();
    }

    function removeParticipant(username) {
      selected.delete(username);
      renderSelected();
    }

    function renderSelected() {
      selectedList.innerHTML = '';
      hiddenInputsBox.innerHTML = '';

      selected.forEach(function (u) {
        const chip = document.createElement('span');
        chip.className = 'badge bg-secondary d-inline-flex align-items-center gap-1 p-2';
        chip.textContent = '@' + u.username + ' ';

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn-close btn-close-white btn-sm';
        removeBtn.style.fontSize = '0.6rem';
        removeBtn.addEventListener('click', function () { removeParticipant(u.username); });

        chip.appendChild(removeBtn);
        selectedList.appendChild(chip);

        
        if (u.id) {
          const hidden = document.createElement('input');
          hidden.type = 'hidden';
          hidden.name = 'participants';
          hidden.value = u.id;
          hiddenInputsBox.appendChild(hidden);
        }
      });
    }
  }
})();