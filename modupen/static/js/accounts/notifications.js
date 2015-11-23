var pagination = 1;
var notificationPreviewMaxLength = parseInt($('#notification-preview-max-length').val());

// Change Moment JS locale globally
moment.locale('ko');
/* TODO globalization
moment.locale('ja');
moment.locale('en');
moment.locale('zh-cn');
*/

// Append notifications to list
function appendNotificationsToList(dataList) {

	dataList.forEach(function(data) {
		var notificationDOMElement = $('#notification-dom-element').clone().removeClass('hidden').removeAttr('id');
		
		notificationDOMElement.attr('data-notification-id', data[0]);
		notificationDOMElement.find('a').attr('href', data[4]);
		
		story_title = data[6];
		
		comment_context = data[7];
		if (comment_context != null && comment_context.length > notificationPreviewMaxLength) {
			comment_context = comment_context.slice(0, notificationPreviewMaxLength) + '...';
		}
		
		reply_context = data[8];
		if (reply_context != null && reply_context.length > notificationPreviewMaxLength) {
			reply_cotext = reply_context.slice(0, notificationPreviewMaxLength) + '...';
		}
		
		created_at = data[9];
		notificationDOMElement.find('.created-at').val(created_at);
		
		switch(data[5]) {
			case 'new_comment':
				notificationDOMElement.find('.notification-message').html(
					'내가 참여한 이야기에 <span class="label label-primary">새 댓글</span>이 달렸습니다');
				notificationDOMElement.find('.notification-preview').html(
					'[시간] <span class="time-past-text">' + moment(new Date(created_at)).fromNow() + '</span><br/>' +
					'[이야기] ' + story_title + '<br/>' +
					'[댓글] ' + comment_context);
				break;
			case 'new_reply':
				notificationDOMElement.find('.notification-message').html(
					'내가 참여한 댓글에 <span class="label label-success">새 대댓글</span>이 달렸습니다');
				notificationDOMElement.find('.notification-preview').html(
					'[시간] <span class="time-past-text">' + moment(new Date(created_at)).fromNow() + '</span><br/>' +
					'[이야기] ' + story_title + '<br/>' +
					'[댓글] ' + comment_context + '<br/>' + 
					'[대댓글] ' + reply_context);
				break;
			case 'get_like':
				notificationDOMElement.find('.notification-message').html(
					'내가 작성한 댓글이 <span class="label label-info">추천</span> 받았습니다');
				notificationDOMElement.find('.notification-preview').html(
					'[시간] <span class="time-past-text">' + moment(new Date(created_at)).fromNow() + '</span><br/>' +
					'[이야기] ' + story_title + '<br/>' +
					'[댓글] ' + comment_context);
				break;
			case 'get_dislike':
				notificationDOMElement.find('.notification-message').html(
					'내가 작성한 댓글이 <span class="label label-warning">비추천</span> 받았습니다');
				notificationDOMElement.find('.notification-preview').html(
					'[시간] <span class="time-past-text">' + moment(new Date(created_at)).fromNow() + '</span><br/>' +
					'[이야기] ' + story_title + '<br/>' +
					'[댓글] ' + comment_context);
				break;
			case 'reported':
				if (data[2] == 'comments') {
					notificationDOMElement.find('.notification-message').html(
						'내가 작성한 댓글이 <span class="label label-danger">신고</span> 받았습니다');
					notificationDOMElement.find('.notification-preview').html(
						'[시간] <span class="time-past-text">' + moment(new Date(created_at)).fromNow() + '</span><br/>' +
						'[이야기] ' + story_title + '<br/>' +
						'[댓글] ' + comment_context);
					break;
				} else {
					notificationDOMElement.find('.notification-message').html(
						'내가 작성한 대댓글이 <span class="label label-danger">신고</span> 받았습니다');
					notificationDOMElement.find('.notification-preview').html(
						'[시간] <span class="time-past-text">' + moment(new Date(created_at)).fromNow() + '</span><br/>' +
						'[이야기] ' + story_title + '<br/>' +
						'[댓글] ' + comment_context + '<br/>' + 
						'[대댓글] ' + reply_context);
					break;
				}
			case 'closed':
				notificationDOMElement.find('.notification-message').html(
					'내가 참여한 이야기가 <span class="label label-default">완결</span> 됐습니다');
				notificationDOMElement.find('.notification-preview').html(
					'[시간] <span class="time-past-text">' + moment(new Date(created_at)).fromNow() + '</span><br/>' +
					'[이야기] ' + story_title);
				break;
			case 'closing_vote_opened':
				notificationDOMElement.find('.notification-message').html(
					'내가 참여한 이야기의 <span class="label label-default">완결 투표</span>가 열렸습니다');
				notificationDOMElement.find('.notification-preview').html(
					'[시간] <span class="time-past-text">' + moment(new Date(created_at)).fromNow() + '</span><br/>' +
					'[이야기] ' + story_title);
				break;
		}
		
		$('#notification-list').append(notificationDOMElement);
	});
}

// Get notifications with options
function getNotifications(num) {
	// Show loading icon
	$('#loading-icon').show();

	var data = {};

  if (num > 1) data['lastNotificationID'] = $('#notification-list .notification').last().attr('data-notification-id');

	$.ajax({
		url: '/notifications/' + num + '/',
		type: 'GET',
		data: data
	}).done(function(data) {
		if (data.state == 'success') {
			switch (data.code) {
				case 1:
					$('#pagination').val(num);
					appendNotificationsToList(data.notifications);
					break;
				case 2:
					$('#pagination').val(num);
					$('#no-more-notification').val('true');
					appendNotificationsToList(data.notifications);
					break;
				default:
					$('#pagination').val(num);
					appendNotificationsToList(data.notifications);
					break;
			}
		}
		// Failed to get more notifications
		else {
			pagination = parseInt($('#pagination').val());
		}
	}).fail(function() {
		pagination = parseInt($('#pagination').val());
		alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
	}).always(function() {
		// Hide loading icon
		$('#loading-icon').hide();
		
		// Show no notification message with icon if there is no notification at all
		if ($('#notification-list .notification').length == 0) {
			$('#no-notification-at-all').removeClass('hidden');
		}
	});
}
	
$(document).ready(function() {

	// Prevent CSRF token problem before sending reqeust with ajax
  function setCSRFToken() {
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': $.cookie('csrftoken')
      }
    });
  }

	$(window).on('scroll', function() {
		// Show 'back to top' if scroll bar appears
		if ($(window).scrollTop() == 0) {
			$('#back-to-top').addClass('hidden');
		} else { 
			$('#back-to-top').removeClass('hidden');
		}
		
		// Get more notifications
		if ($(window).scrollTop() > $(document).height() - $(window).height() - 100) {
			// Prevent from multiple request for same pagination
			if (parseInt($('#pagination').val()) == pagination && $('#no-more-notification').val() == 'false') {
				pagination += 1;
				
				getNotifications(pagination);
			}
		}
	}); 

	$(document).on('change', '#toggle-notification-setting', function() {
		
		setCSRFToken();
		
		$.ajax({
			url: '/user/notification/update/',
			type: 'POST',
			data: {
				'setting': $('#toggle-notification-setting').prop('checked')
			}
		}).done(function() {
		}).fail(function() {
		}).always(function() {
		});
	});
});

$(window).load(function() {

	// Prevent from blinking
	$('#toggle-notification-setting').removeClass('hidden');

	// Get first page
	getNotifications(pagination);

	// Update time past text every minute
  setInterval(function() {
    $('.created-at').each(function() {
      $(this).parent().find('.time-past-text').text(moment(new Date($(this).val())).fromNow());
    });
  }, moment.duration(1, 'minutes'));
});
