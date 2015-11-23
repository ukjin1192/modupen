$(document).ready(function() {

  // Prevent CSRF token problem before sending reqeust with ajax
  function setCSRFToken() {
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': $.cookie('csrftoken')
      }
    });
  }

  // Send email to issue temporary password
  $(document).on('submit', '#send-email-form', function(event) {
    event.preventDefault();
			
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#send-email-btn').button('loading');
    
    // Initialize alert message
    $('#send-email-form .alert-success, #send-email-form .alert-danger').text('').addClass('hidden');
    $('#send-email-form .input-group').removeClass('has-error');
    
    setCSRFToken();
    
    $.ajax({
      url: '/user/password/forgot/send/',
      type: 'POST',
      data: {
        'email': $('#send-email-form input:eq(1)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')
      }
    }).done(function(data) {
			// Failed to send email
      if (data.state == 'fail') {
        switch (data.code) {
          case 1:
            $('#send-email-form .alert-danger').text('메일 주소를 입력해주세요').removeClass('hidden');
            break;
          case 2:
            $('#send-email-form .alert-danger').text('등록되지 않은 메일 주소입니다').removeClass('hidden');
            $('#send-email-form .input-group:eq(0)').addClass('has-error');
            break;
          case 3:
            $('#send-email-form .alert-danger').html('휴면처리된 계정입니다. 아래로 문의해주세요.<br/>'
							+ 'modupen@budafoo.com').removeClass('hidden');
            break;
          default:
            $('#send-email-form .alert-danger').text('임시 비밀번호 발급에 실패했습니다').removeClass('hidden');
            break;
        }
      }
      // Succeed to send email
      else {
        $('#send-email-form .input-group:eq(0), #send-email-btn').addClass('hidden');
        $('#email-address').text($('#send-email-form input:eq(1)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ''));
        $('#send-email-form .alert-success').removeClass('hidden');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
      $('#send-email-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });
});
