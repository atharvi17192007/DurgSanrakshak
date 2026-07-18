// =====================================================
// signup.js — Signup page interactions
// आता खऱ्या Flask backend (/api/signup) ला जोडलेलं आहे
// =====================================================

document.addEventListener('DOMContentLoaded', () => {

  // ---------- Password show/hide toggle ----------
  document.querySelectorAll('.toggle-eye').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.target);
      input.type = input.type === 'password' ? 'text' : 'password';
    });
  });

  const form = document.getElementById('signupForm');
  const toast = document.getElementById('toast');
  const passInput = document.getElementById('signupPass');
  const strengthBars = document.querySelectorAll('.strength-meter span');
  const strengthLabel = document.getElementById('strengthLabel');

  const strengthColors = ['#B23B3B', '#D9601A', '#D4A24C', '#2F5233'];
  const strengthText = ['कमकुवत', 'ठीक आहे', 'चांगला', 'मजबूत'];

  function scorePassword(pw) {
    let score = 0;
    if (pw.length >= 6) score++;
    if (pw.length >= 10) score++;
    if (/[A-Z]/.test(pw) && /[0-9]/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    return Math.min(score, 4);
  }

  passInput.addEventListener('input', () => {
    const score = scorePassword(passInput.value);
    strengthBars.forEach((bar, i) => {
      bar.style.background = i < score ? strengthColors[Math.max(score - 1, 0)] : '#E3D3B4';
    });
    strengthLabel.textContent = passInput.value ? strengthText[Math.max(score - 1, 0)] : '\u00A0';
  });

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

    const fullName = document.getElementById('fullName').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const pass = document.getElementById('signupPass').value.trim();
    const confirm = document.getElementById('confirmPass').value.trim();
    const terms = document.getElementById('terms').checked;

    ['fullName', 'email', 'phone', 'confirmPass'].forEach(id => clearError(id, id + 'Error'));

    if (fullName === '') {
      showError('fullName', 'fullNameError', 'पूर्ण नाव टाका');
      valid = false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      showError('email', 'emailError', 'योग्य ईमेल टाका');
      valid = false;
    }

    const phoneRegex = /^[6-9]\d{9}$/;
    if (!phoneRegex.test(phone)) {
      showError('phone', 'phoneError', '10 अंकी मोबाईल क्रमांक टाका');
      valid = false;
    }

    if (pass.length < 6) {
      valid = false;
    }

    if (confirm !== pass || confirm === '') {
      showError('confirmPass', 'confirmPassError', 'पासवर्ड जुळत नाही');
      valid = false;
    }

    if (!terms) {
      showToast('⚠️ कृपया अटी व शर्ती स्वीकारा');
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
    submitBtn.textContent = 'नोंदणी होत आहे...';

    try {
      const formData = new FormData();
      formData.append('fullName', fullName);
      formData.append('email', email);
      formData.append('phone', phone);
      formData.append('password', pass);

      const response = await fetch('/api/signup', {
        method: 'POST',
        body: formData
      });
      const result = await response.json();

      if (result.success) {
        showToast('✅ ' + result.message + ' आता लॉगिन करा.');
        setTimeout(() => {
          window.location.href = '/';
        }, 1200);
      } else {
        showToast('❌ ' + result.message);
        submitBtn.disabled = false;
        submitBtn.textContent = 'नोंदणी करा';
      }
    } catch (err) {
      showToast('❌ काहीतरी चूक झाली, परत प्रयत्न करा.');
      submitBtn.disabled = false;
      submitBtn.textContent = 'नोंदणी करा';
    }
  });

});
