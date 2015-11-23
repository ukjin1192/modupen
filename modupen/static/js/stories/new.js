var titleMaxLength = parseInt($('#title-max-length').val());
var commentMaxLength = parseInt($('#comment-max-length').val());
var maxImageSize= parseInt($('#max-image-size').val());
var timeIntervalForNewStory = parseInt($('#time-interval-for-new-story').val());
var maxTagsPerStory = parseInt($('#max-tags-per-story').val());
var tagMaxLength = parseInt($('#tag-max-length').val());

$(document).ready(function() {

	// File input options
	$('#image').fileinput({
		allowedFileTypes: ['image', ],
		autoReplace: true,
		browseClass: 'btn btn-default',
		captionClass: 'caption-text',
		initialCaption: '선택 사항입니다',
		language: 'ko',
		maxFileCount: 1,
		maxFileSize: maxImageSize,
		removeLabel: '',
		showUpload: false
	});

	// Prevent from blinking side effect
	$('#image').removeClass('hidden');
	
	// Prevent CSRF token problem before sending reqeust with ajax
	function setCSRFToken() {
		$.ajaxSetup({
			headers: {
				'X-CSRFToken': $.cookie('csrftoken')
			}
		}); 
	}
	
	// Count characters for title input
	$(document).on('keyup', '#title', function() {
		// Count line break as 2 characters
		length = $(this).val().replace(/(\r\n|\n|\r)/g, '--').length;
		$('#title-character-count').text(length);
	});

	// Count characters for context input and auto sizing textarea height
	$(document).on('keyup', '#context', function() {
		// Count line break as 2 characters
		length = $(this).val().replace(/(\r\n|\n|\r)/g, '--').length;
		$('#context-character-count').text(length);
		
		// Auto sizing textarea height
		while ($(this).outerHeight() < this.scrollHeight +
			parseFloat($(this).css('borderTopWidth')) +
			parseFloat($(this).css('borderBottomWidth'))) {
			$(this).height($(this).height()+1);
		};
	});

	// Show input for image reference if image uploaded
	$(document).on('fileloaded', '#image', function() {
		$('#image-sub-info').removeClass('hidden');
	});

	// Hide input for image reference if image cleared
	$(document).on('fileclear', '#image', function() {
		$('#image-sub-info').addClass('hidden');
	});

	// Adjust format of tags
	function adjustTags() {
		if ($('#tags').val() != '') {
			var tagList = []; 
			var tags = $('#tags').val().split(',');
			
			tags.forEach(function(tag) {
				tag = tag.replace(/ /g,'').toLowerCase();
				if (tag.length > 0) tagList.push(tag.slice(0, tagMaxLength));
			});
			
			$('#tags').val(tagList.join(', '));
		}
	}

	$(document).on('blur', '#tags', function() {
		adjustTags();
	});
	
	// Validate story creation form 
	$(document).on('submit', '#create-story-form', function(event) {
		event.preventDefault();
		
		adjustTags();
		
		// Initialize alert message
		$('#create-story-form').find('.input-group, .form-group').removeClass('has-error');
		$('#create-story-form .alert-danger').text('').addClass('hidden');
		
		// Check tags are valid
		if ($('#tags').val() != '') {
			tags = $('#tags').val().split(',');
			
			if (tags.length > maxTagsPerStory) {
				$('#create-story-form .alert-danger').text('태그는 최대 ' + maxTagsPerStory + 
					'개까지 입력 가능합니다').removeClass('hidden');
				$('#tags').closest('.input-group').addClass('has-error');
				
				return false;
			}
			
			var tagMaxLengthException = false;
			tags.forEach(function(tag) {
				if (tag.trim().length > tagMaxLength || tag.trim().length == 0) {
					$('#create-story-form .alert-danger').text('각각의 태그는 최소 1글자, 최대 ' + tagMaxLength + '글자까지 가능합니다').removeClass('hidden');
					$('#tags').closest('.input-group').addClass('has-error');
					
					tagMaxLengthException = true;
					
					return false;
				}
			});
		
			if (tagMaxLengthException == true) return false;
		}
		
		// Show loading icon
		$('#loading-icon').show();
		
		// Prevent from double click
		$('#story-submit-btn').button('loading');
		
		var formData = new FormData();
		
		formData.append('title', $('#title').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ''));
		formData.append('tags', $('#tags').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ''));
		formData.append('context', $('#context').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ''));
		
		if ($('#image')[0].files[0] != null && $('.file-input').hasClass('has-error') == false) {
			formData.append('image', $('#image')[0].files[0]);
			formData.append('imageReference', $('#image-reference').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ''));
			formData.append('imagePosition', $('input[name="image-position"]:checked').val());
		}
		
		setCSRFToken();
		
		$.ajax({
			url: '/story/create/',
			type: 'POST',
			data: formData,
			contentType: false,
			processData: false
		}).done(function(data) {
			// Failed to create story
			if (data.state == 'fail') {
				switch (data.code) {
					case 1:
						$('#create-story-form .alert-danger').text('입력칸을 모두 채워주세요').removeClass('hidden');
						break;
					// Show signup modal if user not logged in
					case 2:
						$('#signup-tab').tab('show');
						$('#signup-form-container').addClass('in active');
						$('#login-form-container').removeClass('in active');
						$('#modal-signup').modal('show');
						break;
					case 3:
						$('#create-story-form .alert-danger').text('새 이야기를 쓰기 위해서는 최소 ' +
								timeIntervalForNewStory + '분의 간격이 필요합니다').removeClass('hidden');
						break;
					default:
						$('#create-story-form .alert-danger').text('새 이야기를 쓰는데 실패했습니다').removeClass('hidden');
						break;
				}
			}
			// Succeed to create story and move to the story detail page
			else {
				// Clear temporarily saved title, tags and context
				clearInterval(temporarySave);
				localStorage.removeItem('title');
				localStorage.removeItem('tags');
				localStorage.removeItem('context');
				
				location.href = '/story/' + data.storyID + '/';
			}
		}).fail(function() {
			alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
		}).always(function() {
			// Recover button clickable
			$('#story-submit-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
		});
	});

	// Save title, tags and context temporarily every 5 seconds
	var temporarySave = setInterval(function() {
		localStorage.setItem('title', $('#title').val());
		localStorage.setItem('tags', $('#tags').val());
		localStorage.setItem('context', $('#context').val());
	}, 5000);
});

$(window).load(function() {
	// Auto filling title, tags and context input
	$('#title').val(localStorage.getItem('title'));
	$('#title-character-count').text($('#title').val().length);
	$('#tags').val(localStorage.getItem('tags'));
	$('#context').val(localStorage.getItem('context'));
	$('#context-character-count').text($('#context').val().length);
});
