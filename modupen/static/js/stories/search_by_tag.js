var pagination = 1;

// Append stories to list
function appendStoriesToList(dataList) {
	
	dataList.forEach(function(data) {
		var storyDOMElement = $('#story-dom-element').clone().removeClass('hidden').removeAttr('id');
		
		storyDOMElement.attr('data-story-id', data.id);
		storyDOMElement.find('a').attr('href', '/story/' + data.id + '/');
		
		if (data.has_image) {
			imageURL = data.image_url;
			imageURL = imageURL.replace('/upload/', '/upload/w_360,h_120,c_thumb/');
			
			// Use lazy loading for image
			storyDOMElement.find('img').attr('data-original', imageURL).lazyload({
				effect: 'fadeIn',
				event: 'inview',
			});
		} else {
      // Update background color of fake block randomly
      storyDOMElement.find('.fake-block').css(
        'background-color',
        '#' + Math.floor(Math.random() * 16777215).toString(16)
      );
    }
		
		storyDOMElement.find('.caption-title').text(data.title);
		
		if (data.contributors_count > 1) {
			storyDOMElement.find('.caption-contributors').text(data.author_nickname + '님 외 ' + 
				parseInt(data.contributors_count - 1) + '명이 함께 만듭니다');
		} else {
			storyDOMElement.find('.caption-contributors').text(data.author_nickname + '님이 시작하셨습니다');
		}
		
		storyTags = data.tags;                              
		if (storyTags == null || storyTags.length == 0) {
      storyDOMElement.find('.caption-tags').addClass('hidden');
    } else {
			storyTags.forEach(function(tag) {                   
				storyDOMElement.find('.caption-tags').append('#' + tag + ' ');
			});
		}
		
		storyDOMElement.find('.hits').text(data.hits);
		storyDOMElement.find('.comments-count').text(data.comments_count);
		storyDOMElement.find('.favorites-count').text(data.favorites_count);
		
		$('#story-list').append(storyDOMElement);
	});
}

// Hide fake block and show image if image is loaded
function showImage(imageObj) {
	if (imageObj.width() > 1) {
		imageObj.parent().removeClass('fake-block');
		imageObj.addClass('full-width');
	}
}

// Get stories
function getStories(num) {
	// Show loading icon
	$('#loading-icon').show();

	var data = {};

  if (num > 1) data['lastStoryID'] = $('#story-list .story').last().attr('data-story-id');

	$.ajax({
		url: window.location.pathname + num + '/',
		type: 'GET',
		data: data
	}).done(function(data) {
		if (data.state == 'success') {
			switch (data.code) {
				case 1:
					$('#pagination').val(num);
					appendStoriesToList(data.stories);
					break;
				case 2:
					$('#pagination').val(num);
					$('#no-more-story').val('true');
					appendStoriesToList(data.stories);
					break;
				default:
					$('#pagination').val(num);
					appendStoriesToList(data.stories);
					break;
			}
		}
		// Failed to get more stories
		else {
			pagination = parseInt($('#pagination').val());
		}
	}).fail(function() {
		pagination = parseInt($('#pagination').val());
		alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
	}).always(function() {
		// Hide loading icon
		$('#loading-icon').hide();
		
		// Show no story message with icon if there is no story at all
		if ($('#story-list .story').length == 0) {
			$('#no-story-at-all').removeClass('hidden');
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
		
		// Get more stories
		if ($(window).scrollTop() > $(document).height() - $(window).height() - 100) {
			// Prevent from multiple request for same pagination
			if (parseInt($('#pagination').val()) == pagination && $('#no-more-story').val() == 'false') {
				pagination += 1;
				
				getStories(pagination);
			}
		}
	}); 
});

$(window).load(function() {

	// Get first page
	getStories(pagination);
});
