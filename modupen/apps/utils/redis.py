#!usr/bin/python
# -*- coding:utf-8 -*-

from django.conf import settings
from django.core.cache import cache
from main.models import Users, Identities, Stories, Tags, ClosingVotes, ClosingVoteRecords, Comments, CommentVotes, Replies, ReportRecords, Notifications, VoiceOfCustomers
from utils import api

# Variable from settings.py
CACHE_TTL = getattr(settings, 'CACHE_TTL')
HITS_TO_COMMIT = getattr(settings, 'HITS_TO_COMMIT')


def update_story_cache(story_id, key=None, value=None):
    """
    Update story cache
    Parameter: story ID, (optional) key, value
    """
    # Update cache totally
    if key == None:
        # Save fields of story object at dictionary
        qs = Stories.objects.select_related('author').filter(id=int(story_id))
        story = list(qs.values())[0]
        
        # Add 'nickname' field of author object to dictionary
        story['author_nickname'] = qs[0].author.nickname
        
        # Add list of 'tag' to dictionary
        story['tags'] = list(qs[0].tags.all().values_list('keyword', flat=True))
        
        # Add 'has_image' and 'image_url' fields of the first comment object to dictionary
        comment = Comments.objects.filter(story=qs[0], order=1)[0]
        story['has_image'] = comment.has_image
        story['image_url'] = comment.image_url
        
        # Add information about 'closing vote' is opened or not
        if ClosingVotes.objects.filter(story=qs[0], closed=False).count() > 0:
            story['closing_vote_opened'] = True
        else:
            story['closing_vote_opened'] = False
        
        cache.set('story:' + str(story_id), story, timeout=CACHE_TTL)
        
        return story
    # Update cache partially
    else:
        story = cache.get('story:' + str(story_id))
        
        if (story == None) or (isinstance(key, (str, unicode)) == False) or (key not in story):
            return None
        
        story[key] = value
        
        cache.set('story:' + str(story_id), story, timeout=CACHE_TTL)
        
        return story


def update_hits_value_cache(story_id):
    """
    Update hits value of story cache
    Parameter: story ID
    """
    story = api.get_story_object(int(story_id))
    cache.set('story:' + str(story_id) + ':hits', str(story.hits), timeout=CACHE_TTL)

    return story.hits


def increase_hits_value_cache(story_id):
    """
    +1 hits value of story cache and commit to DB periodically
    Parameter: story ID
    """
    hits = cache.get('story:' + str(story_id) + ':hits')

    if hits == None:
        hits = update_hits_value_cache(story_id)

    hits = int(hits) + 1
    cache.set('story:' + str(story_id) + ':hits', str(hits), timeout=CACHE_TTL)

    if hits % HITS_TO_COMMIT == 0:
        story = api.get_story_object(int(story_id))
        story.hits += HITS_TO_COMMIT
        story.save()
        
        # Initialize cache
        cache.set('story:' + str(story.id) + ':hits', '0', timeout=CACHE_TTL)
        
        update_story_cache(story.id, 'hits', story.hits)

    return None


def update_comment_cache(comment_id, key=None, value=None):
    """
    Update comment cache
    Parameter: comment ID, (optional) key, value
    """
    # Update cache totally
    if key == None:
        # Save fields of comment object at dictionary
        qs = Comments.objects.select_related('author').filter(id=int(comment_id))
        comment = list(qs.values())[0]
        
        # Add 'nickname' field of author object to dictionary
        comment['author_nickname'] = qs[0].author.nickname
        
        # Add 'id' and 'title' fields of story object to dictionary
        comment['story_id'] = qs[0].story.id
        comment['story_title'] = qs[0].story.title
        
        cache.set('comment:' + str(comment_id), comment, timeout=CACHE_TTL)
        
        return comment
    # Update cache partially
    else:
        comment = cache.get('comment:' + str(comment_id))
        
        if (comment == None) or (isinstance(key, (str, unicode)) == False) or (key not in comment):
            return None
        
        comment[key] = value
        
        cache.set('comment:' + str(comment_id), comment, timeout=CACHE_TTL)
        
        return comment


def update_reply_cache(reply_id, key=None, value=None):
    """
    Update reply cache
    Parameter: reply ID, (optional) key, value
    """
    # Update cache totally
    if key == None:
        # Save fields of reply object at dictionary
        qs = Replies.objects.select_related('author').filter(id=int(reply_id))
        reply = list(qs.values())[0]
        
        # Add 'nickname' field of author object to dictionary
        reply['author_nickname'] = qs[0].author.nickname
        
        # Add 'id' and 'order' fields of comment object to dictionary
        reply['comment_id'] = qs[0].comment.id
        reply['comment_order'] = qs[0].comment.order
        
        # Add 'id' and 'title' fields of story object to dictionary
        reply['story_id'] = qs[0].comment.story.id
        reply['story_title'] = qs[0].comment.story.title
        
        cache.set('reply:' + str(reply_id), reply, timeout=CACHE_TTL)
        
        return reply
    # Update cache partially
    else:
        reply = cache.get('reply:' + str(reply_id))
        
        if (reply == None) or (isinstance(key, (str, unicode)) == False) or (key not in reply):
            return None
        
        reply[key] = value
        
        cache.set('reply:' + str(reply_id), reply, timeout=CACHE_TTL)
        
        return reply
