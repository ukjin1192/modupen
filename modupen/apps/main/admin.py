#!usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin
from main.models import Users, Identities, Stories, Tags, ClosingVotes, ClosingVoteRecords, Comments, CommentVotes, Replies, ReportRecords, Notifications, VoiceOfCustomers


class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nickname', 'language', 'score', 'gold_medal', 'silver_medal', 'bronze_medal', 'is_active')
    search_fields = ('email', 'nickname')
    list_filter = ('last_login', )
    date_hierarchy = 'last_login'
    ordering = ('-id', )


class IdentitiesAdmin(admin.ModelAdmin):
    list_display = ('id', 'platform', 'oauth_user_id')
    search_fields = ('oauth_user_id', )
    ordering = ('-id', )


class StoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'language', 'title', 'comments_count', 'state')
    search_fields = ('title', )
    list_filter = ('created_at', )
    date_hierarchy = 'created_at'
    ordering = ('-id', )


class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'keyword', 'count')
    search_fields = ('keyword', )
    ordering = ('-id', )


class ClosingVotesAdmin(admin.ModelAdmin):
    list_display = ('id', 'story', 'initiator', 'due', 'agreement_count', 'disagreement_count')
    ordering = ('-id', )


class ClosingVoteRecordsAdmin(admin.ModelAdmin):
    list_display = ('id', 'closing_vote', 'voter', 'agreement')
    ordering = ('-id', )


class CommentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'story', 'author', 'order', 'state')
    search_fields = ('context', )
    ordering = ('-id', )


class CommentVotesAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'voter', 'like')
    ordering = ('-id', )


class RepliesAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'author', 'order', 'state')
    search_fields = ('context', )
    ordering = ('-id', )


class ReportRecordsAdmin(admin.ModelAdmin):
    list_display = ('id', 'informant', 'target_class', 'content_id', 'category', 'checked')
    list_filter = ('checked', )
    ordering = ('-id', )


class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'target_class', 'content_id', 'category')
    ordering = ('-id', )


class VoiceOfCustomersAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'email', 'feeling', 'checked')
    list_filter = ('checked', )
    ordering = ('-id', )


admin.site.register(Users, UsersAdmin)
admin.site.register(Identities, IdentitiesAdmin)
admin.site.register(Stories, StoriesAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(ClosingVotes, ClosingVotesAdmin)
admin.site.register(ClosingVoteRecords, ClosingVoteRecordsAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(CommentVotes, CommentVotesAdmin)
admin.site.register(Replies, RepliesAdmin)
admin.site.register(ReportRecords, ReportRecordsAdmin)
admin.site.register(Notifications, NotificationsAdmin)
admin.site.register(VoiceOfCustomers, VoiceOfCustomersAdmin)
