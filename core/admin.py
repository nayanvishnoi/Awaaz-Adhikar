from django.contrib import admin
from .models import Profile, Recording, CouncilPolicy, UsageLog, Community, CommunityMembership, AccessRequest

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'community_name')
    list_filter = ('role',)
    search_fields = ('user__username', 'community_name')

@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ('title', 'speaker', 'language', 'created_at', 'withdrawn')
    list_filter = ('language', 'withdrawn')

admin.site.register(CouncilPolicy)
admin.site.register(UsageLog)

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'language')

@admin.register(CommunityMembership)
class CommunityMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'community', 'status', 'requested_at')
    list_filter = ('status', 'community')


@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ('researcher', 'recording', 'purpose', 'status', 'requested_at', 'reviewed_at', 'council_status', 'council_reviewer')
    list_filter = ('status', 'purpose')
    search_fields = ('researcher__username', 'recording__title')

# Register your models here.
