(function () {
  const step1   = document.getElementById('step1');
  const step2   = document.getElementById('step2');
  const input   = document.getElementById('media-input');
  const preview = document.getElementById('media-preview');
  const btnNext = document.getElementById('btn-next');
  const btnBack = document.getElementById('btn-back');

  if (step1 && step2 && input) {

  input.addEventListener('change', function () {
    const file = input.files[0];
    preview.innerHTML = '';

    if (!file) {
      btnNext.disabled = true;
      return;
    }

    const isVideo = file.type.startsWith('video/');

    const imageInput = document.getElementById(input.dataset.imageInput);
    const videoInput = document.getElementById(input.dataset.videoInput);

    const dt = new DataTransfer();
    dt.items.add(file);

    const emptyDt = new DataTransfer();

    if (isVideo) {
      videoInput.files = dt.files;
      imageInput.files = emptyDt.files;
    } else {
      imageInput.files = dt.files;
      videoInput.files = emptyDt.files;
    }

    const url = URL.createObjectURL(file);

    if (isVideo) {
      const video = document.createElement('video');
      video.src = url;
      video.controls = true;
      video.className = 'w-100 rounded anim-scale-in';
      video.style.maxHeight = '420px';
      preview.appendChild(video);
    } else {
      const img = document.createElement('img');
      img.src = url;
      img.className = 'w-100 rounded anim-scale-in';
      img.style.maxHeight = '420px';
      img.style.objectFit = 'contain';
      preview.appendChild(img);
    }

    btnNext.disabled = false;
  });


  if (btnNext) {
    btnNext.addEventListener('click', function () {
      if (!input.files[0]) return;
      step1.classList.add('d-none');
      step2.classList.remove('d-none');
      step2.classList.add('anim-fade-in-up');
    });
  }

  if (btnBack) {
    btnBack.addEventListener('click', function () {
      step2.classList.add('d-none');
      step1.classList.remove('d-none');
      step1.classList.add('anim-fade-in-up');
    });
  }

  }

  const captionInput = document.getElementById('caption-input');
  const dropdown      = document.getElementById('mention-dropdown');

  if (captionInput && dropdown) {
    const mentionUrl = captionInput.dataset.mentionUrl;
    let debounceTimer = null;
    let activeStart = -1;

    captionInput.addEventListener('input', function () {
      const cursorPos = captionInput.selectionStart;
      const text = captionInput.value.slice(0, cursorPos);
      const match = text.match(/@(\w*)$/);

      clearTimeout(debounceTimer);

      if (!match) {
        dropdown.classList.add('d-none');
        dropdown.innerHTML = '';
        activeStart = -1;
        return;
      }

      activeStart = cursorPos - match[0].length;
      const query = match[1];

      if (!query) {
        dropdown.classList.add('d-none');
        return;
      }

      debounceTimer = setTimeout(function () {
        fetch(mentionUrl + '?q=' + encodeURIComponent(query), {
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
          .then(function (res) { return res.json(); })
          .then(function (data) {
            renderDropdown(data.results, query);
          })
          .catch(function () {
            dropdown.classList.add('d-none');
          });
      }, 200);
    });

    function renderDropdown(results, query) {
      if (!results.length) {
        dropdown.classList.add('d-none');
        dropdown.innerHTML = '';
        return;
      }

      dropdown.innerHTML = '';
      results.forEach(function (user) {
        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'list-group-item list-group-item-action d-flex align-items-center gap-2';

        const avatar = document.createElement('div');
        if (user.avatar_url) {
          avatar.innerHTML = '<img src="' + user.avatar_url + '" width="28" height="28" ' +
            'class="rounded-circle" style="object-fit:cover;">';
        } else {
          avatar.className = 'rounded-circle bg-secondary d-flex align-items-center ' +
            'justify-content-center text-white';
          avatar.style.width = '28px';
          avatar.style.height = '28px';
          avatar.style.fontSize = '0.75rem';
          avatar.textContent = user.username.charAt(0).toUpperCase();
        }

        const label = document.createElement('span');
        label.textContent = '@' + user.username;

        item.appendChild(avatar);
        item.appendChild(label);

        item.addEventListener('click', function () {
          insertMention(user.username);
        });

        dropdown.appendChild(item);
      });

      dropdown.classList.remove('d-none');
    }

    function insertMention(username) {
      const before = captionInput.value.slice(0, activeStart);
      const after  = captionInput.value.slice(captionInput.selectionStart);
      const newValue = before + '@' + username + ' ' + after;

      captionInput.value = newValue;
      const newCursor = (before + '@' + username + ' ').length;
      captionInput.focus();
      captionInput.setSelectionRange(newCursor, newCursor);

      dropdown.classList.add('d-none');
      dropdown.innerHTML = '';
      activeStart = -1;
    }

    document.addEventListener('click', function (e) {
      if (e.target !== captionInput && !dropdown.contains(e.target)) {
        dropdown.classList.add('d-none');
      }
    });
  }
})();
