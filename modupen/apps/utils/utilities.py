#!usr/bin/python
# -*- coding:utf-8 -*-

import base64
import cloudinary
import cloudinary.uploader
import hashlib
import hmac
import json
from django.conf import settings
from django.core.cache import cache
from django.core.files.images import get_image_dimensions
from firebase import firebase
from main.models import Users, Identities, Stories, Tags, ClosingVotes, ClosingVoteRecords, Comments, CommentVotes, Replies, ReportRecords, Notifications, VoiceOfCustomers
from utils import redis

# Variable from settings.py
FACEBOOK_SECRET_CODE = getattr(settings, 'FACEBOOK_SECRET_CODE')

CLOUDINARY_API_KEY = getattr(settings, 'CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = getattr(settings, 'CLOUDINARY_API_SECRET')

FIREBASE_USERNAME = getattr(settings, 'FIREBASE_USERNAME')
FIREBASE_REPO_URL = getattr(settings, 'FIREBASE_REPO_URL')
FIREBASE_API_SECRET = getattr(settings, 'FIREBASE_API_SECRET')

MAX_IMAGE_SIZE = getattr(settings, 'MAX_IMAGE_SIZE')
MAX_IMAGE_RATIO = getattr(settings, 'MAX_IMAGE_RATIO')

# Cloudinary configuration
cloudinary.config( 
    cloud_name = 'modupen', 
    api_key = CLOUDINARY_API_KEY, 
    api_secret = CLOUDINARY_API_SECRET 
)

# Firebase configuration 
authentication = firebase.FirebaseAuthentication(FIREBASE_API_SECRET, FIREBASE_USERNAME, True, True)
firebase_obj = firebase.FirebaseApplication(FIREBASE_REPO_URL, authentication)


def get_language_iso_code(language_string):
    """
    Get language ISO code from language string
    Parameter: language string
    """
    if 'ko' in language_string:
        language_code = 'ko'
    elif 'cn' in language_string:
        language_code = 'cn'
    elif 'jp' in language_string:
        language_code = 'jp'
    # Use English as default
    else:
        language_code = 'en'

    return language_code


def get_percentage_value(target_value, rest_value):
    """
    Get percenetage value
    """
    if target_value == 0 and rest_value == 0:
        return 50
    else:
        return int(100 * float(target_value) / (float(target_value) + float(rest_value)))


def upload_image_to_cloudinary(image_obj):
    """
    Updload image to Cloudinary
    Parameter: image object
    """
    # Check file type is image
    if image_obj.content_type.split('/')[0] != 'image':
        return ''

    # Check maximum image size
    if image_obj._size > MAX_IMAGE_SIZE:
        return ''

    # Check maximum ratio of image width and height
    width, height = get_image_dimensions(image_obj)

    if height > MAX_IMAGE_RATIO * width:
        height = MAX_IMAGE_RATIO * width

    cloudinary_obj = cloudinary.uploader.upload(image_obj, width=width, height=height)

    return cloudinary_obj['secure_url']


def update_firebase_database(permalink, key, value):
    """
    Update Firebase DB about last comment order or last reply order
    """
    firebase_obj.put(permalink, key, value)

    return None


def get_stories_from_story_id_list(story_id_list):
    """
    Get stories from story ID list
    Parameter: story ID list
    """
    if not isinstance(story_id_list, list):
        return None

    stories = []

    for story_id in story_id_list:
        story = cache.get('story:' + str(story_id))
      
        if story == None:
            story = redis.update_story_cache(story_id)
        
        story_hits = cache.get('story:' + str(story_id) + ':hits')
        
        if story_hits == None:
            story_hits = redis.update_hits_value_cache(story_id)
        
        story['hits'] += int(story_hits)
      
        stories.append(story)

    return stories


def get_comments_from_comment_id_list(comment_id_list):
    """
    Get comments from comment ID list
    Parameter: comment ID list
    """
    if not isinstance(comment_id_list, list):
        return None

    comments = []

    for comment_id in comment_id_list:
        comment = cache.get('comment:' + str(comment_id))
      
        if comment == None:
            comment = redis.update_comment_cache(comment_id)
        
        comments.append(comment)

    return comments


def get_replies_from_reply_id_list(reply_id_list):
    """
    Get replies from reply ID list
    Parameter: reply ID list
    """
    if not isinstance(reply_id_list, list):
        return None

    replies = []

    for reply_id in reply_id_list:
        reply = cache.get('reply:' + str(reply_id))
      
        if reply == None:
            reply = redis.update_reply_cache(reply_id)
        
        replies.append(reply)

    return replies


def base64_url_decode(raw_url):
    """
    Decode URL by base64
    Parameter: raw URL
    """
    padding_factor = (4 - len(raw_url) % 4) % 4
    raw_url += "="*padding_factor

    return base64.b64decode(unicode(raw_url).translate(dict(zip(map(ord, u'-_'), u'+/'))))


def parse_facebook_signed_request(signed_request):
    """
    Parse facebook signed request and recognize user ID
    Parameter: signed request
    """
    temp = signed_request.split('.', 2)
    encoded_sig = temp[0]
    payload = temp[1]

    sig = base64_url_decode(encoded_sig)
    data = json.loads(base64_url_decode(payload))

    # Unknown algorithm
    if data.get('algorithm').upper() != 'HMAC-SHA256':
        return None
    else:
        expected_sig = hmac.new(FACEBOOK_SECRET_CODE, msg=payload, digestmod=hashlib.sha256).digest()

    if sig != expected_sig:
        return None
    else:
        return data
