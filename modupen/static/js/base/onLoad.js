$(window).load(function() {

	// Hide loading icon
	$('#loading-icon').hide();

	// Show beta logo
	$('#beta-logo').removeClass('hidden');

	// Vertically center aligning for modal
	function centerModal() {
		$(this).css('display', 'block');
		var $dialog = $(this).find(".modal-dialog"),
		offset = ($(window).height() - $dialog.height()) / 3,
		bottomMargin = parseInt($dialog.css('marginBottom'), 10);
		
		if (offset < bottomMargin) offset = bottomMargin;
		$dialog.css("margin-top", offset);
	}
	$(document).on('show.bs.modal', '.modal', centerModal);
	$(window).on("resize", function() {
		$('.modal:visible').each(centerModal);
	});

	// Change active tab when user opened login or sign up modal
	$(document).on('click', '#login-modal-btn', function() {
		$('#login-tab').addClass('active');
		$('#signup-tab').removeClass('active');
		$('#login-tab').tab('show');
		$('#login-form-container').addClass('in active');
		$('#signup-form-container').removeClass('in active');
		$('#modal-signup').modal('show');
	});
	$(document).on('click', '#signup-modal-btn', function() {
		$('#signup-tab').addClass('active');
		$('#login-tab').removeClass('active');
		$('#signup-tab').tab('show');
		$('#signup-form-container').addClass('in active');
		$('#login-form-container').removeClass('in active');
		$('#modal-signup').modal('show');
	});

	// Activate/deactivate tab
	$(document).on('show.bs.tab', '#login-tab', function() {
		$('#login-tab').addClass('active');
		$('#signup-tab').removeClass('active');
	});
	$(document).on('show.bs.tab', '#signup-tab', function() {
		$('#signup-tab').addClass('active');
		$('#login-tab').removeClass('active');
	});

	// Prevent CSRF token problem before sending reqeust with ajax
	function setCSRFToken() {
		$.ajaxSetup({
			headers: {
				'X-CSRFToken': $.cookie('csrftoken')
			}
		}); 
	}

	// Validate login
	$(document).on('submit', '#login-form', function(event) {
		event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
		
		// Prevent from double click
		$('#login-btn').button('loading');
		
		// Initialize alert message 
		$('#login-form .alert-danger').text('').addClass('hidden');
		$('#login-form .input-group').removeClass('has-error');
		
		setCSRFToken();
		
		$.ajax({
			url: '/login/',
			type: 'POST',
			data: {
				'email': $('#login-form input:eq(1)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ''),
				'password': $('#login-form input:eq(2)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')
			}
		}).done(function(data) {
			// Failed to login
			if (data.state == 'fail') {
				switch (data.code) {
					case 1:
						$('#login-form .alert-danger').text('입력칸을 모두 채워주세요').removeClass('hidden');
						break;
					case 2:
						$('#login-form .alert-danger').text('휴면처리된 계정입니다. modupen@budafoo.com 으로 문의주시면 '
							+ '휴면처리된 이유에 대해 상세히 알려드리도록 하겠습니다.').removeClass('hidden');
						break;
					case 3:
						$('#login-form .alert-danger').text('Facebook 로그인을 이용하세요').removeClass('hidden');
						break;
					case 4:
						$('#login-form .alert-danger').text('비밀번호가 일치하지 않습니다').removeClass('hidden');
						$('#login-form .input-group:eq(1)').addClass('has-error');
						break;
					case 5:
						$('#login-form .alert-danger').text('존재하지 않는 메일 주소입니다').removeClass('hidden');
						$('#login-form .input-group:eq(0)').addClass('has-error');
						break;
					default:
						$('#login-form .alert-danger').text('로그인에 실패했습니다').removeClass('hidden');
						break;
				}
			}
			// Succeed to login
			else {
				// Update sidebar
				$('#sidebar-nickname').text(data.nickname);
				$('#sidebar-btn-group').addClass('hidden');
				$('.login-required').removeClass('hidden');
				
				// Update new notification count if user allowed notification
				if (data.allow_notification && data.new_notification_count > 0) {
					$('.new-notification-count').text(data.new_notification_count).removeClass('hidden');
				}
				
				// Close Modal
				$('#modal-signup').modal('hide');
			}
		}).fail(function() { 
			$('#login-form .alert-danger').text('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.')
		}).always(function() {
			// Recover button clickable
			$('#login-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
		});
	});

	// Validate sign up
	$(document).on('submit', '#signup-form', function(event) {
		event.preventDefault();
		
		// Show loading icon
    $('#loading-icon').show();
		
		// Prevent from double click
		$('#signup-btn').button('loading');
		
		// Initialize alert message 
		$('#signup-form .alert-danger').text('').addClass('hidden');
		$('#signup-form .input-group').removeClass('has-error');
		
		setCSRFToken();
		
		$.ajax({
			url: '/user/create/',
			type: 'POST',
			data: {
				'email': $('#signup-form input:eq(1)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ''),
				'nickname': $('#signup-form input:eq(2)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ''),
				'password': $('#signup-form input:eq(3)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')
			}
		}).done(function(data) {
			// Failed to signup
			if (data.state == 'fail') {
				switch (data.code) {
					case 1:
						$('#login-form .alert-danger').text('입력칸을 모두 채워주세요').removeClass('hidden');
						break;
					case 2:
						$('#signup-form .alert-danger').text('동일한 메일 주소가 존재합니다').removeClass('hidden');
						$('#signup-form .input-group:eq(0)').addClass('has-error');
						break;
					case 3:
						$('#signup-form .alert-danger').text('동일한 별명이 존재합니다').removeClass('hidden');
						$('#signup-form .input-group:eq(1)').addClass('has-error');
						break;
					default:
						$('#signup-form .alert-danger').text('회원 가입에 실패했습니다').removeClass('hidden');
						break;
				}
			}
			// Succeed to signup
			else {
				// Update sidebar
				$('#sidebar-nickname').text(data.nickname);
				$('#sidebar-btn-group').addClass('hidden');
				$('.login-required').removeClass('hidden');
				
				// Close Modal
				$('#modal-signup').modal('hide');
			}
		}).fail(function() { 
			$('#signup-form .alert-danger').text('죄송합니다. 서버가 불안정합니다. 잠시 후에 다시 시도해주세요.')
		}).always(function() {
			// Recover button clickable
			$('#signup-btn').button('reset');
			
			// Hide loading icon
			$('#loading-icon').hide();
		});
	});
	
	// Show sidebar 
	$(document).on('click', '#toggle-sidebar', function() {
		$('#sidebar').css('transform', 'translate3d(210px, 0, 0)');
		$('#transparent-background').removeClass('hidden');
		$('html, body').css('overflow-y', 'hidden');
		
		// Show tooltip message for sidebar
		setTimeout(function() {
			$('#sidebar').tooltip('enable').tooltip('show');
		}, 500); 
	});

	// Hide sidebar when user clicked transparent background
	$(document).on('click', '#transparent-background', function() {
		// Hide tooltip message for sidebar
		$('#sidebar').tooltip('hide');
		
		$('#sidebar').css('transform', 'translate3d(0, 0, 0)');
		$('#transparent-background').addClass('hidden');
		$('html, body').css('overflow-y', '');
	});

	// Change chevron direction when collapse in/out accounts page list
	$(document).on('show.bs.collapse', '#accounts-page-list', function() {
		$('#accounts-page-chevron').toggleClass('glyphicon-chevron-down glyphicon-chevron-up');
	});
	$(document).on('hide.bs.collapse', '#accounts-page-list', function() {
		$('#accounts-page-chevron').toggleClass('glyphicon-chevron-up glyphicon-chevron-down');
	});

	// Change chevron direction when collapse in/out service page list
	$(document).on('show.bs.collapse', '#service-page-list', function() {
		$('#service-page-chevron').toggleClass('glyphicon-chevron-down glyphicon-chevron-up');
	});
	$(document).on('hide.bs.collapse', '#service-page-list', function() {
		$('#service-page-chevron').toggleClass('glyphicon-chevron-up glyphicon-chevron-down');
	});

	// Move page when user submit search form
	function moveToSearchResultPage() {
		keyword = $('#story-search-form input:eq(0)').val().replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '');
		
		if (keyword == '') {
			alert('검색어를 입력해주세요');
		} else {
			if (keyword[0] == '#') {
				location.href = '/stories/search/tag/' + keyword.substr(1, keyword.length) + '/';
			} else {
				location.href = '/stories/search/title/' + keyword + '/';
			}
		}
	}
	$(document).on('submit', '#story-search-form', function(event) {
		event.preventDefault();
		moveToSearchResultPage();
	});
	$(document).on('click', '#story-search-submit-btn', function() {
		moveToSearchResultPage();
	});

	// For the user who first visited
	if (localStorage.getItem('first_visit') == null) {
		$('#modal-first-visit').modal('show');
		try {
			localStorage.setItem('first_visit', 'false');
		} catch (e) {
			void(0);
		}
	}

	// Show numeric data of service when user first visited
	$(document).on('shown.bs.modal', '#modal-first-visit', function() {
		$.ajax({
			url: '/service/numeric_data/',
			type: 'GET',
		}).done(function(data) {
			$('#total-number-of-users').text(data.totalNumberOfUsers);
			$('#total-number-of-stories').text(data.totalNumberOfStories);
		}).fail(function() {
		}).always(function() {
		});
	});

	var userAgent = window.navigator.userAgent;
  msie = userAgent.indexOf('MSIE ');

	// Activate fast-click for iPhone or iPod
	if (userAgent.indexOf('iPhone') != -1 || userAgent.indexOf('iPad') != -1) {
		FastClick.attach(document.body);
	}
	// Warn user who uses Internet Explorer lower than version 10
  else if (msie > 0 && parseInt(userAgent.substring(msie + 5, userAgent.indexOf(".", msie))) < 10) {
    $('#browser-support-warning').text('Internet Explorer 9 이하는 정식적으로 지원하지 않습니다').removeClass('hidden');
  }
	
	// Detect in-app browser
	if (userAgent.indexOf('KAKAOTALK') != -1) {
    $('#browser-support-warning').html('<strong>카카오톡 브라우저</strong>에서는 실행 속도가 느리며, '
				+ '일부 기능(이미지 첨부 등)이 정상 작동하지 않을 수 있습니다. 우측 상단 메뉴를 통해 '
				+ '<strong>다른 브라우저</strong>에서 열어보는 것을 권장합니다').removeClass('hidden');
	}
	else if (userAgent.indexOf('FBAV') != -1) {
    $('#browser-support-warning').html('<strong>페이스북 브라우저</strong>에서는 실행 속도가 느리며, '
				+ '일부 기능(이미지 첨부 등)이 정상 작동하지 않을 수 있습니다. 우측 상단 메뉴를 통해 '
				+ '<strong>다른 브라우저</strong>에서 열어보는 것을 권장합니다').removeClass('hidden');
	}

	// Scroll to top if user clicked 'back to top'
	$(document).on('click', '#back-to-top', function(event) {
		event.preventDefault();
		
		$('html, body').animate({ scrollTop: 0 }, 'fast');
	});

	// Manage announcement
	var announcementID = $('#announcement').attr('data-announcement-id');

	// Show announcement if user didn't close recent announcement
	if (localStorage.getItem('recently_closed_announcement_id') != announcementID &&
			announcementID != '0') {
		$('#announcement').removeClass('hidden');
	}
	
	// Hide announcement and do not show it again if user closed announcement
	$('#announcement').on('closed.bs.alert', function () {
		try {
			localStorage.setItem('recently_closed_announcement_id', announcementID);
		} catch (e) {
			void(0);
		}
	});

	// Manage tutorial
	if (localStorage.getItem('tutorial') != 'checked') {
		$('#tutorial').removeClass('hidden');
	}
	
	// Hide announcement and do not show it again if user closed announcement
	$('#tutorial').on('closed.bs.alert', function () {
		try {
			localStorage.setItem('tutorial', 'checked');
		} catch (e) {
			void(0);
		}
	});

	// Always show sidebar on x-large screen device
	$(window).resize(function() {
		if ($(window).width() > 1585) {
			$('#sidebar').tooltip('hide');
			$('#transparent-background').addClass('hidden');
			$('html, body').css('overflow-y', '');
			
			setTimeout(function() {
				$('#sidebar').css('transform', 'translate3d(0, 0, 0)');
			}, 500); 
		}
	});
});
