var pagination = 1;

// Change Moment JS locale globally
moment.locale('ko');
/* TODO globalization
moment.locale('ja');
moment.locale('en');
moment.locale('zh-cn');
*/

// Append comments to list
function appendCommentsToList(dataList) {
	
	dataList.forEach(function(data) {
		var commentDOMElement = $('#comment-dom-element').clone().removeClass('hidden').removeAttr('id');
		
		commentDOMElement.attr('data-comment-id', data.id);
		commentDOMElement.find('a').attr('href', '/story/' + data.story_id + '/#' + data.order);
		commentDOMElement.find('.story-title').text(data.story_title);
		commentDOMElement.find('.created-at').val(data.created_at);
		commentDOMElement.find('.time-past-text').text(moment(new Date(data.created_at)).fromNow());
		commentDOMElement.find('.comment-context').text(data.context);
		
		if (data.has_image) {
			img = commentDOMElement.find('img');
			
			// Use lazy loading for image
			img.attr('data-original', data.image_url).lazyload({
				effect: 'fadeIn',
				event: 'inview',
			});
			
			// Show image reference
			if (data.image_reference != null && data.image_reference != '') {
				commentDOMElement.find('.image-reference').attr('href', data.image_reference).removeClass('hidden');
			}
			
			// Set position of image
			if (data.image_position == false) {
				commentDOMElement.find('.image-container').before(commentDOMElement.find('.comment-context'));
			}
		} else {
			commentDOMElement.find('.image-container').addClass('hidden');
		}
		
		commentDOMElement.find('.like-count').text(data.like_count);
		commentDOMElement.find('.dislike-count').text(data.dislike_count);
		
		if (data.state == 'deleted') {
			commentDOMElement.find('.alert-danger').removeClass('hidden');
		}
		
		$('#user-wrote-comment-list').append(commentDOMElement);
	});
}

// Get comments
function getComments(num) {
	// Show loading icon
	$('#loading-icon').show();

	var data = {};

  if (num > 1) data['lastCommentID'] = $('#user-wrote-comment-list .comment').last().attr('data-comment-id');

	$.ajax({
		url: '/user/comments/' + num + '/',
		type: 'GET',
		data: data
	}).done(function(data) {
		if (data.state == 'success') {
			switch (data.code) {
				case 1:
					$('#pagination').val(num);
					appendCommentsToList(data.comments);
					break;
				case 2:
					$('#pagination').val(num);
					$('#no-more-comment').val('true');
					appendCommentsToList(data.comments);
					break;
				default:
					$('#pagination').val(num);
					appendCommentsToList(data.comments);
					break;
			}
		}
		// Failed to get more comments
		else {
			pagination = parseInt($('#pagination').val());
		}
	}).fail(function() {
		pagination = parseInt($('#pagination').val());
		alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
	}).always(function() {
		// Hide loading icon
		$('#loading-icon').hide();
		
		// Show no comment message with icon if there is no comment at all
		if ($('#user-wrote-comment-list .comment').length == 0) {
			$('#no-comment-at-all').removeClass('hidden');
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
		
		// Get more comments
		if ($(window).scrollTop() > $(document).height() - $(window).height() - 100) {
			// Prevent from multiple request for same pagination
			if (parseInt($('#pagination').val()) == pagination && $('#no-more-comment').val() == 'false') {
				pagination += 1;
				
				getComments(pagination);
			}
		}
	}); 
});

$(window).load(function() {

	// Get first page
	getComments(pagination);

	// Update time past text every minute
  setInterval(function() {
    $('.created-at').each(function() {
      $(this).parent().find('.time-past-text').text(moment(new Date($(this).val())).fromNow());
    });
	}, moment.duration(1, 'minutes'));
});
