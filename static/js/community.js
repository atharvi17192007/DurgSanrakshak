// =====================================================
// community.js — Community page interactions
// Create/Join/Post/Like/Comment आता खऱ्या backend forms ने होतात.
// इथे फक्त UI-only गोष्टी आहेत: modal उघड-बंद, filter tabs, composer type निवड.
// =====================================================

document.addEventListener('DOMContentLoaded', () => {

  // ---------- Feed filter tabs ----------
  const feedTabs = document.querySelectorAll('#feedTabs button');
  const posts = document.querySelectorAll('.post-card');
  feedTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      feedTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const type = tab.dataset.type;
      posts.forEach(post => {
        post.style.display = (type === 'All' || post.dataset.type === type) ? '' : 'none';
      });
    });
  });

  // ---------- Composer type चिप निवडणं (hidden input update करतं, जे form submit होताना जातं) ----------
  const postTypeInput = document.getElementById('postTypeInput');
  document.querySelectorAll('#composerType .type-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#composerType .type-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      if (postTypeInput) postTypeInput.value = chip.dataset.type;
    });
  });

  // ---------- Comment box उघड/बंद ----------
  document.querySelectorAll('.comment-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const box = btn.closest('.post-card').querySelector('.comment-box');
      box.classList.toggle('open');
    });
  });

  // ---------- Create Community modal ----------
  const createCommunityModal = document.getElementById('createCommunityModal');
  if (createCommunityModal) {
    document.getElementById('openCreateCommunityModal').addEventListener('click', () => createCommunityModal.classList.add('open'));
    document.getElementById('closeCreateCommunityModal').addEventListener('click', () => createCommunityModal.classList.remove('open'));
    createCommunityModal.addEventListener('click', (e) => { if (e.target === createCommunityModal) createCommunityModal.classList.remove('open'); });
  }

  // ---------- Invite Friends modal ----------
  const inviteModal = document.getElementById('inviteModal');
  const openInviteBtn = document.getElementById('openInviteModal');
  if (inviteModal && openInviteBtn) {
    openInviteBtn.addEventListener('click', () => inviteModal.classList.add('open'));
    document.getElementById('closeInviteModal').addEventListener('click', () => inviteModal.classList.remove('open'));
    inviteModal.addEventListener('click', (e) => { if (e.target === inviteModal) inviteModal.classList.remove('open'); });

    document.getElementById('copyInviteBtn').addEventListener('click', function () {
      const link = document.getElementById('inviteLink');
      link.select();
      navigator.clipboard?.writeText(link.value).catch(() => {});
      this.textContent = '✅ कॉपी झालं!';
      setTimeout(() => { this.textContent = 'लिंक कॉपी करा'; }, 2000);
    });
  }

});
