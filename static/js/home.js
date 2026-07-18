// =====================================================
// home.js — Home Dashboard interactions
// =====================================================

document.addEventListener('DOMContentLoaded', () => {

  // Mobile: sidebar open/close (hook this up to a hamburger button
  // if/when one is added to the topbar for small screens)
  const sidebar = document.getElementById('sidebar');

  window.toggleSidebar = () => {
    sidebar.classList.toggle('open');
  };

  // "Join" button demo feedback (backend not connected yet)
  document.querySelectorAll('.btn-ghost').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.textContent = '✅ सामील झालात';
      btn.disabled = true;
      btn.style.opacity = '0.7';
    });
  });

});
