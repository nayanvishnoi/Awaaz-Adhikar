from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class Profile(models.Model):
    SPEAKER = 'speaker'
    RESEARCHER = 'researcher'
    COUNCIL = 'council'
    ROLE_CHOICES = [(SPEAKER, 'Speaker'), (RESEARCHER, 'Researcher'), (COUNCIL, 'Community Council')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=SPEAKER)
    community_name = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.role})'

class Recording(models.Model):
    speaker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_recordings')
    title = models.CharField(max_length=150)
    language = models.CharField(max_length=60)
    audio = models.FileField(upload_to='recordings/%Y/%m/', validators=[FileExtensionValidator(['mp3', 'wav', 'webm', 'ogg', 'm4a'])])
    created_at = models.DateTimeField(auto_now_add=True)
    withdrawn = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    allow_research = models.BooleanField(default=False)
    allow_education = models.BooleanField(default=False)
    allow_ai = models.BooleanField(default=False)
    allow_commercial = models.BooleanField(default=False)

    def __str__(self):
        return self.title

PURPOSE_CHOICES = [('research','Academic Research'),('education','Education'),('ai','AI Training'),('commercial','Commercial Use')]

class CouncilPolicy(models.Model):
    language = models.CharField(max_length=60)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    allowed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['language','purpose'], name='unique_language_purpose')]

class UsageLog(models.Model):
    recording = models.ForeignKey(Recording, on_delete=models.CASCADE, related_name='logs')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=40)
    purpose = models.CharField(max_length=20, blank=True)
    details = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Community(models.Model):
    name = models.CharField(max_length=120, unique=True)
    language = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class CommunityMembership(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUSES = [(PENDING, 'Pending'), (APPROVED, 'Approved'), (REJECTED, 'Rejected')]
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_memberships')
    status = models.CharField(max_length=12, choices=STATUSES, default=PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['community','user'], name='unique_member_community')]

    def __str__(self):
        return f'{self.user.username}: {self.community.name} ({self.status})'


class AccessRequest(models.Model):
    """A named researcher must receive a separate speaker decision per use."""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    REVOKED = 'revoked'
    STATUSES = [
        (PENDING, 'Pending speaker approval'),
        (APPROVED, 'Speaker approved'),
        (REJECTED, 'Speaker declined'),
        (REVOKED, 'Speaker revoked'),
    ]
    recording = models.ForeignKey(Recording, on_delete=models.CASCADE, related_name='access_requests')
    researcher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_access_requests')
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    status = models.CharField(max_length=12, choices=STATUSES, default=PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    COUNCIL_STATUSES = [('pending','Pending council review'), ('approved','Council approved'), ('rejected','Council rejected')]
    council_status = models.CharField(max_length=12, choices=COUNCIL_STATUSES, default='pending')
    council_reviewed_at = models.DateTimeField(null=True, blank=True)
    council_reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='council_reviews')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recording', 'researcher', 'purpose'], name='one_request_per_researcher_recording_purpose'
        )]
        ordering = ['-requested_at']

    def __str__(self):
        return f'{self.researcher.username} - {self.recording.title} - {self.purpose} ({self.status})'

# Create your models here.
