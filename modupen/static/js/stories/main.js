var whileLoadComments = false;

var storyID = parseInt($('#story-id').val());
var storyTitle = $('#story-title').val();

var latestCommentOrder = parseInt($('#last-comment-order').val());
var latestReplyOrder = 0;

var maxImageSize= parseInt($('#max-image-size').val());
var commentMaxLength = parseInt($('#comment-max-length').val());
var replyMaxLength = parseInt($('#reply-max-length').val());

var commentsPerQuery = parseInt($('#comments-per-query').val());
var repliesPerQuery = parseInt($('#replies-per-query').val());

var timeIntervalForNewComment = parseInt($('#time-interval-for-new-comment').val());
var timeIntervalForNewReply = parseInt($('#time-interval-for-new-reply').val());
var timeIntervalForEditVote = parseInt($('#time-interval-for-edit-vote').val());

var costToVoteDislike = parseInt($('#cost-to-vote-dislike').val());
var minDislikeCountToHide = parseInt($('#min-dislike-count-to-hide').val());
var minCommentsToInitiateClosingVote = parseInt($('#min-comments-to-initiate-closing-vote').val());

var minScoreForTheSecondTitle = parseInt($('#min-score-for-the-second-title').val());
var minScoreForTheThirdTitle = parseInt($('#min-score-for-the-third-title').val());
var minScoreForTheFourthTitle = parseInt($('#min-score-for-the-fourth-title').val());
var minScoreForTheFifthTitle = parseInt($('#min-score-for-the-fifth-title').val());
var minScoreForTheSixthTitle = parseInt($('#min-score-for-the-sixth-title').val());
var minScoreForTheSeventhTitle = parseInt($('#min-score-for-the-seventh-title').val());

var firebaseRepoURL = $('#firebase-repo-url').val();
var firebaseConnection = new Firebase(firebaseRepoURL + 'story/' + storyID + '/');

var regexForLocalStorage = new RegExp('(?:,|^)' + storyID + ':([0-9]+,)');
var regexForURL = new RegExp('story\/[0-9]+\/#([0-9]+)');

// Change Moment JS locale globally
moment.locale('ko');
/* TODO globalization
moment.locale('ja');
moment.locale('en');
moment.locale('zh-cn');
*/

// Fill out data list into comments DOM element
function fillOutCommentsDOMElement(dataList, option) {

	if (option == 'prepend') dataList = dataList.reverse();
	
	dataList.forEach(function(data) {
		var commentDOMElement = $('#comment-dom-element').clone().removeClass('hidden').removeAttr('id');
		
		commentDOMElement.attr('data-comment-id', data.id);
		commentDOMElement.find('.comment-order').text(data.order);
		
		// If comment is deleted
		if (data.state == 'deleted') {
			commentDOMElement.find('.deleted-comment-message').removeClass('hidden');
			commentDOMElement.find('.body-section').addClass('hidden');
			commentDOMElement.find('.lower-section-collapsed').addClass('hidden');
			commentDOMElement.find('.report-comment').addClass('hidden');
		} else {
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
			
			commentDOMElement.find('.comment-context').text(data.context);
			commentDOMElement.find('.author-id').val(data.author_id);
			commentDOMElement.find('.author-nickname').text(data.author_nickname);
			commentDOMElement.find('.created-at').val(data.created_at);
			commentDOMElement.find('.time-past-text').text(moment(new Date(data.created_at)).fromNow());
			commentDOMElement.find('.like-count').text(data.like_count);
			commentDOMElement.find('.dislike-count').text(data.dislike_count);
			commentDOMElement.find('.replies-count').text(data.replies_count);
			
			// If comment should be hidden
			if (data.dislike_count >= minDislikeCountToHide && data.dislike_count > data.like_count) {
				commentDOMElement.find('.hidden-comment-message').removeClass('hidden');
				commentDOMElement.find('.body-section').addClass('hidden');
				commentDOMElement.find('.lower-section-collapsed').addClass('hidden');
			}
		}
			
		if (option == 'prepend') {
			$('#comment-list').prepend(commentDOMElement);
		} else {
			$('#comment-list').append(commentDOMElement);
		}
	});
}

// Fill out data list into replies DOM element
function fillOutRepliesDOMElement(commentID, dataList, option) {

	commentBlock = $('.comment[data-comment-id=' + commentID + ']'); 
	replyListBlock = commentBlock.find('.reply-list');

	if (option == 'prepend') dataList = dataList.reverse();
	
	dataList.forEach(function(data) {
		var replyDOMElement = $('#reply-dom-element').clone().removeClass('hidden').removeAttr('id');
		
		replyDOMElement.attr('data-reply-id', data.id);
		replyDOMElement.find('.reply-order').val(data.order);
		replyDOMElement.find('.author-id').val(data.author_id);
		replyDOMElement.find('.author-nickname').text(data.author_nickname);
		replyDOMElement.find('.created-at').val(data.created_at);
		replyDOMElement.find('.time-past-text').text(moment(new Date(data.created_at)).fromNow());
		
		// If reply is deleted
		if (data.state == 'deleted') {
			replyDOMElement.find('.deleted-reply-message').removeClass('hidden');
			replyDOMElement.find('.body-section').addClass('hidden');
			replyDOMElement.find('.report-reply').addClass('hidden');
		} else {
			replyDOMElement.find('.body-section').text(data.context);
		}
			
		if (option == 'prepend') {
			replyListBlock.prepend(replyDOMElement);
		} else {
			replyListBlock.append(replyDOMElement);
		}
	});
}

function fillOutScoreOfUsers(userIDList) {

	if (userIDList.length == 0) return ;

	var data = {}

	data['userIDList'] = userIDList.join(',');

	$.ajax({
    url: '/users/score/',
    type: 'GET',
    data: data
  }).done(function(data) {
    // Succeed to get score of users
    if (data.state == 'success') {
			userScoreListByUserID = data.scores;
			userGoldMedalListByUserID = data.gold_medals;
			userSilverMedalListByUserID = data.silver_medals;
			userBronzeMedalListByUserID = data.bronze_medals;
		
			userIDList.forEach(function(userID) {
				authorScore = userScoreListByUserID[userID];
				goldMedal = userGoldMedalListByUserID[userID];
				silverMedal = userSilverMedalListByUserID[userID];
				bronzeMedal = userBronzeMedalListByUserID[userID];
				
				authorBlock = $('.author-id[value=' + userID + ']').parent();
				authorBlock.find('.author-score').text(authorScore);
				authorBlock.find('.author-title').text(getAuthorTitle(authorScore));
				
				if (goldMedal > 0 || silverMedal > 0 || bronzeMedal > 0) {
					authorBlock.find('.author-medal').removeClass('hidden');
					
					if (goldMedal > 0) {
						authorBlock.find('.gold-medal').text(goldMedal).removeClass('hidden');
					}
					if (silverMedal > 0) {
						authorBlock.find('.silver-medal').text(silverMedal).removeClass('hidden');
					}
					if (bronzeMedal > 0) {
						authorBlock.find('.bronze-medal').text(bronzeMedal).removeClass('hidden');
					}
				}
			});
    }
  }).fail(function() {
    alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
  }).always(function() {
  });
}

function getAuthorTitle(score) {
	if (score < minScoreForTheSecondTitle) {
		return '초심자';
	} else if (score < minScoreForTheThirdTitle) {
		return '문하생';
	} else if (score < minScoreForTheFourthTitle) {
		return '논객';
	} else if (score < minScoreForTheFifthTitle) {
		return '작가';
	} else if (score < minScoreForTheSixthTitle) {
		return '달필가';
	} else if (score < minScoreForTheSeventhTitle) {
		return '명필가';
	} else {
		return '거장';
	}
}

// Get comments
function getComments(firstCommentOrder, numberOfComments, includeBoundary, option) {

	// Show loading icon
	$('#loading-icon').show();

	// Prevent from duplicated request
	whileLoadComments = true;

	var data = {};

	data['storyID'] = storyID;
	data['firstCommentOrder'] = firstCommentOrder;
	data['numberOfComments'] = numberOfComments;
	data['includeBoundary'] = includeBoundary;

	$.ajax({
		url: '/comments/',
		type: 'GET',
		data: data
	}).done(function(data) {
		// Failed to get more comments
		if (data.state == 'fail') {
			switch (data.code) {
				case 1:
					alert('유효하지 않은 요청입니다.');
					break;
				case 2:
					$('#comment-list').text('존재하지 않는 이야기입니다.');
					break;
				case 3:
					$('#comment-list').text('삭제된 이야기입니다.');
					break;
				default:
					alert('유효하지 않은 요청입니다.');
					break;
			}
		}
		// Succeed to get more comments
		else {
			fillOutCommentsDOMElement(data.comments, option);
		}
	}).fail(function() {
		alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
	}).always(function() {
		// Hide loading icon
		$('#loading-icon').hide();
		
		whileLoadComments = false;
		
		// Hide load past comments block if there is no more past comment
		if (parseInt($('#comment-list .comment').first().find('.comment-order').text()) == 1) {
			$('#load-past-comments').addClass('hidden');
		}
	});
}

// Get replies
function getReplies(commentID, lastReplyOrder, numberOfReplies, includeBoundary, option) {

	// Show loading icon
	$('#loading-icon').show();

	var data = {};

	data['commentID'] = commentID;
	data['lastReplyOrder'] = lastReplyOrder;
	data['numberOfReplies'] = numberOfReplies;
	data['includeBoundary'] = includeBoundary;

	$.ajax({
		url: '/replies/',
		type: 'GET',
		data: data
	}).done(function(data) {
		// Failed to get more replies
		if (data.state == 'fail') {
			switch (data.code) {
				case 1:
					alert('유효하지 않은 요청입니다.');
					break;
				case 2:
					alert('존재하지 않는 댓글입니다.');
					break;
				case 3:
					alert('삭제된 댓글입니다.');
					break;
				default:
					alert('유효하지 않은 요청입니다.');
					break;
			}
		}
		// Succeed to get more replies
		else {
			commentBlock = $('.comment[data-comment-id=' + commentID + ']'); 
			replyListBlock = commentBlock.find('.reply-list');
			
			fillOutRepliesDOMElement(commentID, data.replies, option);
			
			// Hide load past replies button if there is no more past reply
			if (parseInt(replyListBlock.find('.reply').last().find('.reply-order').val()) == 1) {
				commentBlock.find('.load-past-replies-btn').addClass('hidden');
			} else {
				commentBlock.find('.load-past-replies-btn').removeClass('hidden');
			}
			
			// Fill out author score
			userIDList = [];
			data.replies.forEach(function(reply) {
				if (userIDList.indexOf(reply.author_id) == -1) userIDList.push(reply.author_id);
			});
			fillOutScoreOfUsers(userIDList);
		}
	}).fail(function() {
		alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
	}).always(function() {
		// Hide loading icon
		$('#loading-icon').hide();
	});
}

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

	// Clear alert message
	function clearAlertMessage(target) {
		switch (target) {
			case 'comment':
				$('#create-comment-form .alert-danger').text('').addClass('hidden');
				break;
			case 'reply':
				$('.create-reply-form .alert-danger').text('').addClass('hidden');
				break;
			case 'report':
				$('#report-comment-form .alert-success, #report-comment-form .alert-danger').text('').addClass('hidden');
				$('#report-reply-form .alert-success, #report-reply-form .alert-danger').text('').addClass('hidden');
				break;
			default:
				break;
		}
  }

  $(document).on('keyup', '#create-comment-form textarea', function() {
    // Count line break as 2 characters
    length = $(this).val().replace(/(\r\n|\n|\r)/g, '--').length;
    $(this).parent().find('.context-character-count').text(length);
		
    // Auto sizing textarea height
    while ($(this).outerHeight() < this.scrollHeight +
      parseFloat($(this).css('borderTopWidth')) +
      parseFloat($(this).css('borderBottomWidth'))) {
      $(this).height($(this).height()+1);
    };
  });

  $(document).on('keyup', '.create-reply-form textarea', function() {
    // Count line break as 2 characters
    length = $(this).val().replace(/(\r\n|\n|\r)/g, '--').length;
    $(this).parent().find('.context-character-count').text(length);
		
    // Auto sizing textarea height
    while ($(this).outerHeight() < this.scrollHeight +
      parseFloat($(this).css('borderTopWidth')) +
      parseFloat($(this).css('borderBottomWidth'))) {
      $(this).height($(this).height()+1);
    };
		
		// Set button height equal to textarea
		$(this).closest('.create-reply-form').find('.reply-submit-btn').css('height', $(this).outerHeight());
  });

  $(document).on('keyup', '#report-comment-form textarea, #report-reply-form textarea', function() {
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

	// Validate comment creation form 
  $(document).on('submit', '#create-comment-form', function(event) {
    event.preventDefault();
    
		// Show loading icon
		$('#loading-icon').show();
		
    // Prevent from double click
    $('#comment-submit-btn').button('loading');
		
		clearAlertMessage('comment');
		
		commentForm = $(this);
		
		var formData = new FormData();
		
		formData.append('storyID', storyID);
    formData.append('context', commentForm.find('textarea').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ''));
    
    if ($('#image')[0].files[0] != null && $('.file-input').hasClass('has-error') == false) {
      formData.append('image', $('#image')[0].files[0]);
			formData.append('imageReference', $('#image-reference').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ''));
			formData.append('imagePosition', $('input[name="image-position"]:checked').val());
    }
    
    setCSRFToken();
		
		$.ajax({
      url: '/comment/create/',
      type: 'POST',
      data: formData,
      contentType: false,
      processData: false
    }).done(function(data) {
      // Failed to create story
      if (data.state == 'fail') {
        switch (data.code) {
          case 1:
            $('#create-comment-form .alert-danger').text('입력칸을 모두 채워주세요').removeClass('hidden');
            break;
          // Show signup modal if user not logged in
          case 2:
            $('#signup-tab').tab('show');
            $('#signup-form-container').addClass('in active');
            $('#login-form-container').removeClass('in active');
            $('#modal-signup').modal('show');
            break;
					case 3:
            $('#create-comment-form .alert-danger').text('존재하지 않는 이야기입니다').removeClass('hidden');
            break;
          case 4:
            $('#create-comment-form .alert-danger').text('삭제되거나 완결된 이야기입니다').removeClass('hidden');
            break;
					case 5:
            $('#create-comment-form .alert-danger').text('새 댓글을 쓰기 위해서는 최소 ' +
                timeIntervalForNewComment + '분의 간격이 필요합니다').removeClass('hidden');
            break;
          default:
            $('#create-comment-form .alert-danger').text('댓글을 쓰는데 실패했습니다').removeClass('hidden');
            break;
        }
      }
      // Succeed to create comment and clear form
      else {
				$('#image').fileinput('clear');
				$('#create-comment-form textarea').val('').removeAttr('style');
				$('#create-comment-form .context-character-count').text('0');
				$('#image-reference').val('');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
      $('#comment-submit-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });

	// Validate reply creation form 
  $(document).on('submit', '.create-reply-form', function(event) {
    event.preventDefault();
		
		replyForm = $(this);
    
		// Show loading icon
		$('#loading-icon').show();
		
    // Prevent from double click
    replyForm.find('.reply-submit-btn').button('loading');
		
		clearAlertMessage('reply');
		
    setCSRFToken();
		
		$.ajax({
      url: '/reply/create/',
      type: 'POST',
      data: {
				'commentID': replyForm.closest('.comment').attr('data-comment-id'),
				'context': replyForm.find('textarea').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')
			}
    }).done(function(data) {
      // Failed to create story
      if (data.state == 'fail') {
        switch (data.code) {
          case 1:
            replyForm.find('.alert-danger').text('입력칸을 모두 채워주세요').removeClass('hidden');
            break;
          // Show signup modal if user not logged in
          case 2:
            $('#signup-tab').tab('show');
            $('#signup-form-container').addClass('in active');
            $('#login-form-container').removeClass('in active');
            $('#modal-signup').modal('show');
            break;
					case 3:
            replyForm.find('.alert-danger').text('존재하지 않는 댓글입니다').removeClass('hidden');
            break;
          case 4:
            replyForm.find('.alert-danger').text('삭제된 이야기입니다').removeClass('hidden');
            break;
					case 5:
            replyForm.find('.alert-danger').text('새 대댓글을 쓰기 위해서는 최소 ' +
                timeIntervalForNewReply + '분의 간격이 필요합니다').removeClass('hidden');
            break;
          default:
            replyForm.find('.alert-danger').text('대댓글을 쓰는데 실패했습니다').removeClass('hidden');
            break;
        }
      }
      // Succeed to create reply and clear form
      else {
				replyForm.find('textarea').val('').removeAttr('style');
				replyForm.find('.reply-submit-btn').removeAttr('style');
				replyForm.find('.context-character-count').text('0');
      }
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
    }).always(function() {
      // Recover button clickable
			replyForm.find('.reply-submit-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
  });

	// Show hidden comment when user clicked hidden comment message
	$(document).on('click', '.hidden-comment-message', function() {
		commentBlock = $(this).closest('.comment');
		
		commentBlock.find('.hidden-comment-message').addClass('hidden');
		commentBlock.find('.body-section').removeClass('hidden');
		commentBlock.find('.lower-section-collapsed').removeClass('hidden');
	});

	// Load past comments when user clicked load past comment block
	$(document).on('click', '#load-past-comments', function() {
		originalFirstCommentBlock = $('#comment-list .comment').first();
		originalFirstCommentOrder = parseInt(originalFirstCommentBlock.find('.comment-order').text());
		
		firstCommentOrder = Math.max(originalFirstCommentOrder - commentsPerQuery, 1);
		numberOfComments = originalFirstCommentOrder - firstCommentOrder;
		includeBoundary = true;
		
		getComments(firstCommentOrder, numberOfComments, includeBoundary, 'prepend');
	});

	// Load past replies when user clicked load past replies button
	$(document).on('click', '.load-past-replies-btn', function() {
		commentBlock = $(this).closest('.comment');
		commentID = commentBlock.attr('data-comment-id');
		replyListBlock = commentBlock.find('.reply-list');
		
		lastReplyOrder = parseInt(replyListBlock.find('.reply').last().find('.reply-order').val());
		numberOfReplies = Math.min(lastReplyOrder - 1, repliesPerQuery);
		includeBoundary = false;
		
		getReplies(commentID, lastReplyOrder, numberOfReplies, includeBoundary, 'append');
	});

	// Show detail information of specific comment when user click collapsed block
	$(document).on('click', '.lower-section-collapsed', function() {
		// Collapse other uncollpased blocks
		uncollapsedCommentBlock = $('.lower-section-uncollapsed:not(.hidden)').closest('.comment');
		uncollapsedCommentBlock.find('.lower-section-uncollapsed').addClass('hidden');
		uncollapsedCommentBlock.find('.lower-section-collapsed').removeClass('hidden');
		uncollapsedCommentBlock.find('.reply-list').html('');
			
		// Make commment block uncollapsed
		commentBlock = $(this).closest('.comment');
		commentID = commentBlock.attr('data-comment-id');
		commentBlock.find('.lower-section-collapsed').addClass('hidden');
		commentBlock.find('.lower-section-uncollapsed').removeClass('hidden');
		
		// Scroll to comment block
		$('html, body').animate({ scrollTop: commentBlock.find('.lower-section-uncollapsed').offset().top  - 100}, 'fast');
		
		// Check whether user voted or not
		$.ajax({
			url: '/comment/' + commentID + '/vote/check/',
			type: 'GET'
		}).done(function(data) {
			if (data.state == 'success') {
				switch (data.code) {
					case 2:
						commentBlock.find('.btn-like').addClass('active');
						break;
					case 3:
						commentBlock.find('.btn-dislike').addClass('active');
						break;
					default:
						break;
				}
			}
		}).fail(function() {
			alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
		}).always(function() {
		});
		
		// Fill out comment author score
		userIDList = [];
		userIDList.push(parseInt(commentBlock.find('.author-id').val()));
		fillOutScoreOfUsers(userIDList);
		
		// Show loading icon
		$('#loading-icon').show();
		
		// Fill out replies count and get recent replies
		firebaseConnection.child('comment/' + commentID + '/last_reply_order/').once('value', function(snapshot) {
			
			latestReplyOrder = snapshot.val();
			
			if (latestReplyOrder == null) {
				// Update Firebase DB
				$.ajax({
					url: '/comment/' + commentID + '/firebase/',
					type: 'GET'
				}).done(function(data) {
				}).fail(function() {
				}).always(function() {
				});
				
				latestReplyOrder = 0;
			}
			
			commentBlock.find('.replies-count').text(latestReplyOrder);
			
			if (latestReplyOrder > 0) {
				lastReplyOrder = latestReplyOrder;
				numberOfReplies = Math.min(lastReplyOrder, repliesPerQuery);
				includeBoundary = true;
				
				getReplies(commentID, lastReplyOrder, numberOfReplies, includeBoundary, 'append');
			}
		});
		
		// Hide loading icon
		$('#loading-icon').hide();
	});

	// Collapse upcollapsed comment block when user click icon
	$(document).on('click', '.lower-section-uncollapsed .icon-container', function() {
		uncollapsedCommentBlock = $(this).closest('.comment');
		uncollapsedCommentBlock.find('.lower-section-uncollapsed').addClass('hidden');
		uncollapsedCommentBlock.find('.lower-section-collapsed').removeClass('hidden');
		uncollapsedCommentBlock.find('.reply-list').html('');
	});

	// If user tries to vote/cancel like for comment
	$(document).on('click', '.btn-like', function() {
		
		// Show loading icon
		$('#loading-icon').show();
		
		commentBlock = $(this).closest('.comment');
		
    setCSRFToken();
		
    $.ajax({
      url: '/comment/' + commentID + '/like/',
      type: 'POST'
    }).done(function(data) {
			// Failed to vote/cancel like for comment
      if (data.state == 'fail') {
        switch (data.code) {
          // Show signup modal if user not logged in
          case 1:
            $('#signup-tab').tab('show');
            $('#signup-form-container').addClass('in active');
            $('#login-form-container').removeClass('in active');
            $('#modal-signup').modal('show');
            break;
          case 2:
						alert('존재하지 않는 댓글입니다.');
            break;
          case 3:
						alert('자신의 댓글에는 투표할 수 없습니다.');
            break;
          case 4:
						alert(timeIntervalForEditVote + '분이 지나면 취소하거나 삭제할 수 없습니다.');
            break;
          default:
						alert('추천에 실패했습니다.');
            break;
        }
      }
			// Succeed to vote/cancel like for comment
			else {
        switch (data.code) {
					// Cancel like
          case 1:
            commentBlock.find('.btn-like').removeClass('active');
            commentBlock.find('.btn-dislike').removeClass('active');
            break;
					// Cancel dislike, vote like
          case 2:
            commentBlock.find('.btn-like').addClass('active');
            commentBlock.find('.btn-dislike').removeClass('active');
            break;
					// Vote like
          case 3:
            commentBlock.find('.btn-like').addClass('active');
            commentBlock.find('.btn-dislike').removeClass('active');
            break;
          default:
            break;
				}
				// Update like count and dislike count
				commentBlock.find('.like-count').text(data.like_count);
				commentBlock.find('.dislike-count').text(data.dislike_count);
			}
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
    }).always(function() {
			// Hide loading icon
			$('#loading-icon').hide();
    });
	});

	// If user tries to vote/cancel dislike for comment
	$(document).on('click', '.btn-dislike', function() {
		
		// Show loading icon
		$('#loading-icon').show();
		
		commentBlock = $(this).closest('.comment');
		
    setCSRFToken();
		
    $.ajax({
      url: '/comment/' + commentID + '/dislike/',
      type: 'POST'
    }).done(function(data) {
			// Failed to vote/cancel dislike for comment
      if (data.state == 'fail') {
        switch (data.code) {
          // Show signup modal if user not logged in
          case 1:
            $('#signup-tab').tab('show');
            $('#signup-form-container').addClass('in active');
            $('#login-form-container').removeClass('in active');
            $('#modal-signup').modal('show');
            break;
          case 2:
						alert('존재하지 않는 댓글입니다.');
            break;
          case 3:
						alert('자신의 댓글에는 투표할 수 없습니다.');
            break;
          case 4:
						alert(timeIntervalForEditVote + '분이 지나면 취소하거나 삭제할 수 없습니다.');
            break;
          case 5:
						alert('비추천을 하기 위해서는 최소 ' + costToVoteDislike + ' 필력이 필요합니다.');
            break;
          default:
						alert('비추천에 실패했습니다.');
            break;
        }
      }
			// Succeed to vote/cancel dislike for comment
			else {
        switch (data.code) {
					// Cancel dislike
          case 1:
            commentBlock.find('.btn-like').removeClass('active');
            commentBlock.find('.btn-dislike').removeClass('active');
            break;
					// Cancel like, vote dislike
          case 2:
            commentBlock.find('.btn-like').removeClass('active');
            commentBlock.find('.btn-dislike').addClass('active');
            break;
					// Vote dislike
          case 3:
            commentBlock.find('.btn-like').removeClass('active');
            commentBlock.find('.btn-dislike').addClass('active');
            break;
          default:
            break;
				}
				// Update like count and dislike count
				commentBlock.find('.like-count').text(data.like_count);
				commentBlock.find('.dislike-count').text(data.dislike_count);
			}
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
    }).always(function() {
			// Hide loading icon
			$('#loading-icon').hide();
    });
	});

	// Show report comment modal
	$(document).on('click', '.report-comment', function() {
		commentID = $(this).closest('.comment').attr('data-comment-id');
		$('#report-comment-form .comment-id').val(commentID);
		
		$('#modal-report-comment').modal('show');
	});

	// Show report reply modal
	$(document).on('click', '.report-reply', function() {
		replyID = $(this).closest('.reply').attr('data-reply-id');
		$('#report-reply-form .reply-id').val(replyID);
		
		$('#modal-report-reply').modal('show');
	});

	// Report comment
	$(document).on('submit', '#report-comment-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
		$('#loading-icon').show();
		
    // Prevent from double click
    $('#report-comment-btn').button('loading');
		
		clearAlertMessage('report');
		
    setCSRFToken();
		
		$.ajax({
      url: '/comment/' + $('#report-comment-form .comment-id').val() + '/report/',
      type: 'POST',
      data: {
				'category': $('#report-comment-form select').val(),
				'reason': $('#report-comment-form textarea').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')
			}
    }).done(function(data) {
      // Failed to report comment
      if (data.state == 'fail') {
        switch (data.code) {
          case 1:
						$('#report-comment-form .alert-danger').text('입력칸을 모두 채워주세요').removeClass('hidden');
            break;
          case 2:
						$('#report-comment-form .alert-danger').text('유효하지 않은 신고 사유입니다').removeClass('hidden');
            break;
          // Show signup modal if user not logged in
          case 3:
            $('#signup-tab').tab('show');
            $('#signup-form-container').addClass('in active');
            $('#login-form-container').removeClass('in active');
            $('#modal-signup').modal('show');
            break;
          case 4:
						$('#report-comment-form .alert-danger').text('존재하지 않는 댓글입니다').removeClass('hidden');
            break;
					case 5:
						$('#report-comment-form .alert-danger').text('본인 댓글을 신고할 수는 없습니다').removeClass('hidden');
            break;
					default:
						$('#report-comment-form .alert-danger').text('댓글 신고에 실패했습니다').removeClass('hidden');
            break;
				}
			}
			// Succeed to report comment
			else {
				$('#report-comment-form textarea').val('');
				$('#report-comment-form .alert-success').text('성공적으로 신고했습니다').removeClass('hidden');
			}
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
    }).always(function() {
			// Recover button clickable
			$('#report-comment-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
	});

	// Report reply
	$(document).on('submit', '#report-reply-form', function(event) {
    event.preventDefault();
		
		// Show loading icon
		$('#loading-icon').show();
		
    // Prevent from double click
    $('#report-reply-btn').button('loading');
		
		clearAlertMessage('report');
		
    setCSRFToken();
		
		$.ajax({
      url: '/reply/' + $('#report-reply-form .reply-id').val() + '/report/',
      type: 'POST',
      data: {
				'category': $('#report-reply-form select').val(),
				'reason': $('#report-reply-form textarea').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')
			}
    }).done(function(data) {
      // Failed to report reply
      if (data.state == 'fail') {
        switch (data.code) {
          case 1:
						$('#report-reply-form .alert-danger').text('입력칸을 모두 채워주세요').removeClass('hidden');
            break;
          case 2:
						$('#report-reply-form .alert-danger').text('유효하지 않은 신고 사유입니다').removeClass('hidden');
            break;
          // Show signup modal if user not logged in
          case 3:
            $('#signup-tab').tab('show');
            $('#signup-form-container').addClass('in active');
            $('#login-form-container').removeClass('in active');
            $('#modal-signup').modal('show');
            break;
          case 4:
						$('#report-reply-form .alert-danger').text('존재하지 않는 대댓글입니다').removeClass('hidden');
            break;
					case 5:
						$('#report-reply-form .alert-danger').text('본인 대댓글을 신고할 수는 없습니다').removeClass('hidden');
            break;
					default:
						$('#report-reply-form .alert-danger').text('대댓글을 신고에 실패했습니다').removeClass('hidden');
						break;
				}
			}
			// Succeed to report reply
			else {
				$('#report-reply-form textarea').val('');
				$('#report-reply-form .alert-success').text('성공적으로 신고했습니다').removeClass('hidden');
			}
    }).fail(function() {
      alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
    }).always(function() {
			// Recover button clickable
			$('#report-reply-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
    });
	});

	// Add story to favorite story list
	$(document).on('click', '#add-story-to-favorite', function() {
		if ($('#add-story-to-favorite').attr('data-favorite') == 'false') {
			
			// Show loading icon
			$('#loading-icon').show();
			
			$.ajax({
				url: '/story/favorite/add/' + storyID + '/',
				type: 'GET'
			}).done(function(data) {
				// Failed to add story to favorite story list
				if (data.state == 'fail') {
					switch (data.code) {
						// Show signup modal if user not logged in
						case 1:
							$('#signup-tab').tab('show');
							$('#signup-form-container').addClass('in active');
							$('#login-form-container').removeClass('in active');
							$('#modal-signup').modal('show');
							break;
						case 2:
							$('#add-story-to-favorite').text('존재하지 않는 이야기입니다');
							break;
						case 3:
							$('#add-story-to-favorite').attr('data-favorite', 'true').html('이미 <strong>즐겨찾기</strong>에 등록되어 있습니다');
							break;
						default:
							$('#add-story-to-favorite').text('즐겨찾기 등록에 실패했습니다');
							break;
					}
				}
				// Succeed to add story to favorite story list
				else {
					$('#add-story-to-favorite').attr('data-favorite', 'true').html('<strong>즐겨찾기</strong>에 등록됐습니다');
				}
			}).fail(function() {
				alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
			}).always(function() {
				// Hide loading icon
				$('#loading-icon').hide();
			});
		}
	});

	$(window).on('scroll', function() {
		// Show 'back to top' if scroll bar appears
		if ($(window).scrollTop() == 0) {
			$('#back-to-top').addClass('hidden');
		} else { 
			$('#back-to-top').removeClass('hidden');
		}
		
		// Get more comments
		if ($(window).scrollTop() + $(window).height() > $('#share-story-block').offset().top - 350) {
			// Prevent from duplicated request
			if (whileLoadComments == false) {
				firstCommentOrder = parseInt($('#comment-list .comment').last().find('.comment-order').text());
				numberOfComments = Math.min(latestCommentOrder - firstCommentOrder, commentsPerQuery);
				includeBoundary = false;
				
				if (numberOfComments > 0) getComments(firstCommentOrder, numberOfComments, includeBoundary, 'append');
			}
		}
	}); 

	firebaseConnection.on('child_added', function(snapshot) {
		checkContentUpdated(snapshot);
	});

	firebaseConnection.on('child_changed', function(snapshot) {
		checkContentUpdated(snapshot);
	});

	// Check the latest comment or reply updated
	function checkContentUpdated(snapshot) {
		// When comment newly added 
		if (snapshot.key() == 'last_comment_order') {
			latestCommentOrder = snapshot.val();
			
			// Update read stories value at local storage
			readStories = localStorage.getItem('read_stories') || '';
			
			if (regexForLocalStorage.test(readStories) == false) {
				readStories = storyID + ':' + latestCommentOrder + ',' + readStories;
				
				try {
					localStorage.setItem('read_stories', readStories);
				} catch(e) {
					void(0);
				}
			} else {
				matchedString = readStories.match(regexForLocalStorage)[1];
				matchedStringLength = matchedString.length;
				startPosition = readStories.indexOf(matchedString);
				
				readStories = readStories.slice(0, startPosition) + latestCommentOrder + ',' +
					readStories.slice(startPosition + matchedStringLength);
				
				try {
					localStorage.setItem('read_stories', readStories);
				} catch(e) {
					void(0);
				}
			}
			
			// Update all the comments count value in DOM
			$('.comments-count').text(latestCommentOrder);
			
			// Append newly added comment to comment list
			firstCommentOrder = parseInt($('#comment-list .comment').last().find('.comment-order').text());
			numberOfComments = Math.min(latestCommentOrder - firstCommentOrder, commentsPerQuery);
			includeBoundary = false;
			
			if (numberOfComments > 0) getComments(firstCommentOrder, numberOfComments, includeBoundary, 'append');
		} 
		// When reply newly added
		else {
			uncollapsedCommentBlock = $('.lower-section-uncollapsed:not(.hidden)').closest('.comment');
			uncollapsedCommentID = uncollapsedCommentBlock.attr('data-comment-id');
			
			if (uncollapsedCommentID != null && snapshot.child(uncollapsedCommentID + '/last_reply_order/').val() > latestReplyOrder) {
				originalLatestReplyOrder = latestReplyOrder;
				latestReplyOrder = snapshot.child(uncollapsedCommentID + '/last_reply_order/').val();
				numberOfReplies = Math.min(latestReplyOrder - originalLatestReplyOrder, repliesPerQuery);
				includeBoundary = true;
				
				// Update replies count value
				uncollapsedCommentBlock.find('.replies-count').text(latestReplyOrder);
				
				// Append newly added reply to reply list
				getReplies(uncollapsedCommentID, latestReplyOrder, numberOfReplies, includeBoundary, 'prepend');
			}
		}
	}

	// Show conditions to close story if user clicked guide message
	$(document).on('click', '#guide-message-for-closing-story', function() {
		// Show conditions to close story
		$('#guide-message-for-closing-story').addClass('hidden');
		$('#conditions-to-close-story').removeClass('hidden');
		
		// Check whether user is contributed story or not
		if (latestCommentOrder >= minCommentsToInitiateClosingVote) {
			// Show loading icon
			$('#loading-icon').show();
			
			$.ajax({
				url: '/story/' + storyID + '/contributor/check/',
				type: 'GET'
			}).done(function(data) {
				if (data.state == 'success') {
					// When user is contributor
					$('#initiate-closing-vote-btn').removeClass('hidden');
				}
			}).fail(function() {
			}).always(function() {
				// Hide loading icon
				$('#loading-icon').hide();
			});
		} 
	});

	// Initiate closing vote
	$(document).on('click', '#initiate-closing-vote-btn', function() {
		// Show loading icon
		$('#loading-icon').show();
		
    setCSRFToken();
		
		$.ajax({
			url: '/closing_vote/create/',
			type: 'POST',
			data: {
				'storyID': storyID
			}
		}).done(function(data) {
			// Failed to create closing vote
			if (data.state == 'fail') {
				switch(data.code) {
					case 1:
						alert('유효하지 않은 요청입니다.');
						break;
					case 2:
						alert('존재하지 않는 이야기입니다.');
						break;
					case 3:
						alert('삭제되거나 완결된 이야기입니다.');
						break;
					case 4:
						alert('완결 투표를 개시하기 위해서는 최소 ' + minCommentsToInitiateClosingVote + '개의 댓글이 있어야 합니다.');
						break;
					case 5:
						alert('이야기에 댓글을 쓴 적 있는 사람만 투표를 개시할 수 있습니다.');
						break;
					case 6:
						alert('이미 진행 중인 투표가 있습니다. 새로 고침해서 확인해보세요.');
						break;
					default:
						alert('투표를 개시하는데 실패했습니다.');
						break;
				}
			}
			// Succeed to create closing vote
			else {
				$('#conditions-to-close-story').addClass('hidden');
				$('#closing-vote').removeClass('hidden');
				
				$('#closing-vote-id').val(data.id);
				$('#closing-vote-due').val(data.due + 'Z');
				$('#closing-vote-time-left').text(moment($('#closing-vote-due').val()).fromNow());
				
				$('#agreement-ratio, #disagreement-ratio').css('width', '50%');
				$('#agreement-count, #disagreement-count').text('0');
			}
		}).fail(function() {
			alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
		}).always(function() {
			// Hide loading icon
			$('#loading-icon').hide();
		});
	});

	// Vote agreement to closing vote
	$(document).on('click', '#agreement-btn', function() {
		// Show loading icon
		$('#loading-icon').show();
		
		var closingVoteID = $('#closing-vote-id').val(); 
		
    setCSRFToken();
		
		$.ajax({
			url: '/closing_vote/' + closingVoteID + '/agree/',
			type: 'POST'
		}).done(function(data) {
			// Failed to vote/cancel agreement
			if (data.state == 'fail') {
				switch(data.code) {
          // Show signup modal if user not logged in
          case 1:
            $('#signup-tab').tab('show');
            $('#signup-form-container').addClass('in active');
            $('#login-form-container').removeClass('in active');
            $('#modal-signup').modal('show');
						break;
					case 2:
						alert('존재하지 않는 투표입니다.');
						break;
					case 3:
						alert('이미 끝난 투표입니다.');
						break;
					default:
						alert('투표에 실패했습니다.')
						break;
				}
			}
			// Succeed to vote/cancel agreement
			else {
				switch(data.code) {
					// Cancel agreement
					case 1:
						$('#agreement-btn').removeClass('active');
						$('#disagreement-btn').removeClass('active');
						break;
					// Cancel disagreement, vote agreement
					case 2:
						$('#agreement-btn').addClass('active');
						$('#disagreement-btn').removeClass('active');
						break;
					// Vote agreement
					case 3:
						$('#agreement-btn').addClass('active');
						$('#disagreement-btn').removeClass('active');
						break;
					default:
						break;
				}
				
				$('#agreement-ratio').css('width', data.agreement_ratio + '%');
				$('#disagreement-ratio').css('width', 100 - data.agreement_ratio + '%');
				
				$('#agreement-count').text(data.agreement_count);
				$('#disagreement-count').text(data.disagreement_count);
			}
		}).fail(function() {
			alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
		}).always(function() {
			// Hide loading icon
			$('#loading-icon').hide();
		});
	});

	// Vote disagreement to closing vote
	$(document).on('click', '#disagreement-btn', function() {
		// Show loading icon
		$('#loading-icon').show();
		
		closingVoteID = $('#closing-vote-id').val(); 
		
    setCSRFToken();
		
		$.ajax({
			url: '/closing_vote/' + closingVoteID + '/disagree/',
			type: 'POST'
		}).done(function(data) {
			// Failed to vote/cancel disagreement
			if (data.state == 'fail') {
				switch(data.code) {
          // Show signup modal if user not logged in
          case 1:
            $('#signup-tab').tab('show');
            $('#signup-form-container').addClass('in active');
            $('#login-form-container').removeClass('in active');
            $('#modal-signup').modal('show');
						break;
					case 2:
						alert('존재하지 않는 투표입니다.');
						break;
					case 3:
						alert('이미 끝난 투표입니다.');
						break;
					default:
						alert('투표에 실패했습니다.')
						break;
				}
			}
			// Succeed to vote/cancel disagreement
			else {
				switch(data.code) {
					// Cancel disagreement
					case 1:
						$('#agreement-btn').removeClass('active');
						$('#disagreement-btn').removeClass('active');
						break;
					// Cancel agreement, vote disagreement
					case 2:
						$('#agreement-btn').removeClass('active');
						$('#disagreement-btn').addClass('active');
						break;
					// Vote disagreement
					case 3:
						$('#agreement-btn').removeClass('active');
						$('#disagreement-btn').addClass('active');
						break;
					default:
						break;
				}
				
				$('#agreement-ratio').css('width', data.agreement_ratio + '%');
				$('#disagreement-ratio').css('width', 100 - data.agreement_ratio + '%');
				
				$('#agreement-count').text(data.agreement_count);
				$('#disagreement-count').text(data.disagreement_count);
			}
		}).fail(function() {
			alert('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.');
		}).always(function() {
			// Hide loading icon
			$('#loading-icon').hide();
		});
	});

	// Kakao talk sharing
	Kakao.init('5b4282cfef3024d07fdd51b4cc34deb8');
	Kakao.Link.createTalkLinkButton({
		container: '#kakaotalk-share',
		label: '[모두펜] ' + storyTitle,
		image: {
			src: 'http://res.cloudinary.com/modupen/image/upload/v1441194561/basic%20component/kakaotalk_share.png',
			width: '274',
			height: '99'
		},
		webButton: {
			text: '이야기 읽기',
			url: 'https://modupen.com/story/' + storyID + '/'
		}
	});
	
	// Alert that kakaotalk and line messenger sharing is only available at mobile
	$(document).on('click', '#line-share, #kakaotalk-share', function() {
		// Detect desktop browser
		if (!('ontouchstart' in window)) {
			alert("모바일에서만 가능합니다");
		}
		return false;
	});
	
	// Alert that twitter sharing in IE is not working properly
	$(document).on('click', '#twitter-share', function() {
		// Check whether browser is IE or not
		if (window.navigator.userAgent.indexOf("MSIE ") > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./)) {
			alert("Internet Explorer 에서 트위터 공유는 정상적으로 작동하지 않습니다.");
			return false;
		}
	});

	// Get recommended stories
	$(document).one('inview', '#story-recommendation-block', function() {
		// Show loading icon
		$('#loading-icon').show();
		
		$.ajax({
			url: '/stories/recommended/',
			type: 'GET'
		}).done(function(data) {
			// Get recently created stories among processing stories
			data.recent_stories.forEach(function(story) {
				$('#recent-stories').append('<a href="/story/' + story[0] + '/">' + story[1] + '</a>');
			});
			
			// Get popular stories among processing stories
			data.popular_stories.forEach(function(story) {
				$('#popular-stories').append('<a href="/story/' + story[0] + '/">' + story[1] + '</a>');
			});
			
			// Get randomly picked stories among closed stories
			data.closed_stories.forEach(function(story) {
				$('#closed-stories').append('<a href="/story/' + story[0] + '/">' + story[1] + '</a>');
			});
		}).fail(function() {
		}).always(function() {
			// Hide loading icon
			$('#loading-icon').hide();
		});
	});
});

$(window).load(function() {

	currentURL = window.location.href;
	readStories = localStorage.getItem('read_stories') || '';

	try {
		firstCommentOrder = parseInt(currentURL.match(regexForURL)[1]);
	} catch(e) {
		firstCommentOrder = null;
	}

	// When user tries to see comments from specific comment
	if (firstCommentOrder != null && firstCommentOrder >= 1 && firstCommentOrder <= latestCommentOrder) {
		numberOfComments = Math.min(latestCommentOrder - firstCommentOrder + 1, commentsPerQuery);
		includeBoundary = true;
		
		getComments(firstCommentOrder, numberOfComments, includeBoundary, 'append');
	} else {
		try {
			lastlyReadCommentOrder = parseInt(readStories.match(regexForLocalStorage)[1]);
		} catch(e) {
			lastlyReadCommentOrder = null;
		}
		
		// When user already read this story
		if (lastlyReadCommentOrder != null && lastlyReadCommentOrder >= 1 && lastlyReadCommentOrder <= latestCommentOrder) {
			numberOfLeftComments = parseInt(commentsPerQuery / 2) - 1;
			numberOfRightComments = commentsPerQuery - numberOfLeftComments;
			
			if (latestCommentOrder - numberOfLeftComments < 1) {
				firstCommentOrder = 1;
				numberOfComments = Math.max(commentsPerQuery, latestCommentOrder) - firstCommentOrder;
				includeBoundary = true;
			} else {
				if (lastlyReadCommentOrder + numberOfRightComments > latestCommentOrder) {
					firstCommentOrder = Math.max(latestCommentOrder - commentsPerQuery + 1, 1)
					numberOfComments = latestCommentOrder - firstCommentOrder + 1
					includeBoundary = true;
				} else {
					firstCommentOrder = latestCommentOrder - numberOfLeftComments;
					numberOfComments = commentsPerQuery;
					includeBoundary = true;
				}
			}
			getComments(firstCommentOrder, numberOfComments, includeBoundary, 'append');
		}
		// When user read this story for the first time
		else {
			firstCommentOrder = 1
			numberOfComments = Math.min(latestCommentOrder, commentsPerQuery);
			includeBoundary = true;
			
			getComments(firstCommentOrder, numberOfComments, includeBoundary, 'append');
		}
	}

	// Hide load past comments block if there is no more past comment
	if (firstCommentOrder != 1) {
		$('#load-past-comments').removeClass('hidden');
	}
	
	// Update read stories value at local storage
	if (regexForLocalStorage.test(readStories) == false) {
		readStories = storyID + ':' + latestCommentOrder + ',' + readStories;
		
		try {
      localStorage.setItem('read_stories', readStories);
    } catch(e) {
      void(0);
    }
	}	else {
		matchedString = readStories.match(regexForLocalStorage)[1];
		matchedStringLength = matchedString.length;
		startPosition = readStories.indexOf(matchedString);
		
		readStories = readStories.slice(0, startPosition) + latestCommentOrder + ',' +
			readStories.slice(startPosition + matchedStringLength);
		
		try {
			localStorage.setItem('read_stories', readStories);
		} catch(e) {
			void(0);
		}
	}

	if ($('#closing-vote-due').val() != '') {
		$('#closing-vote-time-left').text(moment($('#closing-vote-due').val()).fromNow());
	}

	// Update time past text every minute
	setInterval(function() {
		$('.created-at').each(function() {
			$(this).parent().find('.time-past-text').text(moment(new Date($(this).val())).fromNow());
		});
		$('#closing-vote-time-left').text(moment($('#closing-vote-due').val()).fromNow());
	}, moment.duration(1, 'minutes'));
});
