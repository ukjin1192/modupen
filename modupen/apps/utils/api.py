#!usr/bin/python
# -*- coding:utf-8 -*-

from django.conf import settings
from django.utils import timezone
from main.models import Users, Identities, Stories, Tags, ClosingVotes, ClosingVoteRecords, Comments, CommentVotes, Replies, ReportRecords, Notifications, VoiceOfCustomers

# Variable from settings.py
STORIES_PER_QUERY = getattr(settings, 'STORIES_PER_QUERY')
COMMENTS_PER_QUERY = getattr(settings, 'COMMENTS_PER_QUERY')
REPLIES_PER_QUERY = getattr(settings, 'REPLIES_PER_QUERY')
NOTIFICATIONS_PER_QUERY = getattr(settings, 'NOTIFICATIONS_PER_QUERY')


def get_story_object(story_id):
    """
    Get story object
    Parameter: story ID
    """
    if isinstance(story_id, int) == False:
        return None

    story = Stories.objects.get(id=story_id)

    return story


def get_id_list_of_stories(language_iso_code='ko', filter_option='processing', sorting_option='updated_at', pagination=1, last_story_id=None):
    """
    Get ID list of stories
    Parameter: lanuage ISO code, state, sorting option, pagination, (optional) last story ID
    """
    if isinstance(language_iso_code, (str, unicode)) == False or isinstance(filter_option, (str, unicode)) == False \
        or isinstance(sorting_option, (str, unicode)) == False or isinstance(pagination, int) == False:
        return []

    if last_story_id != None and isinstance(last_story_id, int) == False:
        return []

    if sorting_option == 'updated_at':
        sorting_option = '-updated_at'
    elif sorting_option == 'created_at':
        sorting_option = '-id'
    elif sorting_option == 'hits':
        sorting_option = '-hits'
    elif sorting_option == 'favorites':
        sorting_option = '-favorites_count'
    else:
        sorting_option = '-id'

    if last_story_id != None and sorting_option == '-id':
        story_id_list = list(Stories.objects.filter(language=language_iso_code, state=filter_option, id__lt=last_story_id).\
            exclude(state='deleted').order_by(sorting_option)[0 : STORIES_PER_QUERY].\
            values_list('id', flat=True))
    else:
        story_id_list = list(Stories.objects.filter(language=language_iso_code, state=filter_option).\
            exclude(state='deleted').order_by(sorting_option, '-id')\
            [(pagination - 1) * STORIES_PER_QUERY : pagination * STORIES_PER_QUERY].\
            values_list('id', flat=True))

    return story_id_list


def get_id_list_of_stories_searched_by_title(title, pagination, last_story_id=None):
    """
    Get ID list of stories searched by title with recently created order
    Parameter: title, pagination, (optional) last story ID
    """
    if isinstance(title, (str, unicode)) == False or isinstance(pagination, int) == False:
        return []

    if last_story_id != None and isinstance(last_story_id, int) == False:
        return []

    if last_story_id == None:
        story_id_list = list(Stories.objects.filter(title__contains=title).exclude(state='deleted')\
            [(pagination - 1) * STORIES_PER_QUERY : pagination * STORIES_PER_QUERY].\
            values_list('id', flat=True))
    else:
        story_id_list = list(Stories.objects.filter(title__contains=title, id__lt=last_story_id).\
            exclude(state='deleted')[0 : STORIES_PER_QUERY].values_list('id', flat=True))

    return story_id_list


def get_id_list_of_stories_searched_by_tag(tag, pagination, last_story_id=None):
    """
    Get ID list of stories searched by tag with recently created order
    Parameter: tag, pagination, (optional) last story ID
    """
    if isinstance(tag, (str, unicode)) == False or isinstance(pagination, int) == False:
        return []

    try:
        tag_obj = Tags.objects.get(keyword=tag)
    except:
        return []

    if last_story_id != None and isinstance(last_story_id, int) == False:
        return []

    if last_story_id == None:
        story_id_list = list(Stories.objects.filter(tags=tag_obj).exclude(state='deleted')\
            [(pagination - 1) * STORIES_PER_QUERY : pagination * STORIES_PER_QUERY].\
            values_list('id', flat=True))
    else:
        story_id_list = list(Stories.objects.filter(tags=tag_obj, id__lt=last_story_id).\
            exclude(state='deleted')[0 : STORIES_PER_QUERY].values_list('id', flat=True))

    return story_id_list


def get_id_list_of_user_favorite_stories(user_obj, pagination=1):
    """
    Get ID list of user favorite stories with recently added order
    Parameter: user object, pagination
    """
    if isinstance(user_obj, Users) == False or isinstance(pagination, int) == False:
        return []

    story_id_list = list(user_obj.favorites.all().distinct().exclude(state='deleted')\
        [(pagination - 1) * STORIES_PER_QUERY : pagination * STORIES_PER_QUERY].\
        values_list('id', flat=True))

    return story_id_list


def get_id_list_of_user_wrote_stories(user_obj, pagination=None, last_story_id=None):
    """
    Get ID list of user wrote stories with recently created order
    Parameter: user object, (optional) pagination, last story ID
    """
    if isinstance(user_obj, Users) == False:
        return []

    if pagination != None and isinstance(pagination, int) == False:
        return []

    if last_story_id != None and isinstance(last_story_id, int) == False:
        return []

    if pagination == None:
        story_id_list = list(Stories.objects.filter(author=user_obj).values_list('id', flat=True))
    elif last_story_id == None:
        story_id_list = list(Stories.objects.filter(author=user_obj).exclude(state='deleted')\
            [(pagination - 1) * STORIES_PER_QUERY :pagination * STORIES_PER_QUERY].\
            values_list('id', flat=True))
    else:
        story_id_list = list(Stories.objects.filter(author=user_obj, id__lt=last_story_id).\
            exclude(state='deleted')[0 : STORIES_PER_QUERY].values_list('id', flat=True))

    return story_id_list


def get_id_list_of_user_contributed_stories(user_obj, pagination):
    """
    Get ID list of user contributed stories with recently updated order
    Parameter: user object, pagination
    """
    if isinstance(user_obj, Users) == False or isinstance(pagination, int) == False:
        return []

    story_id_list = list(Stories.objects.filter(contributors=user_obj).exclude(state='deleted').\
        order_by('-updated_at')[(pagination - 1) * STORIES_PER_QUERY : pagination * STORIES_PER_QUERY].\
        values_list('id', flat=True))

    return story_id_list


def increase_contributors_count_of_story(story_obj):
    """
    +1 contributors count of story
    Parameter: story object
    """
    if isinstance(story_obj, Stories) == False:
        return None

    story_obj.contributors_count += 1
    story_obj.save()

    return None


def increase_comments_count_of_story(story_obj):
    """
    +1 comments count of story
    Parameter: story object
    """
    if isinstance(story_obj, Stories) == False:
        return None

    story_obj.comments_count += 1
    story_obj.updated_at = timezone.now()
    story_obj.save()

    return None


def increase_favorites_count_of_story(story_obj):
    """
    +1 favorites count of story
    Parameter: story object
    """
    if isinstance(story_obj, Stories) == False:
        return None

    story_obj.favorites_count += 1
    story_obj.save()

    return None


def decrease_favorites_count_of_story(story_obj):
    """
    -1 favorites count of story
    Parameter: story object
    """
    if isinstance(story_obj, Stories) == False:
        return None

    story_obj.favorites_count -= 1
    story_obj.save()

    return None


def get_comment_object(comment_id):
    """
    Get comment object
    Parameter: comment ID
    """
    if isinstance(comment_id, int) == False:
        return None

    comment = Comments.objects.get(id=comment_id)

    return comment


def get_id_list_of_comments(story_id, first_comment_order=1, number_of_comments=COMMENTS_PER_QUERY, include_boundary=True):
    """
    Get ID list of comments with created order
    Parameter: story ID, first comment order, number of comments, include boundary 
    """
    comment_id_list = list(Comments.objects.filter(
            story__id=int(story_id), 
            order__gt=first_comment_order - include_boundary
        ).order_by('order')[0:number_of_comments].values_list('id', flat=True))

    return comment_id_list


def get_id_list_of_user_wrote_comments(user_obj, pagination=None, last_comment_id=None):
    """
    Get ID list of user wrote comments with recently created order 
    Parameter: user object, (optional) pagination, last comment ID
    """
    if isinstance(user_obj, Users) == False:
        return []

    if pagination != None and isinstance(pagination, int) == False:
        return []

    if last_comment_id != None and isinstance(last_comment_id, int) == False:
        return []

    if pagination == None:
        comment_id_list = list(Comments.objects.filter(author=user_obj).values_list('id', flat=True))
    elif last_comment_id == None:
        comment_id_list = list(Comments.objects.filter(author=user_obj)\
            [(pagination - 1) * COMMENTS_PER_QUERY : pagination * COMMENTS_PER_QUERY].\
            values_list('id', flat=True))
    else:
        comment_id_list = list(Comments.objects.filter(author=user_obj, id__lt=last_comment_id)\
            [0 : COMMENTS_PER_QUERY].values_list('id', flat=True))

    return comment_id_list


def increase_replies_count_of_comment(comment_obj):
    """
    Increase replies count of comment
    Parameter: comment object
    """
    if isinstance(comment_obj, Comments) == False:
        return None

    comment_obj.replies_count += 1
    comment_obj.save()

    return None


def increase_like_count_of_comment(comment_obj):
    """
    +1 like count of comment
    Parameter: comment object
    """
    if isinstance(comment_obj, Comments) == False:
        return None

    comment_obj.like_count += 1
    comment_obj.save()

    return None


def decrease_like_count_of_comment(comment_obj):
    """
    -1 like count of comment
    Parameter: comment object
    """
    if isinstance(comment_obj, Comments) == False:
        return None

    comment_obj.like_count -= 1
    comment_obj.save()

    return None


def increase_dislike_count_of_comment(comment_obj):
    """
    +1 dislike count of comment
    Parameter: comment object
    """
    if isinstance(comment_obj, Comments) == False:
        return None

    comment_obj.dislike_count += 1
    comment_obj.save()

    return None


def decrease_dislike_count_of_comment(comment_obj):
    """
    -1 dislike count of comment
    Parameter: comment object
    """
    if isinstance(comment_obj, Comments) == False:
        return None

    comment_obj.dislike_count -= 1
    comment_obj.save()

    return None


def get_reply_object(reply_id):
    """
    Get reply object
    Parameter: reply ID
    """
    if isinstance(reply_id, int) == False:
        return None

    reply = Replies.objects.get(id=reply_id)

    return reply


def get_id_list_of_replies(comment_id, last_reply_order, number_of_replies=REPLIES_PER_QUERY, include_boundary=True):
    """
    Get ID list of replies with recently created order
    Parameter: comment ID, first reply order, number of replies, include boundary
    """
    if last_reply_order == None:
        last_reply_order = comment_obj.replies_count

    reply_id_list = list(Replies.objects.filter(
            comment__id=int(comment_id), 
            order__lt=last_reply_order + include_boundary
        ).order_by('-order')[0:number_of_replies].values_list('id', flat=True))

    return reply_id_list


def get_id_list_of_user_wrote_replies(user_obj, pagination=None, last_reply_id=None):
    """
    Get ID list of user wrote replies with recently created order
    Parameter: user object, (optional) pagination, last reply ID
    """
    if isinstance(user_obj, Users) == False:
        return []

    if pagination != None and isinstance(pagination, int) == False:
        return []

    if last_reply_id != None and isinstance(last_reply_id, int) == False:
        return []

    if pagination == None:
        reply_id_list = list(Replies.objects.filter(author=user_obj).values_list('id', flat=True))
    elif last_reply_id == None:
        reply_id_list = list(Replies.objects.filter(author=user_obj)\
            [(pagination - 1) * REPLIES_PER_QUERY : pagination * REPLIES_PER_QUERY].\
            values_list('id', flat=True))
    else:
        reply_id_list = list(Replies.objects.filter(author=user_obj, id__lt=last_reply_id)\
            [0 : REPLIES_PER_QUERY].values_list('id', flat=True))

    return reply_id_list


def add_number_to_user_score(user_obj, number):
    """
    Add number to user score
    Parameter: user object, number
    """
    if isinstance(user_obj, Users) == False:
        return None

    user_obj.score += number
    user_obj.save()

    return None


def subtract_number_to_user_score(user_obj, number):
    """
    Subtract number to user score
    Parameter: user object, number
    """
    if isinstance(user_obj, Users) == False:
        return None

    user_obj.score -= number
    user_obj.save()

    return None


def get_notifications_of_user(user_obj, pagination, last_notification_id=None):
    """
    Get notifications of user
    Parameter: user object, pagination, (optional) last notification ID
    """
    if last_notification_id != None and isinstance(last_notification_id, int) == False:
        return []

    if last_notification_id == None:
        notifications = list(Notifications.objects.filter(user=user_obj)\
            [(pagination - 1) * NOTIFICATIONS_PER_QUERY : pagination * NOTIFICATIONS_PER_QUERY].values_list())
    else:
        notifications = list(Notifications.objects.filter(user=user_obj, id__lt=last_notification_id)\
            [0 : NOTIFICATIONS_PER_QUERY].values_list())

    return notifications


def get_total_number_of_users():
    """
    Get total number of users
    """
    total_number_of_users = Users.objects.all().exclude(is_active=False).count()

    return total_number_of_users


def get_total_number_of_stories():
    """
    Get total number of stories
    """
    total_number_of_stories = Stories.objects.all().exclude(state='deleted').count()

    return total_number_of_stories
