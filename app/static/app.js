// Minimal JS helpers — most interactivity is handled server-side

// Confirm before delete (backup in case inline onsubmit is stripped)
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', e => {
      if (!confirm(form.dataset.confirm)) e.preventDefault();
    });
  });
});
