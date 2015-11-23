#!usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _


class MyUserManager(BaseUserManager):
    """
    Use email as unique username
    """
    
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password
        """
        if not email:
            raise ValueError('Users must have an email address')
        
        user = self.model(
            email=self.normalize_email(email),
        )
        
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        
        return user


class Users(AbstractBaseUser):
    """
    User profile which extends AbstracUser
    AbstractBaseUser contains basic fields like password and last_login
    """
    email = models.EmailField(
        verbose_name = _('Email'),
        max_length = 255,
        unique = True
    )
    nickname = models.CharField(
        verbose_name = _('Username'),
        max_length = getattr(settings, 'NICKNAME_MAX_LENGTH', None),
        unique = True,
        null = False
    )
    language_choices = getattr(settings, 'LANGUAGES')
    language = models.CharField(
        verbose_name = _('Language'),
        max_length = 2,
        choices = language_choices,
        default = 'ko'
    )
    favorites = models.ManyToManyField(
        'Stories',
        blank = True
    )
    score = models.PositiveIntegerField(
        verbose_name = _('Score'),
        default = 0
    )
    is_active = models.BooleanField(
        verbose_name = _('Active'),
        default = True
    )
    is_admin = models.BooleanField(
        verbose_name = _('Admin'),
        default = False
    )
    login_with_oauth = models.BooleanField(
        verbose_name = _('Login with OAuth'),
        default = False
    )
    email_verified = models.BooleanField(
        verbose_name = _('Email verified'),
        default = False
    )
    new_notification_count = models.PositiveSmallIntegerField(
        verbose_name = _('New notification count'),
        default = 0
    )
    allow_notification = models.BooleanField(
        verbose_name = _('Allow notification'),
        default = True
    )
    gold_medal = models.PositiveSmallIntegerField(
        verbose_name = _('Gold medal'),
        default = 0
    )
    silver_medal = models.PositiveSmallIntegerField(
        verbose_name = _('Silver medal'),
        default = 0
    )
    bronze_medal = models.PositiveSmallIntegerField(
        verbose_name = _('Bronze medal'),
        default = 0
    )
    date_joined = models.DateTimeField(
        verbose_name = _('Joined datetime'),
        auto_now_add = True,
        editable = False
    )

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profile')
        ordering = ['-id']   

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __unicode__(self):
        return unicode(self.email) or u''

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin


class Identities(models.Model):
    """
    Identity information for OAuth login
    """
    user = models.ForeignKey(
        'Users',
    )
    platform_choices = (
        ('facebook', 'Facebook'),
    )
    platform = models.CharField(
        verbose_name = _('Platform'),
        max_length = 10,
        choices = platform_choices,
        default = 'facebook'
    )
    oauth_user_id = models.CharField(
        verbose_name = _('OAuth User ID'),
        max_length = 30
    )
    created_at = models.DateTimeField(
        verbose_name = _('Created datetime'),
        auto_now_add = True,
        editable = False
    )
    updated_at = models.DateTimeField(
        verbose_name = _('Updated datetime'),
        auto_now = True
    )

    class Meta:
        verbose_name = _('Identity')
        verbose_name_plural = _('Identities')
        ordering = ['-id']

    def __unicode__(self):
        return unicode(self.oauth_user_id) or u''


class Stories(models.Model):
    """
    Story information
    """
    author = models.ForeignKey(
        'Users',
    )
    tags = models.ManyToManyField(
        'Tags',
        related_name='stories_tags',
        blank = True
    )
    contributors = models.ManyToManyField(
        'Users',
        related_name='stories_contributors',
        blank = True
    )
    contributors_count = models.PositiveSmallIntegerField(
        verbose_name = _('Contributors count'),
        default = 1
    )
    language_choices = getattr(settings, 'LANGUAGES')
    language = models.CharField(
        verbose_name = _('Language'),
        max_length = 2,
        choices = language_choices,
        default = 'ko'
    )
    title = models.CharField(
        verbose_name = _('Title'),
        max_length = getattr(settings, 'TITLE_MAX_LENGTH', None)
    )
    comments_count = models.PositiveIntegerField(
        verbose_name = _('Comments count'),
        default = 1
    )
    hits = models.PositiveIntegerField(
        verbose_name = _('Hits'),
        default = 0
    )
    favorites_count = models.PositiveIntegerField(
        verbose_name = _('Favorites count'),
        default = 0
    )
    state_choices = (
        ('processing', 'Processing'),
        ('closed', 'Closed'),
        ('deleted', 'Deleted'),
    )
    state = models.CharField(
        verbose_name = _('State'),
        max_length = 10,
        choices = state_choices,
        default = 'processing'
    )
    created_at = models.DateTimeField(
        verbose_name = _('Created datetime'),
        auto_now_add = True,
        editable = False
    )
    updated_at = models.DateTimeField(
        verbose_name = _('Updated datetime')
    )

    class Meta:
        verbose_name = _('Story')
        verbose_name_plural = _('Stories')
        ordering = ['-id']

    def __unicode__(self):
        return unicode(self.title) or u''


class Tags(models.Model):
    """
    Tag for story
    """
    keyword = models.CharField(
        verbose_name = _('Keyword'),
        max_length = getattr(settings, 'TAG_MAX_LENGTH', None),
        unique = True
    )
    count = models.PositiveSmallIntegerField(
        verbose_name = _('Count how many time used'),
        default = 0
    )
    created_at = models.DateTimeField(
        verbose_name = _('Created datetime'),
        auto_now_add = True,
        editable = False
    )
    updated_at = models.DateTimeField(
        verbose_name = _('Updated datetime'),
        auto_now = True
    )

    class Meta:
        verbose_name = _('Tags')
        verbose_name_plural = _('Tags')
        ordering = ['-id']

    def __unicode__(self):
        return unicode(self.keyword) or u''


class ClosingVotes(models.Model):
    """
    Closing vote for story
    """
    story = models.ForeignKey(
        'Stories'
    )
    initiator = models.ForeignKey(
        'Users',
    )
    due = models.DateTimeField(
        verbose_name = _('Due')
    )
    closed = models.BooleanField(
        verbose_name = _('Closed'),
        default = False
    )
    agreement_count = models.PositiveIntegerField(
        verbose_name = _('Agreement count'),
        default = 0
    )
    disagreement_count = models.PositiveIntegerField(
        verbose_name = _('Disagreement count'),
        default = 0
    )
    created_at = models.DateTimeField(
        verbose_name = _('Created datetime'),
        auto_now_add = True,
        editable = False
    )
    updated_at = models.DateTimeField(
        verbose_name = _('Updated datetime'),
        auto_now = True
    )

    class Meta:
        verbose_name = _('Closing votes')
        verbose_name_plural = _('Closing votes')
        ordering = ['-id']

    def __unicode__(self):
        return unicode(self.id) or u''


class ClosingVoteRecords(models.Model):
    """
    Record of closing vote for story
    """
    closing_vote = models.ForeignKey(
        'ClosingVotes'
    )
    voter = models.ForeignKey(
        'Users',
    )
    agreement = models.BooleanField(
        verbose_name = _('Agreement'),
        default = True
    )
    created_at = models.DateTimeField(
        verbose_name = _('Created datetime'),
        auto_now_add = True,
        editable = False
    )
    updated_at = models.DateTimeField(
        verbose_name = _('Updated datetime'),
        auto_now = True
    )

    class Meta:
        verbose_name = _('Closing vote records')
        verbose_name_plural = _('Closing vote records')
        ordering = ['-id']

    def __unicode__(self):
        return unicode(self.id) or u''


class Comments(models.Model):
    """
    Comments under specific story
    """
    story = models.ForeignKey(
        'Stories'
    )
    author = models.ForeignKey(
        'Users',
    )
    participants = models.ManyToManyField(
        'Users',
        related_name='comments_participants',
        blank = True
    )
    order = models.PositiveSmallIntegerField(
        verbose_name = _('Order')
    )
    context = models.TextField(
        verbose_name = _('Context'),
        max_length = getattr(settings, 'COMMENT_MAX_LENGTH', None)
    )
    has_image = models.BooleanField(
        verbose_name = _('Has image'),
        default = False
    )
    image_url = models.CharField(
        verbose_name = _('Image URL'),
        max_length = 255,
        blank = True,
        null = True
    )
    image_reference = models.CharField(
        verbose_name = _('Image Reference'),
        max_length = 255,
        blank = True,
        null = True
    )
    image_position = models.BooleanField(
        verbose_name = _('Image position - Up or down side'),
        default = True
    )
    replies_count = models.PositiveIntegerField(
        verbose_name = _('Replies count'),
        default = 0
    )
    like_count = models.PositiveIntegerField(
        verbose_name = _('Like count'),
        default = 0
    )
    dislike_count = models.PositiveIntegerField(
        verbose_name = _('Dislike count'),
        default = 0
    )
    state_choices = (
        ('shown', 'Shown'),
        ('deleted', 'Deleted'),
    )
    state = models.CharField(
        verbose_name = _('State'),
        max_length = 10,
        choices = state_choices,
        default = 'shown'
    )
    created_at = models.DateTimeField(
        verbose_name = _('Created datetime'),
        auto_now_add = True,
        editable = False
    )
    updated_at = models.DateTimeField(
        verbose_name = _('Updated datetime'),
        auto_now = True
    )

    class Meta:
        verbose_name = _('Comments')
        verbose_name_plural = _('Comments')
        ordering = ['-id']

    def __unicode__(self):
        return unicode(self.id) or u''


class CommentVotes(models.Model):
    """
    Vote to comment
    """
    comment = models.ForeignKey(
        'Comments'
    )
    voter = models.ForeignKey(
        'Users'
    )
    like = models.BooleanField(
        verbose_name = _('Like'),
        default = True
    )
    created_at= models.DateTimeField(
        verbose_name = _('Created datetime'),
        auto_now_add = True,
        editable = False
    )
    updated_at= models.DateTimeField(
        verbose_name = _('Updated datetime'),
        auto_now = True
    )

    class Meta:
        verbose_name = _('Comment votes')
        verbose_name_plural = _('Comment votes')
        ordering = ['-id']

    def __unicode__(self):
        return unicode(self.id) or u''


class Replies(models.Model):
    """
    Replies under specific comment
    """
    comment = models.ForeignKey(
        'Comments'
    )
    author = models.ForeignKey(
        'Users',
    )
    order = models.PositiveSmallIntegerField(
        verbose_name = _('Order')
    )
    context = models.TextField(
        verbose_name = _('Context'),
        max_length = getattr(settings, 'REPLY_MAX_LENGTH', None)
    )
    state_choices = (
        ('shown', 'Shown'),
        ('deleted', 'Deleted'),
    )
    state = models.CharField(
        verbose_name = _('State'),
        max_length = 10,
        choices = state_choices,
        default = 'shown'
    )
    created_at = models.DateTimeField(
        verbose_name = _('Created datetime'),
        auto_now_add = True,
        editable = False
    )
    updated_at = models.DateTimeField(
        verbose_name = _('Updated datetime'),
        auto_now = True
    )

    class Meta:
        verbose_name = _('Replies')
        verbose_name_plural = _('Replies')
        ordering = ['-id']

    def __unicode__(self):
        return unicode(self.id) or u''


class ReportRecords(models.Model):
    """
    Report records for comment or reply
    """
    informant = models.ForeignKey(
        'Users'
    )
    target_class_choices = (
        ('comments', 'Comments'),
        ('replies', 'Replies'),
    )
    target_class = models.CharField(
        verbose_name = _('Target class'),
        max_length = 10,
        choices = target_class_choices
    )
    content_id = models.PositiveIntegerField(
        verbose_name = _('Content ID')
    )
    category_choices = (
        ('extraneous', 'Extraneous'),
        ('promotional', 'Promotional'),
        ('lustful', 'Lustful'),
        ('expletive', 'Expletive'),
        ('copyright', 'Copyright'),
        ('defamation', 'Defamation'),
    )
    category = models.CharField(
        verbose_name = _('Category'),
        max_length = 20,
        choices = category_choices
    )
    reason = models.TextField(
        verbose_name = _('Reason'),
        blank = True,
        null = True
    )
    checked = models.BooleanField(
        verbose_name = _('Admin checked'),
        default = False
    )
    created_at= models.DateTimeField(
        verbose_name = _('Created datetime'),
        auto_now_add = True,
        editable = False
    )
    updated_at= models.DateTimeField(
        verbose_name = _('Updated datetime'),
        auto_now = True
    )

    class Meta:
        verbose_name = _('Report records')
        verbose_name_plural = _('Report records')
        ordering = ['-id']

    def __unicode__(self):
        return unicode(self.id) or u''


class Notifications(models.Model):
    """
    Notifications for contents update
    """
    user = models.ForeignKey(
        'Users'
    )
    target_class_choices = (
        ('stories', 'Stories'),
        ('comments', 'Comments'),
        ('replies', 'Replies'),
    )
    target_class = models.CharField(
        verbose_name = _('Target class'),
        max_length = 10,
        choices = target_class_choices
    )
    content_id = models.PositiveIntegerField(
        verbose_name = _('Content ID')
    )
    link_url = models.CharField(
        verbose_name = _('Link URL'),
        max_length = 255
    )
    category_choices = (
        ('new_comment', 'New comment'),
        ('new_reply', 'New reply'),
        ('get_like', 'Get like'),
        ('get_dislike', 'Get dislike'),
        ('reported', 'Reported'),
        ('closed', 'Story closed'),
        ('closing_vote_opened', 'Closing vote opened'),
    )
    category = models.CharField(
        verbose_name = _('Category'),
        max_length = 20,
        choices = category_choices
    )
    story_title = models.TextField(
        verbose_name = _('Story title'),
        max_length = 20,
        blank = True,
        null = True
    )
    comment_context = models.TextField(
        verbose_name = _('Comment context'),
        blank = True,
        null = True
    )
    reply_context = models.TextField(
        verbose_name = _('Reply context'),
        blank = True,
        null = True
    )
    created_at= models.DateTimeField(
        verbose_name = _('Created datetime'),
        auto_now_add = True,
        editable = False
    )
    updated_at= models.DateTimeField(
        verbose_name = _('Updated datetime'),
        auto_now = True
    )

    class Meta:
        verbose_name = _('Notifications')
        verbose_name_plural = _('Notifications')
        ordering = ['-id']

    def __unicode__(self):
        return unicode(self.id) or u''


class VoiceOfCustomers(models.Model):
    """
    Voice of customer
    """
    author = models.ForeignKey(
        'Users',
        blank = True,
        null = True
    )
    email = models.EmailField(
        verbose_name = _('Email'),
        max_length = 255,
        blank = True,
        null = True
    )
    feeling_choices = (
        ('default', 'Default'),
        ('expected', 'Expected'),
        ('curious', 'Curious'),
        ('apprehensive', 'Apprehensive'),
        ('angry', 'Angry'),
    )
    feeling = models.CharField(
        verbose_name = _('Feeling'),
        max_length = 20,
        choices = feeling_choices
    )
    context = models.TextField(
        verbose_name = _('Context')
    )
    checked = models.BooleanField(
        verbose_name = _('Admin checked'),
        default = False
    )
    created_at= models.DateTimeField(
        verbose_name = _('Created datetime'),
        auto_now_add = True,
        editable = False
    )
    updated_at= models.DateTimeField(
        verbose_name = _('Updated datetime'),
        auto_now = True
    )

    class Meta:
        verbose_name = _('Voice of customers')
        verbose_name_plural = _('Voice of customers')
        ordering = ['-id']

    def __unicode__(self):
        return unicode(self.id) or u''
