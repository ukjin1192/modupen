$(document).ready(function() {

  // Prevent CSRF token problem before sending reqeust with ajax
  function setCSRFToken() {
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': $.cookie('csrftoken')
      }
    });
  }

  // Update nickname
  $(document).on('submit', '#update-nickname-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#update-nickname-btn').button('loading');
    
    // Initialize alert message
    $('#update-nickname-form .alert-success, #update-nickname-form .alert-danger').text('').addClass('hidden');
    $('#update-nickname-form .input-group').removeClass('has-error');
    
    setCSRFToken();
		
    var nickname = $('#update-nickname-form input:eq(1)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '');
    
    $.ajax({
      url: '/user/nickname/update/',
      type: 'POST',
      data: {
        'nickname': nickname
      }
    }).done(function(data) {
			// Failed to update nickname
      if (data.state == 'fail') {
        switch (data.code) {
          case 1:
            $('#update-nickname-form .alert-danger').text('변경할 별명을 입력해주세요').removeClass('hidden');
            $('#update-nickname-form .input-group:eq(0)').addClass('has-error');
            break;
          case 2:
            $('#update-nickname-form .alert-danger').text('이미 존재하는 별명입니다').removeClass('hidden');
            $('#update-nickname-form .input-group:eq(0)').addClass('has-error');
            break;
          default:
            $('#update-nickname-form .alert-danger').text('별명 변경에 실패했습니다').removeClass('hidden');
            break;
        }
      }
      // Succeed to update nickname
      else {
        $('#update-nickname-form .alert-success').text('별명을 변경했습니다').removeClass('hidden');
				
				// Update sidebar
        $('#sidebar-nickname').text(nickname);
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
      $('#update-nickname-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });
});
