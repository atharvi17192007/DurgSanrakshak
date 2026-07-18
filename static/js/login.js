// =====================================================
// login.js — Login page interactions
// आता खऱ्या Flask backend (/api/login) ला जोडलेलं आहे
// =====================================================

document.addEventListener('DOMContentLoaded', () => {

  // ---------- Password show/hide toggle ----------
  document.querySelectorAll('.toggle-eye').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.target);
      input.type = input.type === 'password' ? 'text' : 'password';
    });
  });

  const form = document.getElementById('loginForm');
  const toast = document.getElementById('toast');

  function showError(inputId, errorId, message) {
    document.getElementById(inputId).classList.add('invalid');
    document.getElementById(errorId).textContent = message;
  }

  function clearError(inputId, errorId) {
    document.getElementById(inputId).classList.remove('invalid');
    document.getElementById(errorId).textContent = '';
  }

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2800);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    let valid = true;
    const loginId = document.getElementById('loginId').value.trim();
    const loginPass = document.getElementById('loginPass').value.trim();

    clearError('loginId', 'loginIdError');
    clearError('loginPass', 'loginPassError');

    if (loginId === '') {
      showError('loginId', 'loginIdError', 'ईमेल किंवा मोबाईल क्रमांक टाका');
      valid = false;
    }

    if (loginPass === '') {
      showError('loginPass', 'loginPassError', 'पासवर्ड टाका');
      valid = false;
    }

    if (!valid) {
      form.classList.add('shake');
      setTimeout(() => form.classList.remove('shake'), 300);
      return;
    }

    // ---------- Backend ला खरा request पाठवणं ----------
    const submitBtn = form.querySelector('.btn-primary');
    submitBtn.disabled = true;
    submitBtn.textContent = 'तपासत आहोत...';

    try {
      const formData = new FormData();
      formData.append('loginId', loginId);
      formData.append('loginPass', loginPass);

      const response = await fetch('/api/login', {
        method: 'POST',
        body: formData
      });
      const result = await response.json();

      if (result.success) {
        showToast('✅ ' + result.message);
        setTimeout(() => {
          window.location.href = result.redirect || '/home';
        }, 700);
      } else {
        showToast('❌ ' + result.message);
        submitBtn.disabled = false;
        submitBtn.textContent = 'लॉगिन करा';
      }
    } catch (err) {
      showToast('❌ काहीतरी चूक झाली, परत प्रयत्न करा.');
      submitBtn.disabled = false;
      submitBtn.textContent = 'लॉगिन करा';
    }
  });

});
