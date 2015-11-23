$(document).ready(function() {

  // Prevent CSRF token problem before sending reqeust with ajax
  function setCSRFToken() {
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': $.cookie('csrftoken')
      }
    });
  }

  // Deactivate account
  $(document).on('submit', '#deactivate-account-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#deactivate-account-form button').button('loading');
    
    setCSRFToken();
    
    $.ajax({
			url: '/user/deactivate/',
      type: 'POST',
      data: {
        'userID': $('#deactivate-account-form').find('input[name="user-id"]').val()
      }
    }).done(function(data) {
      // Succeed to deactivate account
      if (data.state == 'success') {
        $('#deactivate-account-form').find('input[name="user-id"]').val('');
				alert('성공적으로 휴면처리했습니다.');
      }
      // Failed to deactivate account
      else {
				alert('휴면처리에 실패했습니다');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
			$('#deactivate-account-form button').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });

  // Close story (Update state as closed)
  $(document).on('submit', '#close-story-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#close-story-form button').button('loading');
    
    setCSRFToken();
		
		var storyID = $('#close-story-form').find('input[name="story-id"]').val();
    
    $.ajax({
			url: '/story/' + storyID + '/close/',
      type: 'POST'
    }).done(function(data) {
      // Succeed to close story
      if (data.state == 'success') {
				$('#close-story-form').find('input[name="story-id"]').val('');
				alert('성공적으로 완결 처리했습니다.');
      }
      // Failed to close story
      else {
				alert('완결 처리에 실패했습니다');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
			$('#close-story-form button').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });

  // Delete story (Update state as deleted)
  $(document).on('submit', '#delete-story-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#delete-story-form button').button('loading');
    
    setCSRFToken();
		
		var storyID = $('#delete-story-form input[name="story-id"]').val();
    
    $.ajax({
			url: '/story/' + storyID + '/delete/',
      type: 'POST'
    }).done(function(data) {
      // Succeed to delete story
      if (data.state == 'success') {
				$('#delete-story-form input[name="story-id"]').val('');
				alert('성공적으로 삭제했습니다.');
      }
      // Failed to delete story
      else {
				alert('삭제에 실패했습니다');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
			$('#delete-story-form button').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });

  // Delete comment (Update state as deleted)
  $(document).on('submit', '#delete-comment-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#delete-comment-form button').button('loading');
    
    setCSRFToken();
		
		var commentID = $('#delete-comment-form').find('input[name="comment-id"]').val();
    
    $.ajax({
			url: '/comment/' + commentID + '/delete/',
      type: 'POST'
    }).done(function(data) {
      // Succeed to delete comment
      if (data.state == 'success') {
				$('#delete-comment-form').find('input[name="comment-id"]').val('');
				alert('성공적으로 삭제했습니다.');
      }
      // Failed to delete comment
      else {
				alert('삭제에 실패했습니다');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
			$('#delete-comment-form button').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });

  // Delete reply (Update state as deleted)
  $(document).on('submit', '#delete-reply-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#delete-reply-form button').button('loading');
    
    setCSRFToken();
		
		var replyID = $('#delete-reply-form').find('input[name="reply-id"]').val();
    
    $.ajax({
			url: '/reply/' + replyID + '/delete/',
      type: 'POST'
    }).done(function(data) {
      // Succeed to delete reply
      if (data.state == 'success') {
				$('#delete-reply-form').find('input[name="reply-id"]').val('');
				alert('성공적으로 삭제했습니다.');
      }
      // Failed to delete reply
      else {
				alert('삭제에 실패했습니다');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
			$('#delete-reply-form button').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });

  // Give reward point to user
  $(document).on('submit', '#give-reward-point-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#give-reward-point-form button').button('loading');
    
    setCSRFToken();
		
    $.ajax({
			url: '/user/reward/',
      type: 'POST',
			data: {
				'userID': $('#give-reward-point-form').find('input[name="user-id"]').val() 
			}
    }).done(function(data) {
      // Succeed to delete reply
      if (data.state == 'success') {
				$('#give-reward-point-form').find('input[name="user-id"]').val('');
				alert('성공적으로 필력을 보상했습니다.');
      }
      // Failed to delete reply
      else {
				alert('필력 보상에 실패했습니다');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
			$('#give-reward-point-form button').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });

  // Update story cache
  $(document).on('submit', '#update-story-cache-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#update-story-cache-form button').button('loading');
    
    setCSRFToken();
		
		var storyID = $('#update-story-cache-form').find('input[name="story-id"]').val();
		
    $.ajax({
			url: '/story/' + storyID + '/cache/update/',
      type: 'POST'
    }).done(function(data) {
      // Succeed to update story cache
      if (data.state == 'success') {
				$('#update-story-cache-form').find('input[name="story-id"]').val('');
				alert('성공적으로 캐쉬를 업데이트했습니다.');
      }
      // Failed to update story cache
      else {
				alert('캐쉬 업데이트에 실패했습니다');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
			$('#update-story-cache-form button').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });

  // Update comment cache
  $(document).on('submit', '#update-comment-cache-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#update-comment-cache-form button').button('loading');
    
    setCSRFToken();
		
		var commentID = $('#update-comment-cache-form').find('input[name="comment-id"]').val();
		
    $.ajax({
			url: '/comment/' + commentID + '/cache/update/',
      type: 'POST'
    }).done(function(data) {
      // Succeed to update comment cache
      if (data.state == 'success') {
				$('#update-comment-cache-form').find('input[name="comment-id"]').val('');
				alert('성공적으로 캐쉬를 업데이트했습니다.');
      }
      // Failed to update comment cache
      else {
				alert('캐쉬 업데이트에 실패했습니다');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
			$('#update-comment-cache-form button').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });

  // Update reply cache
  $(document).on('submit', '#update-reply-cache-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
    
    // Prevent from double click
    $('#update-reply-cache-form button').button('loading');
    
    setCSRFToken();
		
		var replyID = $('#update-reply-cache-form').find('input[name="reply-id"]').val();
		
    $.ajax({
			url: '/reply/' + replyID + '/cache/update/',
      type: 'POST'
    }).done(function(data) {
      // Succeed to update reply cache
      if (data.state == 'success') {
				$('#update-reply-cache-form').find('input[name="reply-id"]').val('');
				alert('성공적으로 캐쉬를 업데이트했습니다.');
      }
      // Failed to update reply cache
      else {
				alert('캐쉬 업데이트에 실패했습니다');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
			$('#update-reply-cache-form button').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });
});
