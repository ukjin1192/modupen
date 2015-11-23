$(document).ready(function() {

  // Prevent CSRF token problem before sending reqeust with ajax
  function setCSRFToken() {
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': $.cookie('csrftoken')
      }
    });
  }

  // Auto sizing textarea height
  $(document).on('keyup', '#context', function() {
    while ($(this).outerHeight() < this.scrollHeight +
      parseFloat($(this).css('borderTopWidth')) +
      parseFloat($(this).css('borderBottomWidth'))) {
      $(this).height($(this).height()+1);
    };
  });

  // Submit voice of customer
  $(document).on('submit', '#voc-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#submit-voc-btn').button('loading');
		
    // Initialize alert message
    $('#voc-form .alert-success, #voc-form .alert-danger').text('').addClass('hidden');
    $('#voc-form .input-group').removeClass('has-error');
		
		var data = {};
		
		if ($('#voc-form input[name="email"]').val()) {
			data['email'] = $('#voc-form input[name="email"]').val();
		}
		data['feeling'] = $('#voc-form select:eq(0)').val();
    data['context'] = $('#voc-form textarea:eq(0)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '');
    
    setCSRFToken();
    
    $.ajax({
			url: '/voc/create/',
      type: 'POST',
      data: data
    }).done(function(data) {
      // Succeed to submit voc
      if (data.state == 'success') {
        $('#voc-form .alert-success').text('성공적으로 건의했습니다').removeClass('hidden');
        $('#voc-form .alert-danger').addClass('hidden');
      }
      // Failed to submit voc
      else {
        $('#voc-form .alert-danger').text('건의하는데 실패했습니다').removeClass('hidden');
        $('#voc-form .alert-success').addClass('hidden');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
      $('#submit-voc-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });
});
