// =====================================================
// wallet.js — Wallet page interactions
// Redeem आता खऱ्या /api/wallet/redeem backend ला जोडलेलं आहे
// =====================================================

document.addEventListener('DOMContentLoaded', () => {

  const redeemModal = document.getElementById('redeemModal');
  const toast = document.getElementById('toast');
  let selectedBtn = null;

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2800);
  }

  document.querySelectorAll('.redeem-btn').forEach(btn => {
    if (btn.disabled) return;
    btn.addEventListener('click', () => {
      selectedBtn = btn;
      document.getElementById('redeemItemName').textContent = btn.dataset.item;
      document.getElementById('redeemItemCost').textContent = btn.dataset.cost;
      redeemModal.classList.add('open');
    });
  });

  document.getElementById('closeRedeemModal').addEventListener('click', () => redeemModal.classList.remove('open'));
  redeemModal.addEventListener('click', (e) => { if (e.target === redeemModal) redeemModal.classList.remove('open'); });

  document.getElementById('confirmRedeemBtn').addEventListener('click', async () => {
    if (!selectedBtn) return;

    const confirmBtn = document.getElementById('confirmRedeemBtn');
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'होत आहे...';

    try {
      const formData = new FormData();
      formData.append('item_key', selectedBtn.dataset.itemKey);

      const response = await fetch('/api/wallet/redeem', { method: 'POST', body: formData });
      const result = await response.json();

      redeemModal.classList.remove('open');

      if (result.success) {
        showToast('✅ ' + result.message);
        setTimeout(() => window.location.reload(), 1000);
      } else {
        showToast('❌ ' + result.message);
      }
    } catch (err) {
      showToast('❌ काहीतरी चूक झाली.');
    } finally {
      confirmBtn.disabled = false;
      confirmBtn.textContent = 'Confirm Redeem';
    }
  });

});
