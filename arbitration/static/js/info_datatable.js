$(document).ready(function () {
      $('#staticDatatable').DataTable({
          "searching": false,
          "pageLength": 15,
          "lengthMenu": [[15, 30, 60, 100], [15, 30, 60, 100]],
          "info": true,
          // 'order': [[0, 'desc']],
    });
});