$(document).ready(function() {

  // Prevent CSRF token problem before sending reqeust with ajax
  function setCSRFToken() {
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': $.cookie('csrftoken')
      }
    });
  }

  // Update password
  $(document).on('submit', '#update-password-form', function(event) {
    event.preventDefault();
    
		// Show loading icon
    $('#loading-icon').show();
		
    // Prevent from double click
    $('#update-password-btn').button('loading');
    
    // Initialize alert message
    $('#update-password-form .alert-success, #update-password-form .alert-danger').text('').addClass('hidden');
    $('#update-password-form .input-group').removeClass('has-error');
    
    setCSRFToken();
    
    $.ajax({
      url: '/user/password/update/',
      type: 'POST',
      data: {
        'originalPassword': $('#update-password-form input:eq(1)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ''),
        'newPassword': $('#update-password-form input:eq(2)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')
      }
    }).done(function(data) {
			// Failed to update password
      if (data.state == 'fail') {
        switch (data.code) {
          case 1:
            $('#update-password-form .alert-danger').text('비밀번호를 입력해주세요').removeClass('hidden');
            break;
          case 2:
            $('#update-password-form .alert-danger').text('OAuth 로 가입한 사용자는 메일 주소를 변경할 수 없습니다').removeClass('hidden');
            break;
          case 3:
            $('#update-password-form .alert-danger').text('비밀번호가 불일치합니다').removeClass('hidden');
            $('#update-password-form .input-group:eq(0)').addClass('has-error');
            break;
          default:
            $('#update-password-form .alert-danger').text('비밀번호 변경에 실패했습니다').removeClass('hidden');
            break;
        }
      }
      // Succeed to update password
      else {
        $('#update-password-form .alert-success').text('비밀번호를 변경했습니다').removeClass('hidden');
        $('#update-password-form input:eq(1), #update-password-form input:eq(2)').val('');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
      $('#update-password-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });
});
