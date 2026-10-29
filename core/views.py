from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, Exists, OuterRef
from django.contrib.auth import get_user_model
import time
from .forms import SignupForm, RecordingForm, ConsentForm
from .models import Profile, Recording, CouncilPolicy, UsageLog, PURPOSE_CHOICES, Community, CommunityMembership, AccessRequest
from .policy import researcher_permission_allowed, PURPOSE_FIELDS

def home(request):
    return render(request, 'home.html')

def government_services(request):
    return render(request, 'government_services.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.email = form.cleaned_data['email']
        user.save()
        Profile.objects.create(user=user, role=form.cleaned_data['role'])
        login(request, user)
        request.session['login_started_at'] = int(time.time())
        request.session.set_expiry(45 * 60)
        messages.success(request, 'Registration successful! You are now logged in.')
        return redirect('dashboard')
    return render(request, 'signup.html', {'form': form})

@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    council_community = Community.objects.filter(language=profile.community_name).first() if profile.role == 'council' else None
    my_requests = AccessRequest.objects.filter(researcher=request.user).select_related('recording', 'recording__speaker') if profile.role == 'researcher' else AccessRequest.objects.none()
    pending_access_requests = AccessRequest.objects.filter(
        recording__speaker=request.user, status=AccessRequest.PENDING,
        recording__withdrawn=False, recording__deleted_at__isnull=True,
    ).select_related('researcher', 'recording') if profile.role == 'speaker' else AccessRequest.objects.none()
    return render(request, 'dashboard.html', {
        'role': profile.role, 'profile': profile,
        'recording_count': Recording.objects.filter(speaker=request.user, deleted_at__isnull=True).count() if profile.role == 'speaker' else 0,
        'active_count': Recording.objects.filter(speaker=request.user, deleted_at__isnull=True, withdrawn=False).count() if profile.role == 'speaker' else 0,
        'recording_form': RecordingForm() if profile.role == 'speaker' else None,
        'browse_recordings': Recording.objects.filter(withdrawn=False, deleted_at__isnull=True).select_related('speaker').order_by('-created_at') if profile.role == 'researcher' else None,
        'my_access_requests': my_requests,
        'pending_access_requests': pending_access_requests,
        'pending_access_count': pending_access_requests.count() if profile.role == 'speaker' else 0,
        'approved_access_count': AccessRequest.objects.filter(recording__speaker=request.user, status='approved', recording__deleted_at__isnull=True).count() if profile.role == 'speaker' else 0,
        'researcher_pending_count': my_requests.filter(status='pending').count() if profile.role == 'researcher' else 0,
        'researcher_approved_count': my_requests.filter(status='approved').count() if profile.role == 'researcher' else 0,
        'purpose_choices': PURPOSE_CHOICES,
        'council_policies': CouncilPolicy.objects.filter(language=profile.community_name) if profile.role == 'council' else None,
        'logs': (UsageLog.objects.filter(recording__speaker=request.user) if profile.role == 'speaker' else UsageLog.objects.filter(recording__language=profile.community_name) if profile.role == 'council' else UsageLog.objects.filter(actor=request.user))[:30],
        'council_community': council_community,
        'council_access_requests': AccessRequest.objects.filter(recording__language=profile.community_name, status='approved').select_related('recording','researcher','council_reviewer').order_by('-requested_at') if profile.role == 'council' and profile.community_name else [],
        'pending_memberships': CommunityMembership.objects.filter(community=council_community, status='pending').select_related('user') if council_community else [],
        'approved_memberships': CommunityMembership.objects.filter(community=council_community, status='approved').select_related('user') if council_community else [],
        'community_recording_count': Recording.objects.filter(language=profile.community_name).count() if council_community else 0,
    })


@login_required
def council_dashboard(request):
    """Dedicated, discoverable dashboard for admin-designated council accounts."""
    if not Profile.objects.filter(user=request.user, role=Profile.COUNCIL).exists():
        return HttpResponseForbidden('Only an assigned Community Council account can open this dashboard.')
    return dashboard(request)


@login_required
def council_setup(request):
    """Only a superuser can appoint a trusted council member for a community."""
    if not request.user.is_superuser:
        return HttpResponseForbidden('Only a site administrator can assign council representatives.')
    if request.method == 'POST':
        candidate = get_user_model().objects.filter(
            pk=request.POST.get('user_id'), is_active=True, is_superuser=False
        ).first()
        community = Community.objects.filter(pk=request.POST.get('community_id')).first()
        if not candidate or not community:
            messages.error(request, 'Choose a valid active non-admin user and an existing community.')
        else:
            profile, _ = Profile.objects.get_or_create(user=candidate)
            profile.role = Profile.COUNCIL
            profile.community_name = community.language
            profile.save(update_fields=['role', 'community_name'])
            messages.success(request, f'{candidate.username} is now assigned to {community.name} Council. They can log in and open Council Dashboard.')
        return redirect('council_setup')
    return render(request, 'council_setup.html', {
        'council_candidates': get_user_model().objects.filter(is_active=True, is_superuser=False).order_by('username'),
        'council_communities': Community.objects.order_by('name'),
        'council_representatives': Profile.objects.filter(role=Profile.COUNCIL).select_related('user').order_by('community_name', 'user__username'),
    })


@login_required
def my_recordings(request):
    if not Profile.objects.filter(user=request.user, role=Profile.SPEAKER).exists():
        return HttpResponseForbidden('Speaker access required.')
    recordings = Recording.objects.filter(speaker=request.user, deleted_at__isnull=True).order_by('-created_at')
    logs = UsageLog.objects.filter(recording__speaker=request.user).select_related('recording', 'actor')[:30]
    access_requests = AccessRequest.objects.filter(recording__speaker=request.user).select_related('recording', 'researcher')
    return render(request, 'my_recordings.html', {'recordings': recordings, 'logs': logs, 'role': 'speaker', 'access_requests': access_requests})

def communities(request):
    assigned_council = Profile.objects.filter(role=Profile.COUNCIL, community_name=OuterRef('language'))
    community_list = Community.objects.annotate(
        member_count=Count('memberships', filter=Q(memberships__status='approved')),
        has_council=Exists(assigned_council),
    ).order_by('name')
    memberships = {}
    if request.user.is_authenticated:
        memberships = dict(CommunityMembership.objects.filter(user=request.user).values_list('community_id', 'status'))
    for community in community_list:
        community.my_status = memberships.get(community.id)
    return render(request, 'communities.html', {'communities': community_list, 'memberships': memberships})

@login_required
@require_POST
def join_community(request, pk):
    if not Profile.objects.filter(user=request.user, role=Profile.SPEAKER).exists():
        return HttpResponseForbidden('Only speaker accounts may request membership.')
    community = Community.objects.filter(pk=pk).first()
    if not community:
        raise Http404('Community not found')
    member, created = CommunityMembership.objects.get_or_create(community=community, user=request.user)
    if created:
        messages.success(request, 'Join request submitted. A community council will review it.')
    else:
        messages.info(request, f'Your membership status is {member.get_status_display()}.')
    return redirect('communities')

@login_required
@require_POST
def review_membership(request, pk):
    profile = Profile.objects.filter(user=request.user, role=Profile.COUNCIL).first()
    if not profile or not profile.community_name:
        return HttpResponseForbidden('Verified council role required.')
    member = CommunityMembership.objects.select_related('community').filter(pk=pk, community__language=profile.community_name, status='pending').first()
    if not member:
        raise Http404('Pending request not found for your community')
    decision = request.POST.get('decision')
    if decision not in ('approved','rejected'):
        return HttpResponseForbidden('Invalid decision')
    member.status = decision
    member.reviewed_at = timezone.now()
    member.save(update_fields=['status', 'reviewed_at'])
    messages.success(request, f'Membership request {decision}.')
    return redirect('council_dashboard')

@login_required
@require_POST
def upload_recording(request):
    if not Profile.objects.filter(user=request.user, role=Profile.SPEAKER).exists():
        return HttpResponseForbidden('Speaker access required.')
    form = RecordingForm(request.POST, request.FILES)
    if form.is_valid():
        recording = form.save(commit=False)
        recording.speaker = request.user
        recording.save()
        messages.success(request, 'Recording saved successfully!')
    else:
        messages.error(request, 'Upload failed: ' + ' '.join(str(x) for errors in form.errors.values() for x in errors))
    return redirect('dashboard')

@login_required
def play_recording(request, pk):
    try:
        recording = Recording.objects.get(pk=pk, speaker=request.user, deleted_at__isnull=True)
    except Recording.DoesNotExist:
        raise Http404('Recording not found')
    if recording.withdrawn:
        return HttpResponseForbidden('Recording is withdrawn.')
    try:
        ext = recording.audio.name.rsplit('.', 1)[-1].lower()
        content_types = {'mp3':'audio/mpeg','wav':'audio/wav','webm':'audio/webm','ogg':'audio/ogg','m4a':'audio/mp4'}
        return FileResponse(recording.audio.open('rb'), content_type=content_types.get(ext, 'application/octet-stream'), as_attachment=False)
    except OSError:
        raise Http404('Audio file missing')

@login_required
@require_POST
def update_consent(request, pk):
    recording = Recording.objects.filter(pk=pk, speaker=request.user, deleted_at__isnull=True).first()
    if not recording:
        raise Http404
    if recording.withdrawn:
        return HttpResponseForbidden('Consent was withdrawn; cannot reactivate this recording.')
    form = ConsentForm(request.POST, instance=recording)
    if form.is_valid():
        form.save()
        UsageLog.objects.create(recording=recording, actor=request.user, action='consent_updated')
        messages.success(request, 'Consent updated. Council restrictions still apply.')
    return redirect('my_recordings')

@login_required
@require_POST
def withdraw_recording(request, pk):
    recording = Recording.objects.filter(pk=pk, speaker=request.user, deleted_at__isnull=True).first()
    if not recording:
        raise Http404
    if not recording.withdrawn:
        recording.withdrawn = True
        recording.save(update_fields=['withdrawn'])
        AccessRequest.objects.filter(recording=recording, status=AccessRequest.APPROVED).update(
            status=AccessRequest.REVOKED, reviewed_at=timezone.now()
        )
        UsageLog.objects.create(recording=recording, actor=request.user, action='withdrawn', details='Future platform-controlled researcher access blocked')
    messages.success(request, 'Future access is blocked. Previously downloaded copies or AI training cannot be undone.')
    return redirect('my_recordings')

@login_required
@require_POST
def delete_recording(request, pk):
    recording = Recording.objects.filter(pk=pk, speaker=request.user, deleted_at__isnull=True).first()
    if not recording:
        raise Http404('Recording not found')
    if request.POST.get('confirm_delete') != 'yes':
        return HttpResponseForbidden('Deletion must be explicitly confirmed.')
    try:
        recording.audio.delete(save=False)
    except OSError:
        messages.error(request, 'Audio could not be deleted. Please try again.')
        return redirect('my_recordings')
    recording.audio = ''
    recording.deleted_at = timezone.now()
    recording.withdrawn = True
    recording.save(update_fields=['audio', 'deleted_at', 'withdrawn'])
    AccessRequest.objects.filter(recording=recording, status=AccessRequest.APPROVED).update(
        status=AccessRequest.REVOKED, reviewed_at=timezone.now()
    )
    UsageLog.objects.create(recording=recording, actor=request.user, action='deleted', details='Audio removed; metadata and audit history retained')
    messages.success(request, 'Recording deleted successfully. Audit history remains for transparency.')
    return redirect('my_recordings')

@login_required
@require_POST
def council_policy(request):
    profile = Profile.objects.filter(user=request.user, role=Profile.COUNCIL).first()
    if not profile or not profile.community_name:
        return HttpResponseForbidden('Verified council profile with assigned language required.')
    purpose = request.POST.get('purpose')
    if purpose not in PURPOSE_FIELDS:
        return HttpResponseForbidden('Invalid purpose')
    allowed = request.POST.get('allowed') == 'yes'
    CouncilPolicy.objects.update_or_create(language=profile.community_name, purpose=purpose, defaults={'allowed':allowed})
    for recording in Recording.objects.filter(language=profile.community_name):
        UsageLog.objects.create(recording=recording, actor=request.user, action='council_policy', purpose=purpose, details='Allowed' if allowed else 'Blocked')
    messages.success(request, 'Council policy updated. Future access uses the latest policy.')
    return redirect('dashboard')

@login_required
@require_POST
def researcher_access(request, pk):
    profile = Profile.objects.filter(user=request.user, role=Profile.RESEARCHER).first()
    if not profile:
        return HttpResponseForbidden('Researcher role required.')
    recording = Recording.objects.filter(pk=pk, deleted_at__isnull=True, withdrawn=False).first()
    if not recording:
        raise Http404
    purpose = request.POST.get('purpose', '')
    if purpose not in PURPOSE_FIELDS:
        return HttpResponseForbidden('Invalid purpose')
    access_request, created = AccessRequest.objects.get_or_create(
        recording=recording, researcher=request.user, purpose=purpose,
    )
    if created or access_request.status in ('rejected', 'revoked'):
        if not created:
            access_request.status = AccessRequest.PENDING
            access_request.requested_at = timezone.now()
            access_request.reviewed_at = None
            access_request.save(update_fields=['status', 'requested_at', 'reviewed_at'])
        access_request.council_status = 'pending'
        access_request.council_reviewer = None
        access_request.council_reviewed_at = None
        access_request.save(update_fields=['council_status', 'council_reviewer', 'council_reviewed_at'])
        UsageLog.objects.create(recording=recording, actor=request.user, action='access_requested', purpose=purpose, details='Waiting for named speaker approval')
        messages.success(request, 'Request sent! Speaker will see your username and choose Allow or Reject. You cannot download yet.')
    elif access_request.status == AccessRequest.APPROVED:
        messages.info(request, 'Speaker already approved. Use the Download button in Your Requests (council and use permissions still apply).')
    else:
        messages.info(request, 'Your request is pending. Please wait for the speaker to decide.')
    return redirect('dashboard')


@login_required
@require_POST
def speaker_review_access(request, pk):
    access_request = AccessRequest.objects.select_related('recording', 'researcher').filter(
        pk=pk, recording__speaker=request.user, recording__deleted_at__isnull=True
    ).first()
    if not access_request:
        raise Http404('Request not found')
    decision = request.POST.get('decision')
    if decision not in ('approved', 'rejected', 'revoked'):
        return HttpResponseForbidden('Invalid decision')
    if decision in ('approved', 'rejected') and access_request.status != AccessRequest.PENDING:
        return HttpResponseForbidden('This request is no longer pending')
    if decision == 'revoked' and access_request.status != AccessRequest.APPROVED:
        return HttpResponseForbidden('Only approved requests can be revoked')
    if decision == 'approved' and access_request.recording.withdrawn:
        return HttpResponseForbidden('Recording was withdrawn')
    access_request.status = decision
    if decision == 'approved':
        access_request.council_status = 'pending'
    access_request.reviewed_at = timezone.now()
    access_request.save(update_fields=['status', 'reviewed_at', 'council_status'])
    UsageLog.objects.create(
        recording=access_request.recording, actor=request.user,
        action='request_' + decision, purpose=access_request.purpose,
        details='Researcher: ' + access_request.researcher.username[:120],
    )
    messages.success(request, f'{access_request.researcher.username}: access {decision}. Council and use permissions are still checked on download.')
    return redirect('dashboard')


@login_required
@require_POST
def researcher_download(request, pk):
    if not Profile.objects.filter(user=request.user, role=Profile.RESEARCHER).exists():
        return HttpResponseForbidden('Researcher role required.')
    access_request = AccessRequest.objects.select_related('recording').filter(
        pk=pk, researcher=request.user
    ).first()
    if not access_request:
        raise Http404('Your request was not found')
    recording = access_request.recording
    if not researcher_permission_allowed(access_request):
        if recording.deleted_at or recording.withdrawn:
            explanation = 'Recording was withdrawn or deleted.'
        elif access_request.status != AccessRequest.APPROVED:
            explanation = 'Speaker has not approved your individual request.'
        elif access_request.council_status != 'approved':
            explanation = 'Community Council has not approved this individual request.'
        elif not PURPOSE_FIELDS.get(access_request.purpose) or not getattr(recording, PURPOSE_FIELDS[access_request.purpose]):
            explanation = 'Speaker did not enable this purpose for the recording.'
        else:
            explanation = 'Community Council has not allowed this purpose.'
        UsageLog.objects.create(recording=recording, actor=request.user, action='access_denied', purpose=access_request.purpose, details=explanation)
        messages.error(request, 'Download blocked: ' + explanation)
        return redirect('dashboard')
    try:
        ext = recording.audio.name.rsplit('.', 1)[-1].lower()
        content_types = {'mp3':'audio/mpeg','wav':'audio/wav','webm':'audio/webm','ogg':'audio/ogg','m4a':'audio/mp4'}
        stream = recording.audio.open('rb')
        UsageLog.objects.create(recording=recording, actor=request.user, action='access_allowed', purpose=access_request.purpose, details='Authorized download started; delivery outside platform cannot be recalled')
        return FileResponse(stream, content_type=content_types.get(ext, 'application/octet-stream'), as_attachment=True, filename=f'recording-{recording.pk}.{ext}')
    except OSError:
        raise Http404('Audio missing')


@login_required
@require_POST
def council_review_access(request, pk):
    """Only the council assigned to the recording language can decide."""
    profile = Profile.objects.filter(user=request.user, role=Profile.COUNCIL).first()
    access = AccessRequest.objects.select_related('recording', 'researcher').filter(
        pk=pk, status=AccessRequest.APPROVED, recording__deleted_at__isnull=True
    ).first()
    if not profile or not access or not profile.community_name or access.recording.language != profile.community_name:
        return HttpResponseForbidden('Assigned council and speaker approval required.')
    decision = request.POST.get('decision')
    if decision not in ('approved', 'rejected'):
        return HttpResponseForbidden('Invalid council decision.')
    access.council_status = decision
    access.council_reviewer = request.user
    access.council_reviewed_at = timezone.now()
    access.save(update_fields=['council_status','council_reviewer','council_reviewed_at'])
    UsageLog.objects.create(recording=access.recording, actor=request.user, action='council_request_' + decision,
                            purpose=access.purpose, details='Researcher: ' + access.researcher.username[:120])
    messages.success(request, f'Individual request {decision}. Language policy and speaker consent still apply.')
    return redirect('council_dashboard')
