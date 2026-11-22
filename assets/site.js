document.querySelectorAll('input.filter').forEach(function (inp) {
  var table = document.querySelector('table[data-filter]');
  inp.addEventListener('input', function () {
    var q = inp.value.toLowerCase();
    table.querySelectorAll('tbody tr').forEach(function (tr) {
      tr.style.display = tr.textContent.toLowerCase().indexOf(q) === -1 ? 'none' : '';
    });
  });
});
