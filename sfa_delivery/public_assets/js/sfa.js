(function () {
  var key = 'sfa-open-details';
  var details = document.querySelectorAll('details');
  if (!details.length) return;

  try {
    var saved = JSON.parse(sessionStorage.getItem(key) || '[]');
    details.forEach(function (el, idx) {
      if (saved.indexOf(idx) !== -1) {
        el.open = true;
      }
      el.addEventListener('toggle', function () {
        var open = [];
        details.forEach(function (d, i) {
          if (d.open) open.push(i);
        });
        sessionStorage.setItem(key, JSON.stringify(open));
      });
    });
  } catch (e) {
    // best-effort UI persistence
  }
})();
