#!usr/bin/python
# -*- coding:utf-8 -*-

from binascii import b2a_hex
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db.models import Sum, Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect 
from django.views.decorators.http import require_http_methods
from main.models import Users, Identities, Stories, Tags, ClosingVotes, ClosingVoteRecords, Comments, CommentVotes, Replies, ReportRecords, Notifications, VoiceOfCustomers
from os import urandom
from random import randint, shuffle
from utils import api, cron, redis, utilities

# Variable from settings.py
LANGUAGES = getattr(settings, 'LANGUAGES')
OAUTH_SECRET_PASSWORD = getattr(settings, 'OAUTH_SECRET_PASSWORD')
FORGOT_PWD_TTL = getattr(settings, 'FORGOT_PWD_TTL')
EMAIL_VERIFICATION_TTL = getattr(settings, 'EMAIL_VERIFICATION_TTL')

STORIES_PER_QUERY = getattr(settings, 'STORIES_PER_QUERY')
COMMENTS_PER_QUERY = getattr(settings, 'COMMENTS_PER_QUERY')
REPLIES_PER_QUERY = getattr(settings, 'REPLIES_PER_QUERY')
NOTIFICATIONS_PER_QUERY = getattr(settings, 'NOTIFICATIONS_PER_QUERY')
RECOMMENDED_STORIES_PER_QUERY = getattr(settings, 'RECOMMENDED_STORIES_PER_QUERY')
BUFFER_TO_CHOOSE_POPULAR_STORIES = getattr(settings, 'BUFFER_TO_CHOOSE_POPULAR_STORIES')

MAX_TAGS_PER_STORY = getattr(settings, 'MAX_TAGS_PER_STORY')
TAG_MAX_LENGTH = getattr(settings, 'TAG_MAX_LENGTH')
MIN_COMMENTS_TO_INITIATE_CLOSING_VOTE = getattr(settings, 'MIN_COMMENTS_TO_INITIATE_CLOSING_VOTE')

TIME_INTERVAL_FOR_NEW_STORY = getattr(settings, 'TIME_INTERVAL_FOR_NEW_STORY')
TIME_INTERVAL_FOR_NEW_COMMENT = getattr(settings, 'TIME_INTERVAL_FOR_NEW_COMMENT')
TIME_INTERVAL_FOR_NEW_REPLY = getattr(settings, 'TIME_INTERVAL_FOR_NEW_REPLY')
TIME_INTERVAL_FOR_EDIT_VOTE = getattr(settings, 'TIME_INTERVAL_FOR_EDIT_VOTE')

SCORE_FOR_NEW_COMMENT = getattr(settings, 'SCORE_FOR_NEW_COMMENT')
SCORE_FOR_LIKE_COMMENT = getattr(settings, 'SCORE_FOR_LIKE_COMMENT')
SCORE_FOR_DISLIKE_COMMENT = getattr(settings, 'SCORE_FOR_DISLIKE_COMMENT')
SCORE_FOR_NEW_REPLY = getattr(settings, 'SCORE_FOR_NEW_REPLY')
SCORE_FOR_INFORMANT = getattr(settings, 'SCORE_FOR_INFORMANT')
COST_TO_VOTE_DISLIKE = getattr(settings, 'COST_TO_VOTE_DISLIKE')

MIN_LIKE_FOR_GOLD_MEDAL = getattr(settings, 'MIN_LIKE_FOR_GOLD_MEDAL')
MIN_LIKE_FOR_SILVER_MEDAL = getattr(settings, 'MIN_LIKE_FOR_SILVER_MEDAL')
MIN_LIKE_FOR_BRONZE_MEDAL = getattr(settings, 'MIN_LIKE_FOR_BRONZE_MEDAL')


@require_http_methods(['GET'])
def load_story_list_page(request):
    """
    Load story list page
    """
    return render_to_response('stories/list.html', locals(), context_instance=RequestContext(request))


@csrf_protect
@require_http_methods(['POST'])
def user_login(request):
    """
    User login
    Parameter: email, password
    """
    if all(x in request.POST for x in ['email', 'password']):
        email = request.POST['email']
        password = request.POST['password']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Email and password parameters are required.' 
        }) 

    u = authenticate(email=email, password=password)

    if u:
        if u.is_active == False:
            return JsonResponse({
                'state': 'fail', 
                'code': 2,
                'msg': 'Account is not active.'
            })
        else:
            login(request, u)
            
            return JsonResponse({
                'state': 'success', 
                'code': 1,
                'msg': 'Succeed to login.',
                'nickname': u.nickname,
                'allow_notification': u.allow_notification,
                'new_notification_count': u.new_notification_count
            }) 
    else:
        if Users.objects.filter(email=email).count() > 0:
            if Users.objects.filter(email=email)[0].login_with_oauth == True:
                return JsonResponse({
                    'state': 'fail', 
                    'code': 3,
                    'msg': 'Please login with OAuth.'
                })
            else:
                return JsonResponse({
                    'state': 'fail', 
                    'code': 4,
                    'msg': 'Password not matching.'
                })
        else:
            return JsonResponse({
                'state': 'fail', 
                'code': 5,
                'msg': 'User does not exist.'
            })


@csrf_protect
@require_http_methods(['POST'])
def user_login_with_oauth(request):
    """
    User login with OAuth
    Create user and identity object together if user does not exist
    Parameter: email, nickname, locale, platform, oauth_user_id
    """
    if all(x in request.POST for x in ['email', 'nickname', 'locale', 'platform', 'oauthUserID']):
        email = request.POST['email']
        nickname = request.POST['nickname']
        locale = request.POST['locale']
        platform = request.POST['platform']
        oauth_user_id = request.POST['oauthUserID']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Email, nickname, locale, platform and OAuth user ID parameters are required.' 
        }) 

    if platform not in [choice[0] for choice in Identities.platform_choices]:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Not valid platform.' 
        }) 

    # User login with OAuth
    try:
        identity = Identities.objects.get(oauth_user_id=str(oauth_user_id))
        
        u = authenticate(email=identity.user.email, password=OAUTH_SECRET_PASSWORD)
        
        if u.is_active == False:
            return JsonResponse({
                'state': 'fail', 
                'code': 3,
                'msg': 'Account is not active.'
            })
        else:
            login(request, u)
            
            return JsonResponse({
                'state': 'success', 
                'code': 1,
                'msg': 'Succeed to login with OAuth.',
                'nickname': u.nickname,
                'allow_notification': u.allow_notification,
                'new_notification_count': u.new_notification_count
            }) 
    except:
        # Connect OAuth with original account if user already verified email
        if Users.objects.filter(email=email, email_verified=True).count() > 0:
            user = Users.objects.get(email=email, email_verified=True)
            user.login_with_oauth = True
            user.save()
            
            # Create identity object
            Identities(
                user = user,
                platform = platform,
                oauth_user_id = oauth_user_id
            ).save()
            
            user.set_password(OAUTH_SECRET_PASSWORD)
            user.save()
            
            u = authenticate(email=user.email, password=OAUTH_SECRET_PASSWORD)
            
            # Session would be deleted after password changing
            login(request, u)
            
            return JsonResponse({
                'state': 'success', 
                'code': 2,
                'msg': 'Succeed to connect original account with OAuth.',
                'nickname': u.nickname,
                'allow_notification': u.allow_notification,
                'new_notification_count': u.new_notification_count
            }) 
            
        # Prevent from email overlap
        temp = 1
        email_overlapped = False
        while Users.objects.filter(email=email).count() > 0:
            email = email.split('@')[0] + str(temp) + '@' + email.split('@')[1]
            email_overlapped = True
        
        # Prevent from nickname overlap
        temp = 1
        while Users.objects.filter(nickname=nickname).count() > 0:
            nickname += str(temp)
        
        # Create user object
        user = Users.objects.create_user(email, OAUTH_SECRET_PASSWORD)
        user.nickname = nickname
        # TODO user.language = utilities.get_language_iso_code(locale)
        user.login_with_oauth = True
        
        if '@facebook.com' not in email and email_overlapped == False:
            user.email_verified = True
        
        user.save()
        
        # Create identity object
        Identities(
            user = user,
            platform = platform,
            oauth_user_id = oauth_user_id
        ).save()
        
        u = authenticate(email=email, password=OAUTH_SECRET_PASSWORD)
        login(request, u)
        
        if user.email_verified == False and '@facebook.com' not in email:
            # Randomly created 30 digit hex string
            secret_code = b2a_hex(urandom(15))
            
            # Matching secret code with user ID
            cache.set(secret_code, str(user.id), timeout=EMAIL_VERIFICATION_TTL)
            
            # Asynchronously send mail
            cron.send_mail_with_template.apply_async(
                args=[
                    '[모두펜] 환영해요, ' + user.nickname + '님!',
                    'email/email_verification.html',
                    'modupen@budafoo.com',
                    user.email
                ],
                kwargs={
                    'nickname': user.nickname,
                    'secret_code': secret_code
                }
            )
        
        return JsonResponse({
            'state': 'success', 
            'code': 3,
            'msg': 'Succeed to sign up with OAuth.',
            'nickname': u.nickname
        }) 


@login_required
@require_http_methods(['GET'])
def user_logout(request):
    """
    User logout
    """
    logout(request)

    return HttpResponseRedirect('/')


@csrf_protect
@require_http_methods(['POST'])
def user_signup(request):
    """
    User signup
    Parameter: email, nickname, password
    """
    if all(x in request.POST for x in ['email', 'nickname', 'password']):
        email = request.POST['email']
        nickname = request.POST['nickname']
        password = request.POST['password']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Email, nickname and password parameters are required.'
        }) 

    if Users.objects.filter(email=email).count() > 0:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Email overlapped. Try oauth login.'
        }) 
    elif Users.objects.filter(nickname=nickname).count() > 0:
        return JsonResponse({
            'state': 'fail',
            'code': 3,
            'msg': 'Nickname overlapped'
        }) 
    else:
        user = Users.objects.create_user(email, password)
        user.nickname = nickname
        # TODO user.language = request.POST['language']
        user.save()
        
        u = authenticate(email=email, password=password)
        login(request, u)
        
        # Randomly created 30 digit hex string
        secret_code = b2a_hex(urandom(15))
        
        # Matching secret code with user ID
        cache.set(secret_code, str(user.id), timeout=EMAIL_VERIFICATION_TTL)
        
        # Asynchronously send mail
        cron.send_mail_with_template.apply_async(
            args=[
                '[모두펜] 환영해요, ' + user.nickname + '님!',
                'email/email_verification.html',
                'modupen@budafoo.com',
                user.email
            ],
            kwargs={
                'nickname': user.nickname,
                'secret_code': secret_code
            }
        )
        
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to sign up.',
            'nickname': u.nickname
        }) 


@login_required
@require_http_methods(['GET'])
def load_update_user_email_page(request):
    """
    Load update user email page
    """
    if request.user.login_with_oauth == True:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'OAuth logged in user cannot change email.'
        }) 

    return render_to_response('accounts/update_user_email.html', locals(), context_instance=RequestContext(request))


@csrf_protect
@login_required
@require_http_methods(['POST'])
def update_user_email(request):
    """
    Update email field of user object
    Parameter: email
    """
    if all(x in request.POST for x in ['email']):
        email = request.POST['email']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Email parameter is required.'
        }) 

    if request.user.login_with_oauth == True:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'OAuth logged in user cannot change email.'
        }) 

    if Users.objects.filter(email=email).count() > 0:
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Email overlapped.', 
        }) 
    else:
        user = request.user
        user.email = email
        user.email_verified = False
        user.save()
        
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to change email.'
        })


@login_required
@csrf_protect
@require_http_methods(['POST'])
def send_verification_email(request):
    """
    Send verification email
    """
    # Randomly created 30 digit hex string
    secret_code = b2a_hex(urandom(15))
    
    # Matching secret code with user ID
    cache.set(secret_code, str(request.user.id), timeout=EMAIL_VERIFICATION_TTL)
    
    # Asynchronously send mail
    cron.send_mail_with_template.apply_async(
        args=[
            '[모두펜] 메일 주소 인증',
            'email/email_verification.html',
            'modupen@budafoo.com',
            request.user.email
        ],
        kwargs={
            'nickname': request.user.nickname,
            'secret_code': secret_code
        }
    )

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to send verification email.'
    })


@require_http_methods(['GET'])
def verify_user_email(request, secret_code):
    """
    Verifiy user email
    Parameter: secret code
    """
    user_id = cache.get(secret_code)
    cache.delete(secret_code)

    # Secret code does not exist
    if user_id == None:
        succeed = False

    try:
        user = Users.objects.get(id=int(user_id))
        user.email_verified = True
        user.save()
        
        succeed = True
    # User does not exist
    except:
        succeed = False

    return render_to_response('accounts/email_verification.html', locals(), context_instance=RequestContext(request))


@login_required
@require_http_methods(['GET'])
def load_update_user_nickname_page(request):
    """
    Load update user nickname page
    """
    return render_to_response('accounts/update_user_nickname.html', locals(), context_instance=RequestContext(request))


@csrf_protect
@login_required
@require_http_methods(['POST'])
def update_user_nickname(request):
    """
    Update nickname field of user object
    Parameter: nickname
    """
    if all(x in request.POST for x in ['nickname']):
        nickname = request.POST['nickname']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Nickname parameter is required.'
        }) 

    if Users.objects.filter(nickname=nickname).count() > 0:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Nickname overlapped.'
        }) 
    else:
        user = request.user
        user.nickname = nickname
        user.save()
       
        # Asynchronously update cache of stories, comments and replies that user wrote
        cron.update_nickname_of_user_wrote_contents_cache.apply_async(args=[user])
        
        return JsonResponse({
            'state': 'success',
            'code': 1,
            'msg': 'Succeed to change nickname.'
        }) 


@login_required
@require_http_methods(['GET'])
def load_update_user_language_page(request):
    """
    Load update user language page
    """
    return render_to_response('accounts/update_user_language.html', locals(), context_instance=RequestContext(request))


@csrf_protect
@login_required
@require_http_methods(['POST'])
def update_user_language(request):
    """
    Update language field of user object
    Parameter: language
    """
    if all(x in request.POST for x in ['language']):
        language = request.POST['language']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Language parameter is required.'
        }) 

    if language not in [choice[0] for choice in LANGUAGES]:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Not proper language ISO code.'
        }) 

    user = request.user
    user.language = language
    user.save()

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to change password.'
    }) 


@login_required
@require_http_methods(['GET'])
def load_update_user_password_page(request):
    """
    Load update user password page
    """
    if request.user.login_with_oauth == True:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'OAuth logged in user cannot change password.'
        }) 

    return render_to_response('accounts/update_user_password.html', locals(), context_instance=RequestContext(request))


@csrf_protect
@login_required
@require_http_methods(['POST'])
def update_user_password(request):
    """
    Update password field of user object
    Parameter: original password, new password
    """
    if all(x in request.POST for x in ['originalPassword', 'newPassword']):
        original_password = request.POST['originalPassword']
        new_password = request.POST['newPassword']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Original password and new password parameters are required.'
        }) 

    if request.user.login_with_oauth == True:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'OAuth logged in user cannot change password.'
        }) 

    u = authenticate(email=request.user.email, password=original_password)

    if not u:
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Password not matching.' 
        }) 
    else:
        u.set_password(new_password)
        u.save()
        
        # Session would be deleted after password changing
        login(request, u)
        
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to change password.'
        }) 


@require_http_methods(['GET'])
def load_forgot_password_page(request):
    """
    Load forgot password page
    """
    return render_to_response('accounts/forgot_password.html', locals(), context_instance=RequestContext(request))


@csrf_protect
@require_http_methods(['POST'])
def send_secret_code_with_email(request):
    """
    Send secret code to user's email if user is active
    Secret code is volatile and saved in In-memory cache
    """
    if all(x in request.POST for x in ['email']):
        email = request.POST['email']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Email parameter is required.'
        }) 

    try:
        user = Users.objects.get(email=email)
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'User does not exist.' 
        }) 

    if user.is_active == False:
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Account is not active.' 
        }) 

    if user.login_with_oauth == True:
        return JsonResponse({
            'state': 'fail', 
            'code': 4,
            'msg': 'Try OAuth login.' 
        }) 

    # Randomly created 30 digit hex string
    secret_code = b2a_hex(urandom(15))
    
    # Matching secret code with user ID
    cache.set(secret_code, str(user.id), timeout=FORGOT_PWD_TTL)

    # Asynchronously send mail
    cron.send_mail_with_template.apply_async(
        args=[
            '[모두펜] ' + user.nickname + '님 비밀번호를 잊으셨나요?',
            'email/forgot_password.html',
            'modupen@budafoo.com',
            user.email
        ],
        kwargs={
            'nickname': user.nickname,
            'secret_code': secret_code
        }
    )
    
    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to send secret code with email.'
    }) 


@require_http_methods(['GET'])
def issue_temporary_password(request, secret_code):
    """
    Issue temporary password to proper user with the secret code
    Parameter: secret code
    """
    user_id = cache.get(secret_code)
    cache.delete(secret_code)

    # Secret code does not exist
    if user_id == None:
        succeed = False

    try:
        user = Users.objects.get(id=int(user_id))
        # Randomly created 10 digit hex string
        temporary_password = b2a_hex(urandom(5))
        user.set_password(str(temporary_password))
        # Verify email
        user.email_verified = True
        user.save()
        
        u = authenticate(email=user.email, password=temporary_password)
        
        # Session would be deleted after password changing
        login(request, u)
        
        succeed = True
    # User does not exist
    except:
        succeed = False

    return render_to_response('accounts/temporary_password.html', locals(), context_instance=RequestContext(request))


@csrf_protect
@login_required
@require_http_methods(['POST'])
def update_notification_setting_of_user(request):
    """
    Update notification setting of user
    Parameter: setting
    """
    if all(x in request.POST for x in ['setting']):
        setting = request.POST['setting']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Setting parameter is required.'
        }) 

    user = request.user

    if setting == 'false':
        user.allow_notification = False
        user.save()
    else:
        user.allow_notification = True
        user.save()

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to update notification setting of user.'
    }) 


@login_required
@require_http_methods(['GET'])
def load_dropout_user_page(request):
    """
    Load dropout user page
    """
    return render_to_response('accounts/dropout_user.html', locals(), context_instance=RequestContext(request))


@csrf_protect
@login_required
@require_http_methods(['POST'])
def dropout_user(request):
    """
    Dropout user
    (1) Do not delete user object
    (2) Changes its email, nickname and password to maintain data
    """
    if all(x in request.POST for x in ['password']):
        password = request.POST['password']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Password parameter is required.'
        }) 

    u = authenticate(email=request.user.email, password=password)

    if not u:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Password not matching.' 
        }) 

    # Change its nickname and email
    temp_user_nickname = 'user' + str(randint(100000, 999999))
    while Users.objects.filter(nickname=temp_user_nickname).count() > 0 and \
        Users.objects.filter(email=temp_user_nickname + '@dropout.com').count() > 0:
        temp_user_nickname = 'user' + str(randint(100000, 999999))
    
    user = request.user
    user.nickname = temp_user_nickname
    user.email = temp_user_nickname + '@dropout.com'
    user.email_verified = False
    user.is_active = False
    user.save()
    
    # Change password with randomly created 10 digit hex string
    temporary_password = b2a_hex(urandom(5))
    user.set_password(str(temporary_password))
    user.save()
    
    # Delete sessions
    for s in Session.objects.all():
        if s.get_decoded().get('_auth_user_id') == user.id:
            s.delete()   

    # Asynchronously update cache of stories, comments and replies that user wrote
    cron.update_nickname_of_user_wrote_contents_cache.apply_async(args=[user])
    
    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to dropout user.'
    }) 


@login_required
@user_passes_test(lambda u: u.is_admin)
@require_http_methods(['POST'])
def deactivate_user(request):
    """
    Deacitvate user
    Parameter: user ID
    """
    if all(x in request.POST for x in ['userID']):
        user_id = request.POST['userID']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'User ID parameter is required.'
        }) 

    try:
        user = Users.objects.get(id=int(user_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'User does not exist.'
        }) 

    user.is_active = False
    user.save()

    # Delete sessions
    for s in Session.objects.all():
        if s.get_decoded().get('_auth_user_id') == user.id:
            s.delete()   

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to deactivate user.'
    }) 


@login_required
@require_http_methods(['GET'])
def load_user_contributed_story_list_page(request):
    """
    Load user contributed story list page
    """
    return render_to_response('stories/user_contributed.html', locals(), context_instance=RequestContext(request))


@login_required
@require_http_methods(['GET'])
def get_user_contributed_stories(request, pagination):
    """
    Get user contributed stories
    Parameter: pagination
    """
    if pagination.isdigit() == False:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Pagination should be the positive interger.'
        }) 

    story_id_list = api.get_id_list_of_user_contributed_stories(request.user, int(pagination))

    stories = utilities.get_stories_from_story_id_list(story_id_list)

    if len(stories) == STORIES_PER_QUERY:
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to get user contributed stories. There are more stories.',
            'stories': stories
        })
    else:
        return JsonResponse({
            'state': 'success', 
            'code': 2,
            'msg': 'Succeed to get user contributed stories. There is no more story.',
            'stories': stories
        })


@login_required
@require_http_methods(['GET'])
def load_user_wrote_comment_list_page(request):
    """
    Load user wrote comment list page
    """
    return render_to_response('comments/user_wrote.html', locals(), context_instance=RequestContext(request))


@login_required
@require_http_methods(['GET'])
def get_user_wrote_comments(request, pagination):
    """
    Get user wrote comments
    Parameter: pagination, (optional) last comment ID
    """
    if pagination.isdigit() == False:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Pagination should be the positive interger.'
        }) 

    if 'lastCommentID' in request.GET:
        last_comment_id = int(request.GET['lastCommentID'])
        comment_id_list = api.get_id_list_of_user_wrote_comments(
            request.user, 
            int(pagination), 
            last_comment_id
        )
    else:
        comment_id_list = api.get_id_list_of_user_wrote_comments(
            request.user, 
            int(pagination), 
            None
        )

    comments = utilities.get_comments_from_comment_id_list(comment_id_list)

    if len(comments) == COMMENTS_PER_QUERY:
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to get user wrote comments. There are more comments.',
            'comments': comments
        })
    else:
        return JsonResponse({
            'state': 'success', 
            'code': 2,
            'msg': 'Succeed to get user wrote comments. There is no more comment.',
            'comments': comments
        })


@login_required
@require_http_methods(['GET'])
def load_user_wrote_reply_list_page(request):
    """
    Load user wrote reply list page
    """
    return render_to_response('replies/user_wrote.html', locals(), context_instance=RequestContext(request))


@login_required
@require_http_methods(['GET'])
def get_user_wrote_replies(request, pagination):
    """
    Get user wrote replies
    Parameter: pagination, (optional) last reply ID
    """
    if pagination.isdigit() == False:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Pagination should be the positive interger.'
        }) 

    if 'lastReplyID' in request.GET:
        last_reply_id = int(request.GET['lastReplyID'])
        reply_id_list = api.get_id_list_of_user_wrote_replies(
            request.user, 
            int(pagination), 
            last_reply_id
        )
    else:
        reply_id_list = api.get_id_list_of_user_wrote_replies(
            request.user, 
            int(pagination), 
            None
        )

    replies = utilities.get_replies_from_reply_id_list(reply_id_list)

    if len(replies) == REPLIES_PER_QUERY:
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to get user wrote replies. There are more replies.',
            'replies': replies
        })
    else:
        return JsonResponse({
            'state': 'success', 
            'code': 2,
            'msg': 'Succeed to get user wrote replies. There is no more reply.',
            'replies': replies
        })


@login_required
@user_passes_test(lambda u: u.is_admin)
@require_http_methods(['POST'])
def give_reward_point_to_informant(request):
    """
    Give reward point to informant
    Parameter: user ID
    """
    if all(x in request.POST for x in ['userID']):
        user_id = request.POST['userID']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'User ID parameter is required.'
        })

    try:
        user = Users.objects.get(id=int(user_id))
        user.score += SCORE_FOR_INFORMANT
        user.save()
        
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to give reward point to informant.'
        })
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'User does not exist.'
        })


@require_http_methods(['GET'])
def get_score_of_users(request):
    """
    Get score of users in user ID list
    Parameter: user ID list
    """
    if all(x in request.GET for x in ['userIDList']):
        raw_user_id_list = request.GET['userIDList']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'User ID list parameter is required.'
        }) 

    user_id_list = []

    for raw_user_id in raw_user_id_list.split(','):
        if raw_user_id.strip().isdigit():
            user_id_list.append(int(raw_user_id.strip()))

    users = list(Users.objects.filter(id__in=user_id_list).\
        values('id', 'score', 'gold_medal', 'silver_medal', 'bronze_medal'))

    scores = {}
    gold_medals = {}
    silver_medals = {}
    bronze_medals = {}
    
    for user_id in user_id_list:
        scores[user_id] = filter(lambda user: user['id'] == user_id, users)[0]['score']
        gold_medals[user_id] = filter(lambda user: user['id'] == user_id, users)[0]['gold_medal']
        silver_medals[user_id] = filter(lambda user: user['id'] == user_id, users)[0]['silver_medal']
        bronze_medals[user_id] = filter(lambda user: user['id'] == user_id, users)[0]['bronze_medal']

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to get score of users.',
        'scores': scores,
        'gold_medals': gold_medals,
        'silver_medals': silver_medals,
        'bronze_medals': bronze_medals
    })


@csrf_exempt
@require_http_methods(['POST'])
def dropout_user_signed_up_with_facebook(request):
    """
    Dropout user signed up with Facebook
    (1) Delete identity object
    (2) Do not delete user object
    (3) changes its email, nickname and password to keep story related data
    (4) Deauthorize callback URL: Facebook developer > App dashboard > Settings > Advanced
    Parameter: signed request
    """
    if all(x in request.POST for x in ['signed_request']):
        signed_request = request.POST['signed_request']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Signed request parameter is required.'
        }) 

    data = utilities.parse_facebook_signed_request(signed_request)

    try:
        identity = Identities.objects.get(oauth_user_id=str(data['user_id']))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Identity does not exist' 
        }) 

    user = identity.user
    
    # Delete identity object
    identity.delete()
    
    # Change its nickname and email
    temp_user_nickname = 'user' + str(randint(100000, 999999))
    while Users.objects.filter(nickname=temp_user_nickname).count() == 1:
        temp_user_nickname = 'user' + str(randint(100000, 999999))
    
    user.nickname = temp_user_nickname
    user.email = temp_user_nickname + '@dropout.com'
    user.email_verified = False
    user.is_active = False
    user.save()
    
    # Change password with randomly created 10 digit hex string
    temporary_password = b2a_hex(urandom(5))
    user.set_password(str(temporary_password))
    user.save()
    
    # Delete sessions
    for s in Session.objects.all():
        if s.get_decoded().get('_auth_user_id') == user.id:
            s.delete()   

    # Asynchronously update cache of stories, comments and replies that user wrote
    cron.update_nickname_of_user_wrote_contents_cache.apply_async(args=[user])
    
    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to dropout user signed up with facebook.'
    }) 


@require_http_methods(['GET'])
def load_new_story_page(request):
    """
    Load new story page
    """
    return render_to_response('stories/new.html', locals(), context_instance=RequestContext(request))


@csrf_protect
@require_http_methods(['POST'])
def create_story(request):
    """
    Create story object and the first comment object
    Parameter: title, context, (optional) tags, image, image reference, image position
    """
    if all(x in request.POST for x in ['title', 'context']):
        title = request.POST['title']
        context = request.POST['context']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Title, context parameters are required.'
        }) 

    if not request.user.is_authenticated():
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Login is required to create story.'
        }) 

    try:
        last_own_story = Stories.objects.filter(author=request.user)[0]
        
        if last_own_story.created_at > timezone.now() - timedelta(minutes=TIME_INTERVAL_FOR_NEW_STORY):
            return JsonResponse({
                'state': 'fail', 
                'code': 3,
                'msg': 'Caught from the time interval limit.'
            })
    except:
        pass

    # Create story object
    story = Stories(
        author=request.user, 
        language=request.user.language, 
        title=title,
        updated_at=timezone.now()
    )
    story.save()

    if 'tags' in request.POST and request.POST['tags'] != '':
        tags = request.POST['tags'].split(',')
        
        count = 1
        for tag in tags:
            if count > MAX_TAGS_PER_STORY:
                break
            
            tag = tag.replace(' ', '').lower()
            if len(tag) > TAG_MAX_LENGTH:
                tag = tag[0: TAG_MAX_LENGTH]
            
            try:
                story_tag = Tags.objects.get(keyword=tag)
                story_tag.count += 1
                story_tag.save()
                
                story.tags.add(story_tag)
            except:
                story_tag = Tags(keyword=tag, count=1)
                story_tag.save()
                
                story.tags.add(story_tag)
            
            count +=1

    # Save image to Cloudinary if image exist
    image_url = ''
    if 'image' in request.FILES:
        image_url = utilities.upload_image_to_cloudinary(request.FILES['image'])

    if image_url != '':
        has_image = True
    else:
        has_image = False

    if 'imageReference' in request.POST:
        image_reference = request.POST['imageReference']
    else:
        image_reference = ''

    if 'imagePosition' in request.POST:
        if request.POST['imagePosition'] == 'up':
            image_position = True
        else:
            image_position = False
    else:
        image_position = False

    # Create the first comment object
    comment = Comments(
        story=story, 
        author=request.user, 
        order=1, 
        context=context, 
        has_image=has_image,
        image_url=image_url,
        image_reference=image_reference,
        image_position=image_position
    )
    comment.save()

    # Add user to story contributor
    story.contributors.add(request.user)

    api.add_number_to_user_score(comment.author, SCORE_FOR_NEW_COMMENT)

    # Update Firebase DB
    utilities.update_firebase_database(
        '/story/' + str(story.id) + '/', 
        'last_comment_order', 
        1
    )
    utilities.update_firebase_database(
        '/story/' + str(story.id) + '/comment/' + str(comment.id) + '/', 
        'last_reply_order', 
        0
    )

    redis.update_story_cache(story.id)
    redis.update_comment_cache(comment.id)

    return JsonResponse({
        'state': 'success',
        'code': 1,
        'msg': 'Succeed to create story object.', 
        'storyID': story.id
    })


@login_required
@require_http_methods(['GET'])
def load_user_favorite_story_list_page(request):
    """
    Load favorite story list page
    """
    return render_to_response('stories/favorite.html', locals(), context_instance=RequestContext(request))


@login_required
@require_http_methods(['GET'])
def get_user_favorite_stories(request, pagination):
    """
    Get user favorite stories at specific pagination
    parameter: pagination
    """
    if pagination.isdigit() == False:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Pagination should be the positive interger.'
        }) 

    story_id_list = api.get_id_list_of_user_favorite_stories(
        request.user, 
        int(pagination) 
    )

    stories = utilities.get_stories_from_story_id_list(story_id_list)

    if len(stories) == STORIES_PER_QUERY:
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to get user favorite stories. There are more stories.',
            'stories': stories
        })
    else:
        return JsonResponse({
            'state': 'success', 
            'code': 2,
            'msg': 'Succeed to get user favorite stories. There is no more story.',
            'stories': stories
        })


@require_http_methods(['GET'])
def add_story_to_favorite_story_list(request, story_id):
    """
    Add story to favorite story list
    parameter: story ID
    """
    if not request.user.is_authenticated():
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Login is required to add story to favorite story list.' 
        }) 

    try:
        story = api.get_story_object(int(story_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Story does not exist.'
        })
    
    user = request.user
    
    if story not in user.favorites.all(): 
        user.favorites.add(story)
        
        api.increase_favorites_count_of_story(story)
        
        redis.update_story_cache(story.id, 'favorites_count', story.favorites_count)
        
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to add story to favorite story list.'
        }) 
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Story is already in favorite story list.'
        }) 


@login_required
@require_http_methods(['GET'])
def remove_whole_story_from_favorite_story_list(request):
    """
    Remove whole story from favorite story list
    """
    user = request.user
    
    for story in user.favorites.all():
        user.favorites.remove(story)
        
        api.decrease_favorites_count_of_story(story)
        
        redis.update_story_cache(story.id, 'favorites_count', story.favorites_count)
    
    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to remove whole story from favorite story list.'
    }) 


@login_required
@require_http_methods(['GET'])
def remove_story_from_favorite_story_list(request, story_id):
    """
    Remove story from favorite story list
    Parameter: story ID
    """
    try:
        story = api.get_story_object(int(story_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Story does not exist.'
        })

    user = request.user

    if story in user.favorites.all():
        user.favorites.remove(story)
         
        api.decrease_favorites_count_of_story(story)
        
        redis.update_story_cache(story.id, 'favorites_count', story.favorites_count)
        
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to remove story from favorite story list.'
        }) 
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Story is not in favorite story list.'
        }) 


@require_http_methods(['GET'])
def load_read_story_list_page(request):
    """
    Load read story list page
    """
    return render_to_response('stories/read.html', locals(), context_instance=RequestContext(request))


@require_http_methods(['GET'])
def load_story_detail_page(request, story_id):
    """
    Load story detail page 
    Parameter: story ID
    """
    story = cache.get('story:' + str(story_id))

    if story == None:
        story = redis.update_story_cache(int(story_id))

    if story == None:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Story does not exist.'
        })

    if story['state'] == 'deleted':
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Story is deleted.' 
        })

    story_hits = cache.get('story:' + str(story_id) + ':hits')

    if story_hits == None:
        story_hits = redis.update_hits_value_cache(int(story_id))
  
    story['hits'] += int(story_hits)

    # Check story is included in user's favorite list if user logged in
    if request.user.is_authenticated() and \
        request.user.favorites.filter(id=int(story_id)).count() > 0:
        favorite = True
    else:
        favorite = False

    redis.increase_hits_value_cache(int(story_id))

    # Check if closing vote is opened
    if story['closing_vote_opened'] == True:
        closing_vote_process = True
        closing_vote = ClosingVotes.objects.filter(story__id=int(story['id']), closed=False)[0]
        agreement_ratio = utilities.get_percentage_value(
            closing_vote.agreement_count, closing_vote.disagreement_count)
        disagreement_ratio = 100 - agreement_ratio
        
        try:
            closing_vote_record = ClosingVoteRecords.objects.get(closing_vote=closing_vote, voter=request.user)
        except:
            pass
    else:
        closing_vote_process = False

    return render_to_response('stories/main.html', locals(), context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.is_admin)
@require_http_methods(['POST'])
def close_story(request, story_id):
    """
    Close story (Update story state as closed)
    """
    try:
        story = api.get_story_object(int(story_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Story does not exist.'
        }) 

    story.state = 'closed'
    story.save()

    redis.update_story_cache(story.id, 'state', 'closed')

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to close story.'
    }) 


@login_required
@user_passes_test(lambda u: u.is_admin)
@require_http_methods(['POST'])
def delete_story(request, story_id):
    """
    Delete story (Update story state as deleted)
    """
    try:
        story = api.get_story_object(int(story_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Story does not exist.'
        }) 

    story.state = 'deleted'
    story.save()

    redis.update_story_cache(story.id, 'state', 'deleted')

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to delete story.'
    }) 


@require_http_methods(['GET'])
def check_whether_user_contributed_story_or_not(request, story_id):
    """
    Check whether user contributed story or not
    Parameter: story ID
    """
    if request.user.is_authenticated():
        try:
            story = api.get_story_object(int(story_id))
            
            if request.user in story.contributors.all():
                return JsonResponse({
                    'state': 'success', 
                    'code': 1,
                    'msg': 'User contributed story.'
                }) 
            else:
                return JsonResponse({
                    'state': 'fail', 
                    'code': 1,
                    'msg': 'User does not contributed story yet.'
                }) 
        except:
            return JsonResponse({
                'state': 'fail', 
                'code': 2,
                'msg': 'Story does not exist.'
            }) 
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'User not logged in.'
        }) 


@login_required
@user_passes_test(lambda u: u.is_admin)
@require_http_methods(['POST'])
def update_story_cache(request, story_id):
    """
    Update story cache
    """
    try:
        redis.update_story_cache(story_id)
        
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to update story cache.'
        }) 
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Story does not exist.'
        }) 


@require_http_methods(['GET'])
def get_stories_with_options(request):
    """
    Get stories with options at specific pagination
    Parameter: filter option, sorting option, pagination, (optional) last story ID 
    """
    if all(x in request.GET for x in ['filterOption', 'sortingOption', 'pagination']):
        filter_option = request.GET['filterOption']
        sorting_option = request.GET['sortingOption']
        pagination = request.GET['pagination']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Filter option, sorting option and pagination parameters are required.'
        }) 

    if filter_option not in ['processing', 'closed']:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Filter option is not valid.'
        }) 

    if sorting_option not in ['updated_at', 'created_at', 'hits', 'favorites']:
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Sorting option is not valid.'
        }) 

    if pagination.isdigit() == False:
        return JsonResponse({
            'state': 'fail', 
            'code': 4,
            'msg': 'Pagination should be the positive interger.'
        }) 

    if request.user.is_authenticated():
        language_iso_code = request.user.language
    else:
        # TODO language_string = request.LANGUAGE_CODE
        # language_iso_code = utilities.get_language_iso_code(language_string)
        language_iso_code = 'ko'

    if 'lastStoryID' in request.GET:
        last_story_id = int(request.GET['lastStoryID'])
        story_id_list = api.get_id_list_of_stories(
            language_iso_code,
            str(filter_option), 
            str(sorting_option), 
            int(pagination),
            last_story_id
        )
    else:
        story_id_list = api.get_id_list_of_stories(
            language_iso_code,
            str(filter_option), 
            str(sorting_option), 
            int(pagination),
            None
        )

    stories = utilities.get_stories_from_story_id_list(story_id_list)

    if len(stories) == STORIES_PER_QUERY:
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to get stories with options. There are more stories.',
            'stories': stories
        })
    else:
        return JsonResponse({
            'state': 'success', 
            'code': 2,
            'msg': 'Succeed to get stories with options. There is no more story.',
            'stories': stories
        })


@require_http_methods(['GET'])
def get_stories_from_the_story_id_list(request):
    """
    Get stories from the story ID list
    Parameter: story ID list
    """
    if all(x in request.GET for x in ['storyIDList']):
        raw_story_id_list = str(request.GET['storyIDList'])
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Story ID list parameter is required.'
        }) 

    story_id_list = []

    for raw_story_id in raw_story_id_list.split(','):
        if raw_story_id.strip().isdigit():
            story_id_list.append(int(raw_story_id.strip()))

    stories = utilities.get_stories_from_story_id_list(story_id_list)

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to get stories from the story ID list',
        'stories': stories
    })


@require_http_methods(['GET'])
def get_recommended_stories(request):
    """
    Get recommended stories
        1. Recently created stories among processing stories
        2. Popular stories among processing stories
        3. Randomly picked stories among closed stories
    """
    recent_stories = list(Stories.objects.order_by('-id').exclude(state='deleted')\
        [0:RECOMMENDED_STORIES_PER_QUERY].values_list('id', 'title'))

    popular_stories = list(Stories.objects.filter(state='processing').\
        order_by('-hits')[0:BUFFER_TO_CHOOSE_POPULAR_STORIES].values_list('id', 'title'))
    shuffle(popular_stories)
    popular_stories = popular_stories[0:RECOMMENDED_STORIES_PER_QUERY]

    closed_stories = list(Stories.objects.filter(state='closed').order_by('?')\
        [0:RECOMMENDED_STORIES_PER_QUERY].values_list('id', 'title'))

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to get recommended stories',
        'recent_stories': recent_stories,
        'popular_stories': popular_stories,
        'closed_stories': closed_stories
    })


@require_http_methods(['GET'])
def load_story_list_page_searched_by_title(request, title):
    """
    Load story list page searched by title
    Parameter: title
    """
    return render_to_response('stories/search_by_title.html', locals(), context_instance=RequestContext(request))


@require_http_methods(['GET'])
def get_stories_searched_by_title(request, title, pagination):
    """
    Get searched stories at specific pagination
    Parameter: title, pagination, (optional) last story ID
    """
    if pagination.isdigit() == False:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Pagination should be the positive interger.'
        }) 

    if 'lastStoryID' in request.GET:
        last_story_id = int(request.GET['lastStoryID'])
        story_id_list = api.get_id_list_of_stories_searched_by_title(
            title, 
            int(pagination), 
            last_story_id
        )
    else:
        story_id_list = api.get_id_list_of_stories_searched_by_title(
            title, 
            int(pagination), 
            None
        )

    stories = utilities.get_stories_from_story_id_list(story_id_list)

    if len(stories) == STORIES_PER_QUERY:
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to get searched stories. There are more stories.',
            'stories': stories
        })
    else:
        return JsonResponse({
            'state': 'success', 
            'code': 2,
            'msg': 'Succeed to get searched stories. There is no more story.',
            'stories': stories
        })


@require_http_methods(['GET'])
def load_story_list_page_searched_by_tag(request, tag):
    """
    Load story list page searched by tag
    Parameter: tag
    """
    return render_to_response('stories/search_by_tag.html', locals(), context_instance=RequestContext(request))


@require_http_methods(['GET'])
def get_stories_searched_by_tag(request, tag, pagination):
    """
    Get searched stories at specific pagination
    Parameter: tag, pagination, (optional) last story ID
    """
    if pagination.isdigit() == False:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Pagination should be the positive interger.'
        }) 

    if 'lastStoryID' in request.GET:
        last_story_id = int(request.GET['lastStoryID'])
        story_id_list = api.get_id_list_of_stories_searched_by_tag(
            tag, 
            int(pagination), 
            last_story_id
        )
    else:
        story_id_list = api.get_id_list_of_stories_searched_by_tag(
            tag, 
            int(pagination), 
            None
        )

    stories = utilities.get_stories_from_story_id_list(story_id_list)

    if len(stories) == STORIES_PER_QUERY:
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to get searched stories. There are more stories.',
            'stories': stories
        })
    else:
        return JsonResponse({
            'state': 'success', 
            'code': 2,
            'msg': 'Succeed to get searched stories. There is no more story.',
            'stories': stories
        })


@login_required
@csrf_protect
@require_http_methods(['POST'])
def create_closing_vote(request):
    """
    Create closing vote object
    Parameter: story ID
    """
    if all(x in request.POST for x in ['storyID']):
        story_id = int(request.POST['storyID'])
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Story ID parameter is required.'
        }) 

    try:
        story = api.get_story_object(int(story_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Story does not exist.'
        }) 

    if story.state != 'processing':
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Story is deleted or closed.'
        }) 

    if story.comments_count < MIN_COMMENTS_TO_INITIATE_CLOSING_VOTE:
        return JsonResponse({
            'state': 'fail', 
            'code': 4,
            'msg': 'Caught from minmum limit for comments count.'
        }) 

    if request.user not in story.contributors.all():
        return JsonResponse({
            'state': 'fail', 
            'code': 5,
            'msg': 'User does not contributed story yet.'
        }) 

    if ClosingVotes.objects.filter(story=story, closed=False).count() > 0:
        return JsonResponse({
            'state': 'fail', 
            'code': 6,
            'msg': 'Closing vote is opened already.'
        }) 

    now = timezone.now()

    closing_vote = ClosingVotes(
        story=story,
        initiator=request.user,
        due=datetime(now.year, now.month, now.day, now.hour) + timedelta(days=1, hours=1)
    )
    closing_vote.save()

    redis.update_story_cache(story.id, 'closing_vote_opened', True)

    # Asynchronously push notification to story contributors and subscribers
    cron.push_notification_to_user.apply_async(
        args=[
            story,
            'closing_vote_opened',
            story.title,
            None,
            None,
            0
        ]
    )

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to create closing vote object.',
        'id': closing_vote.id,
        'due': closing_vote.due
    }) 


@require_http_methods(['GET'])
def get_closing_vote(request, closing_vote_id):
    """
    Get closing vote object
    Parameter: closing vote ID
    """
    try:
        closing_vote = ClosingVotes.objects.get(id=int(closing_vote_id))
        
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to get closing vote object.',
            'id': closing_vote.id,
            'due': closing_vote.due
        }) 
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Closing vote does not exist.'
        }) 


@csrf_protect
@require_http_methods(['POST'])
def vote_agreement_to_closing_vote(request, closing_vote_id):
    """
    Vote agreement to closing vote
    Parameter: closing vote ID
    """
    if not request.user.is_authenticated():
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Login is required to vote.'
        }) 

    try:
        closing_vote = ClosingVotes.objects.get(id=int(closing_vote_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Closing vote does not exist.'
        }) 

    if closing_vote.closed == True:
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Closing vote already closed.'
        }) 

    try:
        closing_vote_record = ClosingVoteRecords.objects.get(closing_vote=closing_vote, voter=request.user)
        
        # Cancel agreement
        if closing_vote_record.agreement == True:
            closing_vote_record.delete()
            
            closing_vote.agreement_count -= 1
            closing_vote.save()
            
            return JsonResponse({
                'state': 'success', 
                'code': 1,
                'msg': 'Succeed to cancel agreement to closing vote.',
                'agreement_count': closing_vote.agreement_count,
                'disagreement_count': closing_vote.disagreement_count,
                'agreement_ratio': utilities.get_percentage_value(
                    closing_vote.agreement_count, closing_vote.disagreement_count)
            }) 
        # Cancel disagreement, vote agreement
        else:
            closing_vote_record.agreement = False
            closing_vote_record.save()
            
            closing_vote.agreement_count += 1
            closing_vote.disagreement_count -= 1
            closing_vote.save()
            
            return JsonResponse({
                'state': 'success', 
                'code': 2,
                'msg': 'Succeed to cancel disagreement and vote agreement to closing vote.',
                'agreement_count': closing_vote.agreement_count,
                'disagreement_count': closing_vote.disagreement_count,
                'agreement_ratio': utilities.get_percentage_value(
                    closing_vote.agreement_count, closing_vote.disagreement_count)
            }) 
    # Vote agreement
    except:
        closing_vote_record = ClosingVoteRecords(
            closing_vote=closing_vote, 
            voter=request.user,
            agreement=True
        )
        closing_vote_record.save()
        
        closing_vote.agreement_count += 1
        closing_vote.save()
        
        return JsonResponse({
            'state': 'success', 
            'code': 3,
            'msg': 'Succeed to vote agreement to closing vote.',
            'agreement_count': closing_vote.agreement_count,
            'disagreement_count': closing_vote.disagreement_count,
            'agreement_ratio': utilities.get_percentage_value(
                closing_vote.agreement_count, closing_vote.disagreement_count)
        }) 


@csrf_protect
@require_http_methods(['POST'])
def vote_disagreement_to_closing_vote(request, closing_vote_id):
    """
    Vote disagreement to closing vote
    Parameter: closing vote ID
    """
    if not request.user.is_authenticated():
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Login is required to vote.'
        }) 

    try:
        closing_vote = ClosingVotes.objects.get(id=int(closing_vote_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Closing vote does not exist.'
        }) 

    if closing_vote.closed == True:
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Closing vote already closed.'
        }) 

    try:
        closing_vote_record = ClosingVoteRecords.objects.get(closing_vote=closing_vote, voter=request.user)
        
        # Cancel disagreement
        if closing_vote_record.agreement == False:
            closing_vote_record.delete()
            
            closing_vote.disagreement_count -= 1
            closing_vote.save()
            
            return JsonResponse({
                'state': 'success', 
                'code': 1,
                'msg': 'Succeed to cancel disagreement to closing vote.',
                'agreement_count': closing_vote.agreement_count,
                'disagreement_count': closing_vote.disagreement_count,
                'agreement_ratio': utilities.get_percentage_value(
                    closing_vote.agreement_count, closing_vote.disagreement_count)
            }) 
        # Cancel agreement, vote disagreement
        else:
            closing_vote_record.agreement = False
            closing_vote_record.save()
            
            closing_vote.agreement_count -= 1
            closing_vote.disagreement_count += 1
            closing_vote.save()
            
            return JsonResponse({
                'state': 'success', 
                'code': 2,
                'msg': 'Succeed to cancel agreement and vote disagreement to closing vote.',
                'agreement_count': closing_vote.agreement_count,
                'disagreement_count': closing_vote.disagreement_count,
                'agreement_ratio': utilities.get_percentage_value(
                    closing_vote.agreement_count, closing_vote.disagreement_count)
            }) 
    # Vote disagreement
    except:
        closing_vote_record = ClosingVoteRecords(
            closing_vote=closing_vote, 
            voter=request.user,
            agreement=False
        )
        closing_vote_record.save()
        
        closing_vote.disagreement_count += 1
        closing_vote.save()
        
        return JsonResponse({
            'state': 'success', 
            'code': 3,
            'msg': 'Succeed to vote disagreement to closing vote.',
            'agreement_count': closing_vote.agreement_count,
            'disagreement_count': closing_vote.disagreement_count,
            'agreement_ratio': utilities.get_percentage_value(
                closing_vote.agreement_count, closing_vote.disagreement_count)
        }) 


@csrf_protect
@require_http_methods(['POST'])
def create_comment(request):
    """
    Create comment object
    Parameter: story ID, context, (optional) image, image reference, image position
    """
    if all(x in request.POST for x in ['storyID', 'context']):
        story_id = int(request.POST['storyID'])
        context = request.POST['context']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Story ID and context parameters are required.'
        }) 

    if not request.user.is_authenticated():
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'fail': 'Login is required to create comment.' 
        })

    try:
        story = api.get_story_object(int(story_id))
    except:
        return JsonResponse({
            'state': 'fail',
            'code': 3,
            'msg': 'Story does not exist.'
        })

    if story.state != 'processing':
        return JsonResponse({
            'state': 'fail', 
            'code': 4,
            'msg': 'Story is deleted or closed.'
        })

    try:
        last_own_comment = Comments.objects.filter(story=story, author=request.user)[0]
        
        if last_own_comment.created_at > timezone.now() - \
            timedelta(minutes=TIME_INTERVAL_FOR_NEW_COMMENT):
            return JsonResponse({
                'state': 'fail', 
                'code': 5,
                'msg': 'Caught from the time interval limit.'
            })
    except:
        pass

    # Save image to Cloudinary if image exist
    image_url = ''
    if 'image' in request.FILES:
        image_url = utilities.upload_image_to_cloudinary(request.FILES['image'])

    if image_url != '':
        has_image = True
    else:
        has_image = False

    if 'imageReference' in request.POST:
        image_reference = request.POST['imageReference']
    else:
        image_reference = ''

    if 'imagePosition' in request.POST:
        if request.POST['imagePosition'] == 'up':
            image_position = True
        else:
            image_position = False
    else:
        image_position = False

    # Create comment object
    comment = Comments(
        story=story,
        author=request.user, 
        order=story.comments_count + 1, 
        context=context, 
        has_image=has_image,
        image_url=image_url,
        image_reference=image_reference,
        image_position=image_position
    )
    comment.save()

    # Add user to story contributor
    if request.user not in story.contributors.all():
        story.contributors.add(request.user)
        
        api.increase_contributors_count_of_story(story)
        
        redis.update_story_cache(story.id, 'contributors_count', story.contributors_count)

    # Add user to comment participant
    comment.participants.add(request.user)

    api.increase_comments_count_of_story(story)
    api.add_number_to_user_score(request.user, SCORE_FOR_NEW_COMMENT)

    # Update Firebase DB
    utilities.update_firebase_database(
        '/story/' + str(story.id) + '/', 
        'last_comment_order', 
        comment.order
    )
    utilities.update_firebase_database(
        '/story/' + str(story.id) + '/comment/' + str(comment.id) + '/', 
        'last_reply_order', 
        0
    )

    redis.update_story_cache(story.id, 'comments_count', story.comments_count)
    redis.update_comment_cache(comment.id)

    # Asynchronously push notification to story contributors and subscribers
    cron.push_notification_to_user.apply_async(
        args=[
            story,
            'new_comment',
            story.title,
            comment.context,
            None,
            comment.author.id
        ]
    )

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to create comment object.'
    })


@require_http_methods(['GET'])
def get_comment(request, comment_id):
    """
    Get comment object
    Parameter: comment ID
    """
    comment = cache.get('comment:' + str(comment_id))

    if comment == None:
        comment = redis.update_comment_cache(int(comment_id))

    if comment == None:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Comment does not exist.'
        })

    if comment['state'] == 'deleted':
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Comment is deleted.'
        })
    else:
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to get comment object.',
            'comment': comment
        })


@login_required
@user_passes_test(lambda u: u.is_admin)
@require_http_methods(['POST'])
def delete_comment(request, comment_id):
    """
    Delete comment (Update comment state as deleted)
    """
    try:
        comment = api.get_comment_object(int(comment_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Comment does not exist.'
        }) 

    comment.state = 'deleted'
    comment.save()

    redis.update_comment_cache(comment.id, 'state', 'deleted')

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to delete comment.'
    }) 


@require_http_methods(['GET'])
def update_firebase_db_for_comment(request, comment_id):
    """
    Update Firebase DB for specific comment object
    Parameter: comment ID
    """
    try:
        comment = api.get_comment_object(int(comment_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Comment does not exist.'
        })

    # Update Firebase DB
    utilities.update_firebase_database(
        '/story/' + str(comment.story.id) + '/comment/' + str(comment.id) + '/', 
        'last_reply_order', 
        comment.replies_count
    )

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to update Firebase DB.'
    }) 

@csrf_protect
@require_http_methods(['POST'])
def vote_like_to_comment(request, comment_id):
    """
    Vote like to comment
    Parameter: comment ID
    """
    if not request.user.is_authenticated():
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Login is required to vote.'
        }) 

    try:
        comment = api.get_comment_object(int(comment_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Comment does not exist.'
        })

    if comment.author == request.user:
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Cannot vote yourself.'
        })

    try:
        comment_vote = CommentVotes.objects.get(comment=comment, voter=request.user)
        
        if comment_vote.created_at < timezone.now() - timedelta(minutes=TIME_INTERVAL_FOR_EDIT_VOTE):
            return JsonResponse({
                'state': 'fail', 
                'code': 4,
                'msg': 'Caught from the time interval limit.'
            })
        
        # Delete comment vote object (Cancel like)
        if comment_vote.like == True:
            comment_vote.delete()
            
            api.decrease_like_count_of_comment(comment)
            api.subtract_number_to_user_score(comment.author, SCORE_FOR_LIKE_COMMENT)
            redis.update_comment_cache(comment.id, 'like_count', comment.like_count)
            
            if comment.like_count == MIN_LIKE_FOR_GOLD_MEDAL - 1:
                comment.author.gold_medal -= 1
                comment.author.silver_medal += 1
                comment.author.save()
            elif comment.like_count == MIN_LIKE_FOR_SILVER_MEDAL - 1:
                comment.author.silver_medal -= 1
                comment.author.bronze_medal += 1
                comment.author.save()
            elif comment.like_count == MIN_LIKE_FOR_BRONZE_MEDAL - 1:
                comment.author.bronze_medal -= 1
                comment.author.save()
            else:
                pass
        
            return JsonResponse({
                'state': 'success',
                'code': 1,
                'msg': 'Succeed to delete comment vote object.',
                'like_count': comment.like_count,
                'dislike_count': comment.dislike_count
            })
        # Edit comment vote object (Cancel dislike, Vote like)
        else:
            comment_vote.like = True
            comment_vote.save()
            
            api.decrease_dislike_count_of_comment(comment)
            api.subtract_number_to_user_score(comment.author, SCORE_FOR_DISLIKE_COMMENT)
            api.add_number_to_user_score(request.user, COST_TO_VOTE_DISLIKE)
            redis.update_comment_cache(comment.id, 'dislike_count', comment.dislike_count)
            
            api.increase_like_count_of_comment(comment)
            api.add_number_to_user_score(comment.author, SCORE_FOR_LIKE_COMMENT)
            redis.update_comment_cache(comment.id, 'like_count', comment.like_count)
            
            if comment.like_count == MIN_LIKE_FOR_GOLD_MEDAL:
                comment.author.gold_medal += 1
                comment.author.silver_medal -= 1
                comment.author.save()
            elif comment.like_count == MIN_LIKE_FOR_SILVER_MEDAL:
                comment.author.silver_medal += 1
                comment.author.bronze_medal -= 1
                comment.author.save()
            elif comment.like_count == MIN_LIKE_FOR_BRONZE_MEDAL:
                comment.author.bronze_medal += 1
                comment.author.save()
            else:
                pass
            
            # Asynchronously push notification to comment author
            cron.push_notification_to_user.apply_async(
                args=[
                    comment,
                    'get_like',
                    comment.story.title,
                    comment.context,
                    None,
                    0
                ]
            )
            
            return JsonResponse({
                'state': 'success', 
                'code': 2,
                'msg': 'Succeed to edit comment vote object.',
                'like_count': comment.like_count,
                'dislike_count': comment.dislike_count
            })
    # Create comment vote object (Vote like)
    except:
        comment_vote = CommentVotes(
            comment=comment,
            voter=request.user,
            like=True
        )
        comment_vote.save()
        
        api.increase_like_count_of_comment(comment)
        api.add_number_to_user_score(comment.author, SCORE_FOR_LIKE_COMMENT)
        redis.update_comment_cache(comment.id, 'like_count', comment.like_count)
        
        if comment.like_count == MIN_LIKE_FOR_GOLD_MEDAL:
            comment.author.gold_medal += 1
            comment.author.silver_medal -= 1
            comment.author.save()
        elif comment.like_count == MIN_LIKE_FOR_SILVER_MEDAL:
            comment.author.silver_medal += 1
            comment.author.bronze_medal -= 1
            comment.author.save()
        elif comment.like_count == MIN_LIKE_FOR_BRONZE_MEDAL:
            comment.author.bronze_medal += 1
            comment.author.save()
        else:
            pass
        
        # Asynchronously push notification to comment author
        cron.push_notification_to_user.apply_async(
            args=[
                comment,
                'get_like',
                comment.story.title,
                comment.context,
                None,
                0
            ]
        )
        
        return JsonResponse({
            'state': 'success', 
            'code': 3,
            'msg': 'Succeed to create comment vote object.',
            'like_count': comment.like_count,
            'dislike_count': comment.dislike_count
        })


@csrf_protect
@require_http_methods(['POST'])
def vote_dislike_to_comment(request, comment_id):
    """
    Vote dislike to comment
    Parameter: comment ID
    """
    if not request.user.is_authenticated():
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Login is required to vote.'
        }) 

    try:
        comment = api.get_comment_object(int(comment_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Comment does not exist.'
        })

    if comment.author == request.user:
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Cannot vote yourself.'
        })

    try:
        comment_vote = CommentVotes.objects.get(comment=comment, voter=request.user)
        
        if comment_vote.created_at < timezone.now() - timedelta(minutes=TIME_INTERVAL_FOR_EDIT_VOTE):
            return JsonResponse({
                'state': 'fail', 
                'code': 4,
                'msg': 'Caught from the time interval limit.'
            })
        
        # Delete comment vote object (Cancel dislike)
        if comment_vote.like == False:
            comment_vote.delete()
            
            api.decrease_dislike_count_of_comment(comment)
            api.subtract_number_to_user_score(comment.author, SCORE_FOR_DISLIKE_COMMENT)
            api.add_number_to_user_score(request.user, COST_TO_VOTE_DISLIKE)
            redis.update_comment_cache(comment.id, 'dislike_count', comment.dislike_count)
        
            return JsonResponse({
                'state': 'success',
                'code': 1,
                'msg': 'Succeed to delete comment vote object.',
                'like_count': comment.like_count,
                'dislike_count': comment.dislike_count
            })
        # Edit comment vote object (Cancel like, Vote dislike)
        else:
            if request.user.score < COST_TO_VOTE_DISLIKE:
                return JsonResponse({
                    'state': 'fail', 
                    'code': 5,
                    'msg': 'Minimum score limit to vote dislike.'
                })
            
            comment_vote.like = False
            comment_vote.save()
            
            api.decrease_like_count_of_comment(comment)
            api.subtract_number_to_user_score(comment.author, SCORE_FOR_LIKE_COMMENT)
            redis.update_comment_cache(comment.id, 'like_count', comment.like_count)
            
            api.increase_dislike_count_of_comment(comment)
            api.add_number_to_user_score(comment.author, SCORE_FOR_DISLIKE_COMMENT)
            api.subtract_number_to_user_score(request.user, COST_TO_VOTE_DISLIKE)
            redis.update_comment_cache(comment.id, 'dislike_count', comment.dislike_count)
            
            if comment.like_count == MIN_LIKE_FOR_GOLD_MEDAL - 1:
                comment.author.gold_medal -= 1
                comment.author.silver_medal += 1
                comment.author.save()
            elif comment.like_count == MIN_LIKE_FOR_SILVER_MEDAL - 1:
                comment.author.silver_medal -= 1
                comment.author.bronze_medal += 1
                comment.author.save()
            elif comment.like_count == MIN_LIKE_FOR_BRONZE_MEDAL - 1:
                comment.author.bronze_medal -= 1
                comment.author.save()
            else:
                pass
            
            # Asynchronously push notification to comment author
            cron.push_notification_to_user.apply_async(
                args=[
                    comment,
                    'get_dislike',
                    comment.story.title,
                    comment.context,
                    None,
                    0
                ]
            )
            
            return JsonResponse({
                'state': 'success', 
                'code': 2,
                'msg': 'Succeed to edit comment vote object.',
                'like_count': comment.like_count,
                'dislike_count': comment.dislike_count
            })
    # Create comment vote object (Vote dislike)
    except:
        if request.user.score < COST_TO_VOTE_DISLIKE:
            return JsonResponse({
                'state': 'fail', 
                'code': 5,
                'msg': 'Minimum score limit to vote dislike.'
            })
        
        comment_vote = CommentVotes(
            comment=comment,
            voter=request.user,
            like=False
        )
        comment_vote.save()
        
        api.increase_dislike_count_of_comment(comment)
        api.add_number_to_user_score(comment.author, SCORE_FOR_DISLIKE_COMMENT)
        api.subtract_number_to_user_score(request.user, COST_TO_VOTE_DISLIKE)
        redis.update_comment_cache(comment.id, 'dislike_count', comment.dislike_count)
        
        # Asynchronously push notification to comment author
        cron.push_notification_to_user.apply_async(
            args=[
                comment,
                'get_dislike',
                comment.story.title,
                comment.context,
                None,
                0
            ]
        )
        
        return JsonResponse({
            'state': 'success', 
            'code': 3,
            'msg': 'Succeed to create comment vote object.',
            'like_count': comment.like_count,
            'dislike_count': comment.dislike_count
        })


@csrf_protect
@require_http_methods(['POST'])
def report_comment(request, comment_id):
    """
    Report comment
    Parameter: comment ID, category, (optional) reason
    """
    if all(x in request.POST for x in ['category']):
        category = request.POST['category']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Category parameter is required.'
        }) 

    if category not in [choice[0] for choice in ReportRecords.category_choices]:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Not proper category.'
        }) 

    reason = ''
    if 'reason' in request.POST:
        reason = request.POST['reason']

    if not request.user.is_authenticated():
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Login is required to report.'
        }) 

    try:
        comment = api.get_comment_object(int(comment_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 4,
            'msg': 'Comment does not exist.'
        })

    if comment.author == request.user:
        return JsonResponse({
            'state': 'fail', 
            'code': 5,
            'msg': 'Cannot report yourself.'
        })

    report_record = ReportRecords(
        informant=request.user,
        target_class='comments',
        content_id=comment.id,
        category=category,
        reason=reason
    )
    report_record.save()

    # Asynchronously push notification to comment author
    cron.push_notification_to_user.apply_async(
        args=[
            comment,
            'reported',
            comment.story.title,
            comment.context,
            None,
            0
        ]
    )

    # Asynchronously send mail
    cron.send_mail_with_template.apply_async(
        args=[
            '[모두펜] 댓글 신고 접수입니다',
            'email/content_report.html',
            'modupen@budafoo.com',
            'modupen@budafoo.com'
        ],
        kwargs={
            'context': comment.context
        }
    )

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to report comment.'
    })


@require_http_methods(['GET'])
def check_whether_user_voted_to_comment_or_not(request, comment_id):
    """
    Check whether user voted to comment or not
    Parameter: comment ID
    """
    if not request.user.is_authenticated():
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Not voted yet.'
        }) 

    try:
        comment_vote = CommentVotes.objects.get(comment_id=int(comment_id), voter=request.user)
        
        if comment_vote.like == True:
            return JsonResponse({
                'state': 'success', 
                'code': 2,
                'msg': 'Voted like already.'
            }) 
        else:
            return JsonResponse({
                'state': 'success', 
                'code': 3,
                'msg': 'Voted dislike already.'
            }) 
    except:
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Not voted yet.'
        }) 


@login_required
@user_passes_test(lambda u: u.is_admin)
@require_http_methods(['POST'])
def update_comment_cache(request, comment_id):
    """
    Update comment cache
    """
    try:
        redis.update_comment_cache(comment_id)
        
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to update comment cache.'
        }) 
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Comment does not exist.'
        }) 


@require_http_methods(['GET'])
def get_comments(request):
    """
    Get comments with options
    Parameter: story ID, (optional) first comment order, number of comments, include boundary
    """
    if all(x in request.GET for x in ['storyID']):
        story_id = int(request.GET['storyID'])
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Story ID parameter is required.'
        }) 

    story = cache.get('story:' + str(story_id))

    if story == None:
        story = redis.update_story_cache(story_id)

    if story == None:
        return JsonResponse({
            'state': 'fail',
            'code': 2,
            'msg': 'Story does not exist.'
        })

    if story['state'] == 'deleted':
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Story is deleted.'
        })

    if 'firstCommentOrder' in request.GET and request.GET['firstCommentOrder'].isdigit():
        first_comment_order = int(request.GET['firstCommentOrder'])
    else:
        first_comment_order = 1

    if 'numberOfComments' in request.GET and request.GET['numberOfComments'].isdigit():
        number_of_comments = int(request.GET['numberOfComments'])
    else:
        number_of_comments = COMMENTS_PER_QUERY

    if 'includeBoundary' in request.GET and request.GET['includeBoundary'] == 'true':
        include_boundary = True
    else:
        include_boundary = False

    comment_id_list = api.get_id_list_of_comments(
        story_id, 
        first_comment_order,
        number_of_comments,
        include_boundary
    )
    comments = utilities.get_comments_from_comment_id_list(comment_id_list)

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to get comments of story.',
        'comments': comments
    })


@csrf_protect
@require_http_methods(['POST'])
def create_reply(request):
    """
    Create reply object
    Parameter: comment ID, context
    """
    if all(x in request.POST for x in ['commentID', 'context']):
        comment_id = int(request.POST['commentID'])
        context = request.POST['context']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Comment ID and context parameters are required.'
        }) 

    if not request.user.is_authenticated():
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'fail': 'Login is required to create reply.' 
        })

    try:
        comment = api.get_comment_object(comment_id)
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Comment does not exist.'
        }) 

    if comment.state == 'deleted':
        return JsonResponse({
            'state': 'fail', 
            'code': 4,
            'msg': 'Comment is deleted.'
        })

    try:
        last_own_reply = Replies.objects.filter(comment=comment, author=request.user)[0]
        
        if last_own_reply.created_at > timezone.now() - \
            timedelta(minutes=TIME_INTERVAL_FOR_NEW_REPLY):
            return JsonResponse({
                'state': 'fail', 
                'code': 5,
                'msg': 'Caught from the time interval limit.'
            })
    except:
        pass
    
    # Create reply object
    reply = Replies(
        comment=comment,
        author=request.user,
        order=comment.replies_count + 1,
        context=context
    )
    reply.save()

    # Add user to comment participant
    if request.user not in comment.participants.all():
        comment.participants.add(request.user)

    api.increase_replies_count_of_comment(comment)
    api.add_number_to_user_score(request.user, SCORE_FOR_NEW_REPLY)

    # Update Firebase DB
    utilities.update_firebase_database(
        '/story/' + str(comment.story.id) + '/comment/' + str(comment.id) + '/', 
        'last_reply_order', 
        reply.order
    )

    redis.update_comment_cache(comment.id, 'replies_count', comment.replies_count)
    redis.update_reply_cache(reply.id)

    # Asynchronously push notification to comment participants
    cron.push_notification_to_user.apply_async(
        args=[
            comment,
            'new_reply',
            comment.story.title,
            comment.context,
            reply.context,
            reply.author.id
        ]
    )

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to create reply object.'
    })


@require_http_methods(['GET'])
def get_reply(request, reply_id):
    """
    Get reply object
    Parameter: reply ID
    """
    reply = cache.get('reply:' + str(reply_id))

    if reply == None:
        reply = redis.update_reply_cache(int(reply_id))

    if reply == None:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Reply does not exist.'
        })

    if reply['state'] == 'deleted':
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Reply is deleted.'
        })

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to get reply object.',
        'reply': reply
    })


@login_required
@user_passes_test(lambda u: u.is_admin)
@require_http_methods(['POST'])
def delete_reply(request, reply_id):
    """
    Delete reply (Update reply state as deleted)
    """
    try:
        reply = api.get_reply_object(int(reply_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Reply does not exist.'
        }) 

    reply.state = 'deleted'
    reply.save()

    redis.update_reply_cache(reply.id, 'state', 'deleted')

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to delete reply.'
    }) 


@csrf_protect
@require_http_methods(['POST'])
def report_reply(request, reply_id):
    """
    Report reply
    Parameter: reply ID, category, (optional) reason
    """
    if all(x in request.POST for x in ['category']):
        category = request.POST['category']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Category parameter is required.'
        }) 

    if category not in [choice[0] for choice in ReportRecords.category_choices]:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Not proper category.'
        }) 

    reason = ''
    if 'reason' in request.POST:
        reason = request.POST['reason']

    if not request.user.is_authenticated():
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Login is required to report.'
        }) 

    try:
        reply = api.get_reply_object(int(reply_id))
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 4,
            'msg': 'Reply does not exist.'
        })

    if reply.author == request.user:
        return JsonResponse({
            'state': 'fail', 
            'code': 5,
            'msg': 'Cannot report yourself.'
        })

    report_record = ReportRecords(
        informant=request.user,
        target_class='replies',
        content_id=reply.id,
        category=category,
        reason=reason
    )
    report_record.save()

    # Asynchronously push notification to reply author
    cron.push_notification_to_user.apply_async(
        args=[
            reply,
            'reported',
            reply.comment.story.title,
            reply.comment.context,
            reply.context,
            0
        ]
    )

    # Asynchronously send mail
    cron.send_mail_with_template.apply_async(
        args=[
            '[모두펜] 대댓글 신고 접수입니다',
            'email/content_report.html',
            'modupen@budafoo.com',
            'modupen@budafoo.com'
        ],
        kwargs={
            'context': reply.context
        }
    )

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to report reply.'
    })
    

@login_required
@user_passes_test(lambda u: u.is_admin)
@require_http_methods(['POST'])
def update_reply_cache(request, reply_id):
    """
    Update reply cache
    """
    try:
        redis.update_reply_cache(reply_id)
        
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to update reply cache.'
        })
    except:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Reply does not exist.'
        })


@require_http_methods(['GET'])
def get_replies(request):
    """
    Get replies with options
    Parameter: Comment ID, (optional) last reply order, number of replies, include boundary
    """
    if all(x in request.GET for x in ['commentID']):
        comment_id = int(request.GET['commentID'])
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Comment ID parameter is required.'
        }) 

    comment = cache.get('comment:' + str(comment_id))

    if comment == None:
        comment = redis.update_comment_cache(comment_id)

    if comment == None:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Comment does not exist.'
        }) 

    if comment['state'] == 'deleted':
        return JsonResponse({
            'state': 'fail', 
            'code': 3,
            'msg': 'Comment is deleted.'
        }) 

    if 'lastReplyOrder' in request.GET and request.GET['lastReplyOrder'].isdigit():
        last_reply_order = int(request.GET['lastReplyOrder'])
    else:
        last_reply_order = comment.replies_count

    if 'numberOfReplies' in request.GET and request.GET['numberOfReplies'].isdigit():
        number_of_replies = int(request.GET['numberOfReplies'])
    else:
        number_of_replies = REPLIES_PER_QUERY

    if 'includeBoundary' in request.GET and request.GET['includeBoundary'] == 'true':
        include_boundary = True
    else:
        include_boundary = False

    reply_id_list = api.get_id_list_of_replies(
        comment_id, 
        last_reply_order,
        number_of_replies,
        include_boundary
    )
    replies = utilities.get_replies_from_reply_id_list(reply_id_list)

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to get replies of story.',
        'replies': replies
    })


@login_required
@require_http_methods(['GET'])
def load_notification_page(request):
    """
    Load notification page
    """
    user = request.user

    new_notification_count = user.new_notification_count

    user.new_notification_count = 0
    user.save()

    return render_to_response('accounts/notifications.html', locals(), context_instance=RequestContext(request))


@login_required
@require_http_methods(['GET'])
def get_notifications(request, pagination):
    """
    Get notifications at specific pagination
    Parameter: pagination, (optional) last notification ID
    """
    if pagination.isdigit() == False:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Pagination should be the positive interger.'
        }) 

    if 'lastNotificationID' in request.GET:
        last_notification_id = int(request.GET['lastNotificationID'])
        notifications = api.get_notifications_of_user(
            request.user, 
            int(pagination), 
            last_notification_id
        )
    else:
        notifications = api.get_notifications_of_user(
            request.user, 
            int(pagination)
        )

    if len(notifications) == NOTIFICATIONS_PER_QUERY:
        return JsonResponse({
            'state': 'success', 
            'code': 1,
            'msg': 'Succeed to get notifications. There are more notifications.',
            'notifications': notifications
        })
    else:
        return JsonResponse({
            'state': 'success', 
            'code': 2,
            'msg': 'Succeed to get notifications. There is no more notification.',
            'notifications': notifications
        })


@require_http_methods(['GET'])
def get_tag(request):
    """
    Get most popular tag matching with keyword
    Parameter: keyword
    """
    if all(x in request.GET for x in ['keyword']):
        keyword = int(request.GET['keyword'])
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Keyword parameter is required.'
        }) 

    tag = Tags.objects.filter(keyword__contains=keyword).order_by('-count')[0]

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to get matching tag.',
        'tag': tag
    })


@login_required
@require_http_methods(['GET'])
def load_analytics_page(request):
    """
    Load analytics page
    """
    # Count contents
    num_of_stories_as_contributor = Stories.objects.filter(contributors=request.user).\
        exclude(state='deleted').count()

    comments = Comments.objects.filter(author=request.user).aggregate(
        author=Count('id'), 
        total_likes=Sum('like_count'), 
        total_dislikes=Sum('dislike_count')
    )

    num_of_comments_as_author = comments['author']

    total_likes_for_comments = comments['total_likes']
    if total_likes_for_comments == None:
        total_likes_for_comments = 0

    total_dislikes_for_comments = comments['total_dislikes']
    if total_dislikes_for_comments == None:
        total_dislikes_for_comments = 0

    replies = Replies.objects.filter(author=request.user).aggregate(
        author=Count('id') 
    )

    num_of_replies_as_author = replies['author']

    # Score ranking
    ranking = Users.objects.filter(score__gt=request.user.score).count() + 1

    return render_to_response('accounts/analytics.html', locals(), context_instance=RequestContext(request))


@require_http_methods(['GET'])
def load_voice_of_customer_page(request):
    """
    Load voice of customer page
    """
    return render_to_response('extra/voice_of_customer.html', locals(), context_instance=RequestContext(request))


@csrf_protect
@require_http_methods(['POST'])
def create_voice_of_customer(request):
    """
    Create voice of customer
    Parameter: feeling, context, (optional) email
    """
    if all(x in request.POST for x in ['feeling', 'context']):
        feeling = request.POST['feeling']
        context = request.POST['context']
    else:
        return JsonResponse({
            'state': 'fail', 
            'code': 1,
            'msg': 'Feeling and context parameters are required.'
        }) 

    if not request.user.is_authenticated() and 'email' not in request.POST:
        return JsonResponse({
            'state': 'fail', 
            'code': 2,
            'msg': 'Email parameter is required for not logged in user.'
        }) 

    if request.user.is_authenticated():
        VoiceOfCustomers(
            author=request.user,
            feeling=feeling,
            context=context
        ).save()
    else:
        VoiceOfCustomers(
            email=request.POST['email'],
            feeling=feeling,
            context=context
        ).save()

    # Asynchronously send mail
    cron.send_mail_with_template.apply_async(
        args=[
            '[모두펜] VOC 접수입니다',
            'email/voice_of_customer.html',
            'modupen@budafoo.com',
            'modupen@budafoo.com'
        ],
        kwargs={
            'feeling': feeling,
            'context': context
        }
    )
    
    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to create voice of customer.'
    }) 


@require_http_methods(['GET'])
def load_terms_of_use_page(request):
    """
    Load terms of use page
    """
    return render_to_response('extra/terms_of_use.html', locals(), context_instance=RequestContext(request))


@require_http_methods(['GET'])
def get_numeric_data_of_service(request):
    """
    Get numeric data of service
    """
    total_number_of_users = api.get_total_number_of_users()
    total_number_of_stories = api.get_total_number_of_stories()

    return JsonResponse({
        'state': 'success', 
        'code': 1,
        'msg': 'Succeed to get numeric data of service.',
        'totalNumberOfUsers': total_number_of_users, 
        'totalNumberOfStories': total_number_of_stories
    }) 


@login_required
@user_passes_test(lambda u: u.is_admin)
@require_http_methods(['GET'])
def load_custom_admin_page(request):
    """
    Load custom admin page
    """
    return render_to_response('extra/custom_admin.html', locals(), context_instance=RequestContext(request))
