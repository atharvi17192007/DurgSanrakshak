// =====================================================
// event.js — Event page interactions
// Create Event व Join आता खऱ्या Flask backend ला जोडलेले आहेत
// (Filter tabs आणि modal उघड-बंद करणं मात्र JS मध्येच, कारण तो फक्त UI आहे)
// =====================================================

document.addEventListener('DOMContentLoaded', () => {

  // ---------- Status filter tabs ----------
  const tabs = document.querySelectorAll('#statusTabs button');
  const cards = document.querySelectorAll('.event-card');
  const emptyState = document.getElementById('emptyState');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const filter = tab.dataset.filter;
      let visibleCount = 0;

      cards.forEach(card => {
        const show = filter === 'All' || card.dataset.status === filter;
        card.style.display = show ? '' : 'none';
        if (show) visibleCount++;
      });

      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    });
  });

  // ---------- Create Event modal (उघड/बंद फक्त UI साठी; submit खरंच backend ला जातो) ----------
  const createModal = document.getElementById('createModal');
const openCreateBtn = document.getElementById('openCreateModal');
const closeCreateBtn = document.getElementById('closeCreateModal');

if (openCreateBtn && createModal) {
  openCreateBtn.addEventListener('click', () => {
    createModal.classList.add('open');
  });
}

if (closeCreateBtn && createModal) {
  closeCreateBtn.addEventListener('click', () => {
    createModal.classList.remove('open');
  });

  createModal.addEventListener('click', (e) => {
    if (e.target === createModal) {
      createModal.classList.remove('open');
    }
  });
}
  // खऱ्या backend ला जातो आणि यशस्वी झाल्यावर पेज परत लोड होतं.

  // ---------- Event Details modal ----------
  const detailsModal = document.getElementById('detailsModal');
  document.getElementById('closeDetailsModal').addEventListener('click', () => detailsModal.classList.remove('open'));
  detailsModal.addEventListener('click', (e) => { if (e.target === detailsModal) detailsModal.classList.remove('open'); });

  document.querySelectorAll('.view-details-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const card = btn.closest('.event-card');
      const status = card.dataset.status;
      const eventId = card.dataset.eventId;
      const alreadyJoined = card.dataset.joined === 'true';

      document.getElementById('detailEventName').textContent = card.dataset.name;
      document.getElementById('detailFort').textContent = card.dataset.fort;
      document.getElementById('detailDate').textContent = card.dataset.date;
      document.getElementById('detailTime').textContent = card.dataset.time;
document.getElementById('detailParticipantCount').textContent =
    card.dataset.participants;
      const badge = document.getElementById('detailStatusBadge');
      badge.textContent = status;
      badge.className = 'badge-pill badge-' + status;

      // ---------- Join फॉर्मचा action dynamically त्या event च्या id वर सेट करणं ----------
      const joinForm = document.getElementById('joinEventForm');
      const joinBtn = document.getElementById('joinEventBtn');
joinForm.action = '/api/events/' + eventId + '/join';
      if (status === 'Completed') {
        joinForm.style.display = 'none';
      } else if (alreadyJoined) {
        joinForm.style.display = '';
        joinBtn.textContent = '✅ आधीच सामील आहात';
        joinBtn.disabled = true;
      } else {
        joinForm.style.display = '';
        joinBtn.textContent = 'Event ला सामील व्हा';
        joinBtn.disabled = false;
      }

      // ---------- Participants Load ----------
fetch('/api/events/' + eventId + '/details')
  .then(response => response.json())
  .then(data => {

    const participantList = document.getElementById('detailParticipantList');

    participantList.innerHTML = "";

    if (data.participants.length === 0) {
      participantList.innerHTML = "<p>अजून कोणी सहभागी झाले नाही.</p>";
    } 
    else {
      data.participants.forEach(name => {
       participantList.innerHTML += `
  <div class="participant-item">
    <p>👤 ${name}</p>
  </div>
`;
      });
    }

    document.getElementById('detailParticipantCount').textContent =
      data.participant_count;

  })
  .catch(error => {
    console.log("Participant load error:", error);
  });
      detailsModal.classList.add('open');
    });
  });
  // NOTE: joinEventForm ला पण JS submit-handler नाहीये — तो खरंच
  // /api/events/join/<id> ला POST करतो आणि Flask परत /event वर पाठवतं.

});
