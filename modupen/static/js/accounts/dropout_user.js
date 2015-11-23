$(document).ready(function() {

  // Prevent CSRF token problem before sending reqeust with ajax
  function setCSRFToken() {
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': $.cookie('csrftoken')
      }
    });
  }

  // Dropout user
  $(document).on('submit', '#dropout-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
		$('#loading-icon').show();
    
    // Prevent from double click
    $('#dropout-btn').button('loading');
    
    // Initialize alert message
    $('#dropout-form .alert-danger').text('').addClass('hidden');
    $('#dropout-form .input-group').removeClass('has-error');
    
    setCSRFToken();
    
    $.ajax({
      url: '/user/delete/',
      type: 'POST',
      data: {
        'password': $('#dropout-form input:eq(1)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')
      }
    }).done(function(data) {
			// Failed to dropout
      if (data.state == 'fail') {
        switch (data.code) {
          case 1:
            $('#dropout-form .alert-danger').text('비밀번호를 입력해주세요').removeClass('hidden');
            break;
          case 2:
            $('#dropout-form .alert-danger').text('비밀번호가 불일치합니다').removeClass('hidden');
            $('#dropout-form .input-group:eq(0)').addClass('has-error');
            break;
          default:
            $('#dropout-form .alert-danger').text('회원 탈퇴에 실패했습니다').removeClass('hidden');
            break;
        }
      }
      // Succeed to dropout and move to the main page
      else {
        location.href = '/';
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
      $('#dropout-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });
});
