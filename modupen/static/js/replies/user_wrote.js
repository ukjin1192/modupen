var pagination = 1;

// Change Moment JS locale globally
moment.locale('ko');
/* TODO globalization
moment.locale('ja');
moment.locale('en');
moment.locale('zh-cn');
*/

// Append replies to list
function appendRepliesToList(dataList) {
	
	dataList.forEach(function(data) {
		var replyDOMElement = $('#reply-dom-element').clone().removeClass('hidden').removeAttr('id');
		
		replyDOMElement.attr('data-reply-id', data.id);
		replyDOMElement.find('a').attr('href', '/story/' + data.story_id + '/#' + data.comment_order);
		replyDOMElement.find('.story-title').text(data.story_title);
		replyDOMElement.find('.created-at').val(data.created_at);
		replyDOMElement.find('.time-past-text').text(moment(new Date(data.created_at)).fromNow());
		replyDOMElement.find('.reply-context').text(data.context);
		
		if (data.state == 'deleted') {
			replyDOMElement.find('.alert-danger').removeClass('hidden');
		}
		
		$('#user-wrote-reply-list').append(replyDOMElement);
	});
}

// Get replies
function getReplies(num) {
	// Show loading icon
	$('#loading-icon').show();

	var data = {};

  if (num > 1) data['lastReplyID'] = $('#user-wrote-reply-list .reply').last().attr('data-reply-id');

	$.ajax({
		url: '/user/replies/' + num + '/',
		type: 'GET',
		data: data
	}).done(function(data) {
		if (data.state == 'success') {
			switch (data.code) {
				case 1:
					$('#pagination').val(num);
					appendRepliesToList(data.replies);
					break;
				case 2:
					$('#pagination').val(num);
					$('#no-more-reply').val('true');
					appendRepliesToList(data.replies);
					break;
				default:
					$('#pagination').val(num);
					appendRepliesToList(data.replies);
					break;
			}
		}
		// Failed to get more replies
		else {
			pagination = parseInt($('#pagination').val());
		}
	}).fail(function() {
		pagination = parseInt($('#pagination').val());
		alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
	}).always(function() {
		// Hide loading icon
		$('#loading-icon').hide();
		
		// Show no reply message with icon if there is no reply at all
		if ($('#user-wrote-reply-list .reply').length == 0) {
			$('#no-reply-at-all').removeClass('hidden');
		}
	});
}
	
$(document).ready(function() {

	$(window).on('scroll', function() {
		// Show 'back to top' if scroll bar appears
		if ($(window).scrollTop() == 0) {
			$('#back-to-top').addClass('hidden');
		} else { 
			$('#back-to-top').removeClass('hidden');
		}
		
		// Get more replies
		if ($(window).scrollTop() > $(document).height() - $(window).height() - 100) {
			// Prevent from multiple request for same pagination
			if (parseInt($('#pagination').val()) == pagination && $('#no-more-reply').val() == 'false') {
				pagination += 1;
				
				getReplies(pagination);
			}
		}
	}); 
});

$(window).load(function() {

	// Get first page
	getReplies(pagination);

	// Update time past text every minute
  setInterval(function() {
    $('.created-at').each(function() {
      $(this).parent().find('.time-past-text').text(moment(new Date($(this).val())).fromNow());
    });
	}, moment.duration(1, 'minutes'));
});
