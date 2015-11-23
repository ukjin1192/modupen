$(document).ready(function() {

  // Prevent CSRF token problem before sending reqeust with ajax
  function setCSRFToken() {
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': $.cookie('csrftoken')
      }
    });
  }

  // Update email
  $(document).on('submit', '#update-email-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#update-email-btn').button('loading');
    
    // Initialize alert message
    $('#update-email-form .alert-success, #update-email-form .alert-danger').text('').addClass('hidden');
    $('#update-email-form .input-group').removeClass('has-error');
    
    setCSRFToken();
    
    $.ajax({
      url: '/user/email/update/',
      type: 'POST',
      data: {
        'email': $('#update-email-form input:eq(1)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')
      }
    }).done(function(data) {
			// Failed to update email
      if (data.state == 'fail') {
        switch (data.code) {
          case 1:
            $('#update-email-form .alert-danger').text('변경할 메일 주소를 입력해주세요').removeClass('hidden');
            $('#update-email-form .input-group:eq(0)').addClass('has-error');
            break;
          case 2:
            $('#update-email-form .alert-danger').text('OAuth 로 가입한 사용자는 메일 주소를 변경할 수 없습니다').removeClass('hidden');
            break;
          case 3:
            $('#update-email-form .alert-danger').text('이미 존재하는 메일 주소입니다').removeClass('hidden');
            $('#update-email-form .input-group:eq(0)').addClass('has-error');
            break;
          default:
            $('#update-email-form .alert-danger').text('메일 주소 변경에 실패했습니다').removeClass('hidden');
            break;
        }
      }
      // Succeed to update email
      else {
        $('#update-email-form .alert-success').text('메일 주소를 변경했습니다').removeClass('hidden');
				
				$('#email-verification-message').addClass('hidden');
				$('#verify-email-form').removeClass('hidden');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
      $('#update-email-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });

  // Verify email
  $(document).on('submit', '#verify-email-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#verify-email-btn').button('loading');
    
    setCSRFToken();
    
    $.ajax({
      url: '/user/email/verification/',
      type: 'POST'
    }).done(function(data) {
			$('#verify-email-form .alert-success').text('인증 메일을 전송했습니다').removeClass('hidden');
			$('#verify-email-form .alert-warning').addClass('hidden');
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
      $('#verify-email-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });
});
