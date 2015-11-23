#!usr/bin/python
# -*- coding:utf-8 -*-
# Admin > Djcelery > periodic tasks

from celery import task
from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone
from main.models import Users, Identities, Stories, Tags, ClosingVotes, ClosingVoteRecords, Comments, CommentVotes, Replies, ReportRecords, Notifications, VoiceOfCustomers
from utils import api, redis, utilities

# Variable from settings.py
INACTIVATE_DAYS_TO_CLOSE_STORY = getattr(settings, 'INACTIVATE_DAYS_TO_CLOSE_STORY')
MIN_AGREEMENT_RATIO_TO_CLOSE_STORY = getattr(settings, 'MIN_AGREEMENT_RATIO_TO_CLOSE_STORY')

SCORE_FOR_NEW_COMMENT = getattr(settings, 'SCORE_FOR_NEW_COMMENT')
SCORE_FOR_LIKE_COMMENT = getattr(settings, 'SCORE_FOR_LIKE_COMMENT')
SCORE_FOR_DISLIKE_COMMENT = getattr(settings, 'SCORE_FOR_DISLIKE_COMMENT')
SCORE_FOR_NEW_REPLY = getattr(settings, 'SCORE_FOR_NEW_REPLY')


@task()
def close_inactive_story_for_few_days():
    """
    Close story if story is not updated for few days
    Period: once a day
    """
    stories = Stories.objects.filter(
        state='processing', 
        updated_at__lt=timezone.now() - timedelta(days=INACTIVATE_DAYS_TO_CLOSE_STORY)
    ).exclude(id=25)

    for story in stories:
        story.state = 'closed'
        story.save()
        
        redis.update_story_cache(story.id, 'state', 'closed')
        redis.update_story_cache(story.id, 'closing_vote_opened', False)
        
        # Push notification to story contributors and subscribers
        push_notification_to_user(story, 'closed', story.title, None, None, 0)

    return None


@task()
def check_closing_vote_for_story():
    """
    Check closing vote for story and close story if agreement ratio exceeds specific value
    Period: every hour on the hour
    """
    closing_votes = ClosingVotes.objects.filter(closed=False, due__lte=timezone.now())

    for closing_vote in closing_votes:
        story = closing_vote.story
        
        # Story already closed
        if story.state == 'closed':
            closing_vote.closed = True
            closing_vote.save()
            
            redis.update_story_cache(story.id, 'state', 'closed')
        # Succeed to close story
        elif utilities.get_percentage_value(closing_vote.agreement_count, 
            closing_vote.disagreement_count) >= MIN_AGREEMENT_RATIO_TO_CLOSE_STORY:
            story.state = 'closed'
            story.save()
        
            redis.update_story_cache(story.id, 'state', 'closed')
            
            # Push notification to story contributors and subscribers
            push_notification_to_user(story, 'closed', story.title, None, None, 0)
        # Failed to close story
        else:
            closing_vote.closed = True
            closing_vote.save()
            
        redis.update_story_cache(story.id, 'closing_vote_opened', False)

    return None


@task()
def update_user_score(user_obj):
    """
    Re-calculate score of user
    Parameter: user object
    """
    if not isinstance(user_obj, Users):
        return None

    comments = Comments.objects.filter(author=user_obj).aggregate(
        author=Count('id'),
        total_likes=Sum('like_count'),
        total_dislikes=Sum('dislike_count')
    )
    num_of_comments_as_author = comments['author']
    total_likes_for_comments = comments['total_likes']
    total_dislikes_for_comments = comments['total_dislikes']

    replies = Replies.objects.filter(author=user_obj).aggregate(
        author=Count('id')
    )
    num_of_replies_as_author = comments['author']

    score = num_of_comments_as_author * SCORE_FOR_NEW_COMMENT +\
        total_likes_for_comments * SCORE_FOR_LIKE_COMMENT +\
        total_dislikes_for_comments * SCORE_FOR_DISLIKE_COMMENT +\
        num_of_replies_as_author * SCORE_FOR_NEW_REPLY

    user_obj.score = score
    user_obj.save()

    return None


@task()
def update_nickname_of_user_wrote_contents_cache(user_obj):
    """
    Update nickname of stories, comments, replies cache that user wrote
    Parameter: user object
    """
    if not isinstance(user_obj, Users):
        return None

    story_id_list = api.get_id_list_of_user_wrote_stories(user_obj, None, None)

    for story_id in story_id_list:                               
        redis.update_story_cache(story_id, 'author_nickname', user_obj.nickname) 

    comment_id_list = api.get_id_list_of_user_wrote_comments(user_obj, None, None)

    for comment_id in comment_id_list:
        redis.update_comment_cache(comment_id, 'author_nickname', user_obj.nickname)

    reply_id_list = api.get_id_list_of_user_wrote_replies(user_obj, None, None)

    for reply_id in reply_id_list:
        redis.update_reply_cache(reply_id, 'author_nickname', user_obj.nickname)

    return None


@task()
def push_notification_to_user(content_obj, category, story_title=None, comment_context=None, reply_context=None, exception_user_id=0):
    """
    Push notification to user(s) with respect to updated content
    Parameter: content object, category, (optional) preview, exception user ID
    """
    if isinstance(content_obj, Stories) and category == 'new_comment':
        story_obj = content_obj
        target_class = 'stories'
        content_id = story_obj.id
        link_url = '/story/' + str(story_obj.id) + '/#' + str(story_obj.comments_count)
        
        contributors = story_obj.contributors.all()
        subscribers = Users.objects.filter(favorites=story_obj)
        
        for target_user in (contributors | subscribers).distinct().exclude(id=int(exception_user_id)):
            Notifications(
                user=target_user,
                target_class=target_class,
                content_id=content_id,
                link_url=link_url,
                category=category,
                story_title=story_title,
                comment_context=comment_context,
                reply_context=reply_context
            ).save()
            
            target_user.new_notification_count += 1
            target_user.save()
    elif isinstance(content_obj, Stories) and category == 'closed':
        story_obj = content_obj
        target_class = 'stories'
        content_id = story_obj.id
        link_url = '/story/' + str(story_obj.id) + '/'
        
        contributors = story_obj.contributors.all()
        subscribers = Users.objects.filter(favorites=story_obj)
        
        for target_user in (contributors | subscribers).distinct():
            Notifications(
                user=target_user,
                target_class=target_class,
                content_id=content_id,
                link_url=link_url,
                category=category,
                story_title=story_title,
                comment_context=comment_context,
                reply_context=reply_context
            ).save()
            
            target_user.new_notification_count += 1
            target_user.save()
    elif isinstance(content_obj, Stories) and category == 'closing_vote_opened':
        story_obj = content_obj
        target_class = 'stories'
        content_id = story_obj.id
        link_url = '/story/' + str(story_obj.id) + '/'
        
        contributors = story_obj.contributors.all()
        subscribers = Users.objects.filter(favorites=story_obj)
        
        for target_user in (contributors | subscribers).distinct():
            Notifications(
                user=target_user,
                target_class=target_class,
                content_id=content_id,
                link_url=link_url,
                category=category,
                story_title=story_title,
                comment_context=comment_context,
                reply_context=reply_context
            ).save()
            
            target_user.new_notification_count += 1
            target_user.save()
    elif isinstance(content_obj, Comments) and category == 'new_reply':
        comment_obj = content_obj
        target_class = 'comments'
        content_id = comment_obj.id
        link_url = '/story/' + str(comment_obj.story.id) + '/#' + str(comment_obj.order)
        
        for participant in comment_obj.participants.all().exclude(id=int(exception_user_id)):
            Notifications(
                user=participant,
                target_class=target_class,
                content_id=content_id,
                link_url=link_url,
                category=category,
                story_title=story_title,
                comment_context=comment_context,
                reply_context=reply_context
            ).save()
            
            participant.new_notification_count += 1
            participant.save()
    elif isinstance(content_obj, Comments) and category in ['get_like', 'get_dislike', 'reported']:
        comment_obj = content_obj
        target_class = 'comments'
        content_id = comment_obj.id
        link_url = '/story/' + str(comment_obj.story.id) + '/#' + str(comment_obj.order)
        
        Notifications(
            user=comment_obj.author,
            target_class=target_class,
            content_id=content_id,
            link_url=link_url,
            category=category,
            story_title=story_title,
            comment_context=comment_context,
            reply_context=reply_context
        ).save()
        
        author = comment_obj.author
        author.new_notification_count += 1
        author.save()
    elif isinstance(content_obj, Replies) and category == 'reported':
        reply_obj = content_obj
        target_class = 'replies'
        content_id = reply_obj.id
        link_url = '/story/' + str(reply_obj.comment.story.id) + '/#' + str(reply_obj.comment.order)
        
        Notifications(
            user=reply_obj.author,
            target_class=target_class,
            content_id=content_id,
            link_url=link_url,
            category=category,
            story_title=story_title,
            comment_context=comment_context,
            reply_context=reply_context
        ).save()
        
        author = reply_obj.author
        author.new_notification_count += 1
        author.save()

    return None


@task()
def send_mail_with_template(title, template_name, sender_email_address, *addressee_email_address_list, **dictionary_variables):
    """
    Send mail with template
    Parameter: title, template name, sender email address, 
        addressee email address list, dictionary variables
    For example,
        send_mail_with_template.apply_async(
            args=[
                'Title Here',
                'email/template_name.html',
                'sender@domain.com',
                'addressee_1@domain.com', 'addressee_2@domain.com'
            ],
            kwargs={
                'var_1': 'foo', 
                'var_2': 'bar'
            }
        )
    """
    plaintext = get_template('email/email.txt')
    htmly = get_template(template_name)

    d = Context(dictionary_variables)

    text_content = plaintext.render(d)
    html_content = htmly.render(d)

    msg = EmailMultiAlternatives(
        title,
        text_content,
        sender_email_address,
        addressee_email_address_list
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

    return None
