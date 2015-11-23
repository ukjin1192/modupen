$(document).ready(function() {

  // Activate/deactivate tab
  $(document).on('show.bs.tab', '#terms-tab', function() {
    $('#terms-tab').addClass('active');
    $('#policy-tab').removeClass('active');
  });
  $(document).on('show.bs.tab', '#policy-tab', function() {
    $('#policy-tab').addClass('active');
    $('#terms-tab').removeClass('active');
  });
});
