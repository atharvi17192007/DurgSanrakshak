// =====================================================
// location.js — Location page interactions
// "दिशा दाखवा" आता खऱ्या Google Maps ला (fort च्या खऱ्या GPS coordinates सह) घेऊन जातो.
// "भेट दिली ✓" आता खरंच /api/forts/mark-visited/<id> ला POST करतो.
// =====================================================

document.addEventListener('DOMContentLoaded', () => {

  // ---------- Filter chips ----------
  const chips = document.querySelectorAll('#filterChips button');
  const listItems = document.querySelectorAll('.fort-list-item');

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const filter = chip.dataset.filter;

      listItems.forEach(item => {
        const visited = item.dataset.visited === 'true';
        const isEventFort = item.dataset.event === 'true';
        let show = true;
        if (filter === 'visited') show = visited;
        if (filter === 'not-visited') show = !visited;
        if (filter === 'event') show = isEventFort;
        item.style.display = show ? '' : 'none';
      });
    });
  });

  // ---------- Popover उघडणं (list किंवा map pin वरून) ----------
  const popover = document.getElementById('mapPopover');
  const popoverName = document.getElementById('popoverName');
  const popoverDist = document.getElementById('popoverDist');
  const popoverDirections = document.getElementById('popoverDirections');
  const popoverVisitedForm = document.getElementById('popoverVisitedForm');
  const popoverVisitedBtn = document.getElementById('popoverVisited');

  function openPopoverFor(name, lat, lng, visited, fortId) {
    popoverName.textContent = name;
    popoverDist.textContent = visited ? '✅ तुम्ही भेट दिली आहे' : '📍 अजून भेट दिलेली नाही';

    // ---- खरा Google Maps directions link ----
    popoverDirections.href = 'https://www.google.com/maps/dir/?api=1&destination=' + lat + ',' + lng;

    popoverVisitedForm.action = '/api/forts/mark-visited/' + fortId;
    if (visited) {
      popoverVisitedBtn.textContent = '✅ भेट दिली';
      popoverVisitedBtn.disabled = true;
    } else {
      popoverVisitedBtn.textContent = 'भेट दिली ✓';
      popoverVisitedBtn.disabled = false;
    }

    popover.classList.add('open');
  }

  listItems.forEach(item => {
    item.addEventListener('click', () => {
      listItems.forEach(i => i.classList.remove('selected'));
      item.classList.add('selected');
      // list मध्ये lat/lng नाहीये, म्हणून त्याच fort च्या map pin वरून माहिती घेणं
      const fortId = item.dataset.fortId;
      const pin = document.querySelector('.map-pin[data-fort-id="' + fortId + '"]');
      if (pin) {
        openPopoverFor(pin.dataset.name, pin.dataset.lat, pin.dataset.lng, pin.dataset.visited === 'true', fortId);
      }
    });
  });

  document.querySelectorAll('.map-pin').forEach(pin => {
    pin.addEventListener('click', () => {
      openPopoverFor(pin.dataset.name, pin.dataset.lat, pin.dataset.lng, pin.dataset.visited === 'true', pin.dataset.fortId);
    });
  });
  // popoverVisitedForm खरंच backend ला POST होतो (JS ने अडवत नाही).

});
