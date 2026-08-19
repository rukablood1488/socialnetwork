(function () {
  const toggles = document.querySelectorAll('.password-toggle');

  toggles.forEach(function (btn) {
    const targetId = btn.dataset.target;
    const input = document.getElementById(targetId);
    if (!input) return;

    btn.addEventListener('click', function () {
      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.querySelector('use').setAttribute('href', isHidden ? '#icon-eye-off' : '#icon-eye');
      btn.setAttribute('aria-label', isHidden ? 'Приховати пароль' : 'Показати пароль');
    });
  });
})();
