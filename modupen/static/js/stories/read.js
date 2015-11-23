var pagination = 1;
var storyIDList = [];
var storiesPerQuery = parseInt($('#stories-per-query').val());

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

	slicedStoryIDList = storyIDList.slice((pagination - 1) * storiesPerQuery, pagination * storiesPerQuery);

	if (slicedStoryIDList.length == 0) {
		$('#no-more-story').val('true');
		return ;
	}

	var data = {};

	data['storyIDList'] = slicedStoryIDList.join(',');

	$.ajax({
		url: '/stories/list/',
		type: 'GET',
		data: data
	}).done(function(data) {
		// Succeed to get stories
		if (data.state == 'success') {
			$('#pagination').val(num);
			
			if (slicedStoryIDList.length < storiesPerQuery) $('#no-more-story').val('true');
			
			appendStoriesToList(data.stories);
		} 
		// Failed to get stories
		else {
			pagination = parseInt($('#pagination').val());
		}
	}).fail(function() {
		pagination = parseInt($('#pagination').val());
		alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
	}).always(function() {
		// Hide loading icon
		$('#loading-icon').hide();
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

	// Toggle on/off edit mode
	$(document).on('click', '#toggle-edit-mode-btn', function() {
		// Toggle on edit mode
		if ($('#toggle-edit-mode-btn').attr('data-edit-mode') == 'false') {
			$('#toggle-edit-mode-btn').attr('data-edit-mode', 'true').text('완료');
			$('#remove-whole-story-btn').attr('data-confirm', 'false').text('전체 삭제');
			$('.remove-story-btn, #remove-whole-story-btn, #bottom-space').removeClass('hidden');
		}
		// Toggle off edit mode
		else {
			$('#toggle-edit-mode-btn').attr('data-edit-mode', 'false').text('편집');
			$('#remove-whole-story-btn').attr('data-confirm', 'false').text('전체 삭제');
			$('.remove-story-btn, #remove-whole-story-btn, #bottom-space').addClass('hidden');
		}
	});

	// Remove story from read story list
	$(document).on('click', '.remove-story-btn', function() {
		var removeStoryBtn = $(this);
		storyID = removeStoryBtn.parent().attr('data-story-id');
		regex = new RegExp('(?:,|^)(' + storyID + ':[0-9]+,)');
		
		// Edit local storage (Splice string)
		readStories = localStorage.getItem('read_stories') || '';
		matchedString = readStories.match(regex)[1];
		matchedStringLength = matchedString.length;
		startPosition = readStories.indexOf(matchedString);
		
		readStories = readStories.slice(0, startPosition) + 
			readStories.slice(startPosition + matchedStringLength);
		
		try {
			localStorage.setItem('read_stories', readStories);
		} catch(e) {
			void(0);
		}
		
		// Remove DOM element
		removeStoryBtn.parent().remove();
	});

	// Remove whole story from read story list
	$(document).on('click', '#remove-whole-story-btn', function() {
		var removeWholeStoryBtn = $(this);
		
		// Confirm once more  
    if (removeWholeStoryBtn.attr('data-confirm') == 'false') {
      removeWholeStoryBtn.attr('data-confirm', 'true').text('한번 더 클릭하면 전체 삭제합니다');
      return ;
    }
		
		// Edit local storage
		try {
			localStorage.setItem('read_stories', '');
		} catch(e) {
			void(0);
		}
		
		// Remove DOM element
		$('#story-list').html('');
		
		// Toggle off edit mode
		$('#toggle-edit-mode-btn').attr('data-edit-mode', 'false').text('편집');
		$('#remove-whole-story-btn').attr('data-confirm', 'false').text('전체 삭제');
		$('.remove-story-btn, #remove-whole-story-btn, #bottom-space').addClass('hidden');
	});
});

$(window).load(function() {

	// Get story ID list
	readStories = (localStorage.getItem('read_stories') || '').split(',');
	readStories.forEach(function(data) {
		storyID = data.split(':')[0];
		if (storyID != '') storyIDList.push(storyID);
	});

	// Get first page
	if (storyIDList.length > 0) {
		getStories(pagination);
	} else {
		$('#no-more-story').val('true');
		$('#no-story-at-all').removeClass('hidden');
	}
});
