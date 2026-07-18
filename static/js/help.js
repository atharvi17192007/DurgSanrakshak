// =====================================================
// help.js — Help page interactions
// Report/Feedback/Contact Admin आता खऱ्या backend forms ने साठतात.
// इथे फक्त UI-only गोष्टी: FAQ accordion, star rating निवड, modal उघड-बंद,
// आणि page reload नंतर (?submitted=...) टोस्ट दाखवणं.
// =====================================================

document.addEventListener('DOMContentLoaded', () => {

  const toast = document.getElementById('toast');
  function showToast(message) {
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3200);
  }

  // ---- Server ने पाठवलेला success message असेल तर दाखवणं ----
  if (window.__toastMessage) {
    showToast(window.__toastMessage);
    // URL मधून ?submitted=... काढून टाकणं, म्हणजे refresh केल्यावर परत toast दिसणार नाही
    const url = new URL(window.location);
    url.searchParams.delete('submitted');
    window.history.replaceState({}, '', url);
  }

  // ---------- FAQ accordion ----------
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const wasOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!wasOpen) item.classList.add('open');
    });
  });

  // ---------- Quick card scroll shortcuts ----------
  document.getElementById('scrollToContacts').addEventListener('click', () => {
    document.getElementById('scrollToContactsAnchor').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  document.getElementById('scrollToSafety').addEventListener('click', () => {
    document.getElementById('scrollToSafetyAnchor').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  // ---------- Star rating (हा फक्त निवड दाखवतो; खरा value hidden input मध्ये जातो) ----------
  const stars = document.querySelectorAll('#starRow svg');
  const ratingInput = document.getElementById('ratingInput');
  stars.forEach(star => {
    star.addEventListener('click', () => {
      const selectedRating = parseInt(star.dataset.val, 10);
      ratingInput.value = selectedRating;
      stars.forEach(s => {
        s.classList.toggle('filled', parseInt(s.dataset.val, 10) <= selectedRating);
      });
    });
  });

  // ---------- Report Issue modal ----------
  const reportModal = document.getElementById('reportModal');
  document.getElementById('openReportModal').addEventListener('click', () => reportModal.classList.add('open'));
  document.getElementById('closeReportModal').addEventListener('click', () => reportModal.classList.remove('open'));
  reportModal.addEventListener('click', (e) => { if (e.target === reportModal) reportModal.classList.remove('open'); });
  // reportForm खरंच /api/help/report ला POST होतो.

  // ---------- Contact Admin modal ----------
  const contactAdminModal = document.getElementById('contactAdminModal');
  document.getElementById('openContactAdminModal').addEventListener('click', () => contactAdminModal.classList.add('open'));
  document.getElementById('closeContactAdminModal').addEventListener('click', () => contactAdminModal.classList.remove('open'));
  contactAdminModal.addEventListener('click', (e) => { if (e.target === contactAdminModal) contactAdminModal.classList.remove('open'); });
  // contactAdminForm खरंच /api/help/contact-admin ला POST होतो.

});
