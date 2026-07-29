(function () {
  const input      = document.getElementById('search-input');
  const resultsBox = document.getElementById('search-results');
  const spinner    = document.getElementById('search-spinner');

  if (!input || !resultsBox) {
    return;
  }

  const searchUrl = resultsBox.dataset.searchUrl;
  const emptyMessage = '<p class="text-muted text-center py-4">Почніть вводити, щоб знайти користувачів або групи.</p>';

  let debounceTimer  = null;
  let currentRequest = null;

  input.addEventListener('input', function () {
    const query = input.value.trim();

    clearTimeout(debounceTimer);

    if (!query) {
      resultsBox.innerHTML = emptyMessage;
      if (spinner) spinner.classList.add('d-none');
      return;
    }

    if (spinner) spinner.classList.remove('d-none');

    debounceTimer = setTimeout(function () {
      if (currentRequest) {
        currentRequest.abort();
      }

      const controller = new AbortController();
      currentRequest = controller;

      fetch(searchUrl + '?q=' + encodeURIComponent(query), {
        signal: controller.signal,
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      })
        .then(function (response) { return response.text(); })
        .then(function (html) {
          resultsBox.innerHTML = html;
          if (spinner) spinner.classList.add('d-none');
        })
        .catch(function (err) {
          if (err.name !== 'AbortError' && spinner) {
            spinner.classList.add('d-none');
          }
        });
    }, 300);
  });
})();