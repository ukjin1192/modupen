$(document).ready(function() {

  // Prevent CSRF token problem before sending reqeust with ajax
  function setCSRFToken() {
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': $.cookie('csrftoken')
      }
    });
  }

  // Update language
  $(document).on('submit', '#update-language-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#update-language-btn').button('loading');
    
    // Initialize alert message
    $('#update-language-form .alert-success, #update-language-form .alert-danger').text('').addClass('hidden');
    
    setCSRFToken();
    
    $.ajax({
      url: '/user/language/update/',
      type: 'POST',
      data: {
        'language': $('#update-language-form select').val()
      }
    }).done(function(data) {
      // Failed to update language
			if (data.state == 'fail') {
        switch (data.code) {
          case 1:
            $('#update-language-form .alert-danger').text('사용할 언어를 선택해주세요').removeClass('hidden');
            break;
          case 2:
            $('#update-language-form .alert-danger').text('사용할 수 없는 언어입니다').removeClass('hidden');
            break;
          default:
            $('#update-language-form .alert-danger').text('사용 언어 변경에 실패했습니다').removeClass('hidden');
            break;
        }
      }
      // Succeed to update language
      else {
        $('#update-language-form .alert-success').text('사용 언어를 변경했습니다').removeClass('hidden');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
      $('#update-language-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });
});
