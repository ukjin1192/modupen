// Prevent CSRF token problem before sending reqeust with ajax
function setCSRFToken() {
	$.ajaxSetup({
		headers: {
			'X-CSRFToken': $.cookie('csrftoken')
		}
	});
}

// When someone finishes with the Login Button
function connectWithModupen() {
	var email, nickname, oauthUserID, authorized = false;

	// Show loading icon
	$('#loading-icon').show();
	
	FB.api('/me?fields=email,id,name,locale', function(response) {
		email = response.email;
		nickname = response.name;
		oauthUserID = response.id;
		locale = response.locale;
		
		// If user does not have email or not allowed
		if (email === undefined) email = oauthUserID + '@facebook.com';
		
		setCSRFToken();
		
		$.ajax({
			url: '/login/oauth/',
			type: 'POST',
			data: {
				'email': email,
				'nickname': nickname,
				'locale': locale,
				'platform': 'facebook',
				'oauthUserID': oauthUserID
			}
		}).done(function(data) {
			// Failed to login with Facebook OAuth
			if (data.state == 'fail') {
				switch (data.code) {
					case 1:
						$('#signup-form .alert-danger').text('Facebook 에서 정보를 받아올 수 없습니다').removeClass('hidden');
						$('#login-form .alert-danger').text('Facebook 에서 정보를 받아올 수 없습니다').removeClass('hidden');
						break;
					case 2:
						$('#signup-form .alert-danger').text('휴면처리된 계정입니다. modupen@budafoo.com 으로 문의주시면 '
							+ '휴면처리된 이유에 대해 상세히 알려드리도록 하겠습니다.').removeClass('hidden');
						$('#login-form .alert-danger').text('휴면처리된 계정입니다. modupen@budafoo.com 으로 문의주시면 '
							+ '휴면처리된 이유에 대해 상세히 알려드리도록 하겠습니다.').removeClass('hidden');
						break;
					default:
						$('#signup-form .alert-danger').text('회원 가입에 실패했습니다').removeClass('hidden');
						$('#login-form .alert-danger').text('로그인에 실패했습니다').removeClass('hidden');
						break;
				}
			}
			// Succeed to login with Facebook OAuth
			else {
				// Update sidebar
				$('#sidebar-nickname').text(data.nickname);
        $('#sidebar-btn-group').addClass('hidden');
				$('.sidebar-oauth-hidden').addClass('hidden');
        $('.login-required').removeClass('hidden');
				
				// Update new notification count if user allowed notification
        if (data.allow_notification && data.new_notification_count > 0) {
          $('.new-notification-count').text(data.new_notification_count).removeClass('hidden');
        }
				
				// Close Modal
				$('#modal-signup').modal('hide');
			}
		}).fail(function() {
		}).always(function() {
			// Hide loading icon
			$('#loading-icon').hide();
		});
	});
}

window.fbAsyncInit = function() {
	FB.init({
		appId: '897286763640067',
		cookie: true,  	// enable cookies to allow the server to access the session
		xfbml: true,  	// parse social plugins on this page
		version: 'v2.4' // use version 2.4
	});

	// Detect status change
	FB.Event.subscribe('auth.statusChange', function(response) {
		// User logged in modupen with facebook OAuth
		if (response.status === 'connected') {
			connectWithModupen();
		}
		// User deleted modupen from the facebook application list
		else if (response.status === 'not_authorized') {
		} 
		// User logged out facebook
		else {
		}
	});
};

// Load the SDK asynchronously
(function(d, s, id) {
	var js, fjs = d.getElementsByTagName(s)[0];
	if (d.getElementById(id)) return;
	js = d.createElement(s); js.id = id;
	js.src = "//connect.facebook.net/en_US/sdk.js";
	fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

// Open facebook login modal page
function facebookLogin() {
	FB.login(function() {}, {
		scope: 'email,public_profile'
	});
}
$(document).on('click', '#fb-signup-btn, #fb-login-btn', function() {
	facebookLogin();
});
