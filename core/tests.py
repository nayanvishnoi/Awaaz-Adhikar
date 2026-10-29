from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from unittest.mock import patch
from .models import Profile, Recording, CouncilPolicy, UsageLog, Community, CommunityMembership, AccessRequest

class RecordingTests(TestCase):
    def setUp(self):
        self.speaker = User.objects.create_user('speaker1', password='safePass123!')
        Profile.objects.create(user=self.speaker, role='speaker')
        self.other = User.objects.create_user('other1', password='safePass123!')
        Profile.objects.create(user=self.other, role='researcher')

    def test_upload_and_owner_playback(self):
        self.client.force_login(self.speaker)
        uploaded = SimpleUploadedFile('voice.wav', b'RIFF' + b'0'*100, content_type='audio/wav')
        response = self.client.post(reverse('upload_recording'), {'title':'Sample','language':'Bhojpuri','audio':uploaded})
        self.assertEqual(response.status_code, 302)
        rec = Recording.objects.get(title='Sample')
        self.assertEqual(self.client.get(reverse('play_recording', args=[rec.pk])).status_code, 200)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('play_recording', args=[rec.pk])).status_code, 404)

    def test_researcher_cannot_upload(self):
        self.client.force_login(self.other)
        result = self.client.post(reverse('upload_recording'), {'title':'Not allowed','language':'Hindi'})
        self.assertEqual(result.status_code, 403)

    def test_consent_council_and_withdrawal_enforcement(self):
        self.client.force_login(self.speaker)
        file = SimpleUploadedFile('voice.wav', b'RIFF' + b'0'*100, content_type='audio/wav')
        self.client.post(reverse('upload_recording'), {'title':'Story','language':'Bhojpuri','audio':file})
        rec = Recording.objects.get(title='Story')
        self.client.post(reverse('update_consent', args=[rec.pk]), {'allow_research':'on'})
        self.client.force_login(self.other)
        route = reverse('researcher_access', args=[rec.pk])
        self.assertEqual(self.client.post(route, {'purpose':'research'}).status_code, 302)
        access_request = AccessRequest.objects.get(researcher=self.other, recording=rec, purpose='research')
        self.assertEqual(access_request.status, 'pending')
        download_route = reverse('researcher_download', args=[access_request.pk])
        CouncilPolicy.objects.create(language='Bhojpuri', purpose='research', allowed=True)
        self.assertEqual(self.client.post(download_route).status_code, 302)
        self.client.force_login(self.speaker)
        self.assertContains(self.client.get(reverse('dashboard')), 'other1')
        self.assertEqual(self.client.post(reverse('speaker_review_access', args=[access_request.pk]), {'decision':'approved'}).status_code, 302)
        self.client.force_login(self.other)
        # Council's named approval is mandatory even after speaker approval.
        self.assertEqual(self.client.post(download_route).status_code, 302)
        council = User.objects.create_user('bhojpuri_approver', password='safePass123!')
        Profile.objects.create(user=council, role='council', community_name='Bhojpuri')
        self.client.force_login(council)
        self.assertEqual(self.client.post(reverse('council_review_access', args=[access_request.pk]), {'decision':'approved'}).status_code, 302)
        self.client.force_login(self.other)
        response = self.client.post(download_route)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'].startswith('attachment;'), True)
        self.client.force_login(self.speaker)
        self.client.post(reverse('withdraw_recording', args=[rec.pk]))
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(download_route).status_code, 302)
        self.assertTrue(UsageLog.objects.filter(recording=rec, action='access_denied').exists())

    def test_individual_speaker_approval_revocation_and_council_gate(self):
        self.client.force_login(self.speaker)
        uploaded = SimpleUploadedFile('permission.wav', b'RIFF'+b'3'*100, content_type='audio/wav')
        self.client.post(reverse('upload_recording'), {'title':'Permission demo','language':'Awadhi','audio':uploaded})
        rec = Recording.objects.get(title='Permission demo')
        self.client.post(reverse('update_consent', args=[rec.pk]), {'allow_research':'on'})
        CouncilPolicy.objects.create(language='Awadhi', purpose='research', allowed=True)
        self.client.force_login(self.other)
        self.client.post(reverse('researcher_access', args=[rec.pk]), {'purpose':'research'})
        req = AccessRequest.objects.get(recording=rec, researcher=self.other, purpose='research')
        download_route = reverse('researcher_download', args=[req.pk])
        self.assertEqual(self.client.post(download_route).status_code, 302)
        # A researcher cannot approve their own request.
        self.assertEqual(self.client.post(reverse('speaker_review_access', args=[req.pk]), {'decision':'approved'}).status_code, 404)
        self.client.force_login(self.speaker)
        self.assertEqual(self.client.post(reverse('speaker_review_access', args=[req.pk]), {'decision':'approved'}).status_code, 302)
        # A different researcher cannot download another user's grant.
        outsider = User.objects.create_user('researcher_two', password='safePass123!')
        Profile.objects.create(user=outsider, role='researcher')
        self.client.force_login(outsider)
        self.assertEqual(self.client.post(download_route).status_code, 404)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(download_route).status_code, 302)
        council = User.objects.create_user('awadhi_approver', password='safePass123!')
        Profile.objects.create(user=council, role='council', community_name='Awadhi')
        self.client.force_login(council)
        self.assertEqual(self.client.post(reverse('council_review_access', args=[req.pk]), {'decision':'approved'}).status_code, 302)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(download_route).status_code, 200)
        # Council blocks subsequent downloads, even for an approved researcher.
        CouncilPolicy.objects.filter(language='Awadhi', purpose='research').update(allowed=False)
        self.assertEqual(self.client.post(download_route).status_code, 302)
        CouncilPolicy.objects.filter(language='Awadhi', purpose='research').update(allowed=True)
        self.client.force_login(self.speaker)
        self.assertEqual(self.client.post(reverse('speaker_review_access', args=[req.pk]), {'decision':'revoked'}).status_code, 302)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(download_route).status_code, 302)
        self.assertEqual(req.recording.access_requests.count(), 1)
        # A revoked researcher can ask again, but never auto-approves.
        self.client.post(reverse('researcher_access', args=[rec.pk]), {'purpose':'research'})
        req.refresh_from_db()
        self.assertEqual(req.status, 'pending')
        self.assertEqual(self.client.post(download_route).status_code, 302)

    def test_council_must_have_assigned_language(self):
        council = User.objects.create_user('council1', password='safePass123!')
        Profile.objects.create(user=council, role='council')
        self.client.force_login(council)
        self.assertEqual(self.client.post(reverse('council_policy'), {'purpose':'research','allowed':'yes'}).status_code, 403)
        council.profile.community_name = 'Bhojpuri'
        council.profile.save()
        self.assertEqual(self.client.post(reverse('council_policy'), {'purpose':'research','allowed':'yes'}).status_code, 302)
        self.assertTrue(CouncilPolicy.objects.get(language='Bhojpuri',purpose='research').allowed)

    def test_speaker_join_and_council_approval(self):
        community = Community.objects.get(language='Bhojpuri')
        self.client.force_login(self.speaker)
        response = self.client.post(reverse('join_community', args=[community.pk]))
        self.assertEqual(response.status_code, 302)
        membership = CommunityMembership.objects.get(community=community, user=self.speaker)
        self.assertEqual(membership.status, 'pending')
        self.client.post(reverse('join_community', args=[community.pk]))
        self.assertEqual(CommunityMembership.objects.filter(community=community,user=self.speaker).count(), 1)
        council = User.objects.create_user('bhojpuri_council', password='safePass123!')
        Profile.objects.create(user=council, role='council', community_name='Bhojpuri')
        self.client.force_login(council)
        response = self.client.post(reverse('review_membership', args=[membership.pk]), {'decision':'approved'})
        self.assertEqual(response.status_code, 302)
        membership.refresh_from_db()
        self.assertEqual(membership.status, 'approved')

    def test_unrelated_council_cannot_review(self):
        membership = CommunityMembership.objects.create(community=Community.objects.get(language='Bhojpuri'),user=self.speaker)
        council = User.objects.create_user('other_council', password='safePass123!')
        Profile.objects.create(user=council, role='council', community_name='Awadhi')
        self.client.force_login(council)
        self.assertEqual(self.client.post(reverse('review_membership', args=[membership.pk]), {'decision':'approved'}).status_code, 404)
        membership.refresh_from_db()
        self.assertEqual(membership.status, 'pending')

    def test_researcher_cannot_join_as_speaker(self):
        self.client.force_login(self.other)
        community = Community.objects.get(language='Awadhi')
        self.assertEqual(self.client.post(reverse('join_community', args=[community.pk])).status_code, 403)

    def test_community_page_and_council_dashboard_render(self):
        self.assertEqual(self.client.get(reverse('communities')).status_code, 200)
        council = User.objects.create_user('council_render', password='safePass123!')
        Profile.objects.create(user=council, role='council', community_name='Bhojpuri')
        self.client.force_login(council)
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
        self.assertContains(self.client.get(reverse('council_dashboard')), 'Community Council Dashboard')
        self.assertContains(self.client.get(reverse('council_dashboard')), 'Join Requests')

    def test_admin_assigns_council_then_council_approves_join_request(self):
        community = Community.objects.get(language='Bhojpuri')
        self.client.force_login(self.speaker)
        self.client.post(reverse('join_community', args=[community.pk]))
        membership = CommunityMembership.objects.get(user=self.speaker, community=community)
        self.assertContains(self.client.get(reverse('communities')), 'Council account not assigned yet')
        self.assertEqual(self.client.get(reverse('council_dashboard')).status_code, 403)
        self.assertEqual(self.client.get(reverse('council_setup')).status_code, 403)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('council_dashboard')).status_code, 403)
        self.assertEqual(self.client.post(reverse('council_setup'), {'user_id': self.other.pk, 'community_id': community.pk}).status_code, 403)
        admin_user = User.objects.create_superuser('site_admin', 'site_admin@example.com', 'safePass123!')
        self.client.force_login(admin_user)
        self.assertContains(self.client.get(reverse('council_setup')), 'Assign Council Role')
        response = self.client.post(reverse('council_setup'), {'user_id': self.other.pk, 'community_id': community.pk}, follow=True)
        self.assertContains(response, 'is now assigned')
        self.other.profile.refresh_from_db()
        self.assertEqual(self.other.profile.role, 'council')
        self.assertEqual(self.other.profile.community_name, 'Bhojpuri')
        self.client.force_login(self.other)
        dashboard = self.client.get(reverse('council_dashboard'))
        self.assertContains(dashboard, 'speaker1')
        self.assertContains(dashboard, 'Approve')
        self.assertContains(dashboard, 'Council Dashboard')
        response = self.client.post(reverse('review_membership', args=[membership.pk]), {'decision': 'approved'})
        self.assertRedirects(response, reverse('council_dashboard'))
        membership.refresh_from_db()
        self.assertEqual(membership.status, 'approved')
        self.client.force_login(self.speaker)
        self.assertContains(self.client.get(reverse('communities')), '✓ Member')

    def test_login_logout_messages_and_45_minute_session(self):
        response = self.client.post(reverse('login'), {'username':'speaker1', 'password':'safePass123!'}, follow=True)
        self.assertContains(response, 'Login successful!')
        self.assertContains(response, 'sessionTimer')
        self.assertEqual(self.client.session.get_expiry_age() <= 2700, True)
        # Simulate the passage of 45 minutes without sleeping.
        with patch('core.session_middleware.time.time', return_value=self.client.session['login_started_at'] + 2701):
            response = self.client.get(reverse('dashboard'), follow=True)
        self.assertContains(response, 'Your 45-minute session expired')
        self.assertFalse('_auth_user_id' in self.client.session)
        response = self.client.post(reverse('login'), {'username':'speaker1', 'password':'safePass123!'}, follow=True)
        self.assertContains(response, 'Login successful!')
        response = self.client.post(reverse('logout'), follow=True)
        self.assertContains(response, 'Logout successful!')

    def test_recordings_menu_and_delete_confirmation(self):
        self.client.force_login(self.speaker)
        self.assertContains(self.client.get(reverse('dashboard')), 'My Recordings')
        uploaded = SimpleUploadedFile('delete.wav', b'RIFF' + b'0'*100, content_type='audio/wav')
        self.client.post(reverse('upload_recording'), {'title':'Disposable','language':'Hindi','audio':uploaded})
        rec = Recording.objects.get(title='Disposable')
        self.assertContains(self.client.get(reverse('my_recordings')), 'Delete Recording')
        delete_url = reverse('delete_recording', args=[rec.pk])
        self.assertEqual(self.client.post(delete_url).status_code, 403)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(delete_url, {'confirm_delete':'yes'}).status_code, 404)
        self.assertEqual(self.client.get(reverse('my_recordings')).status_code, 403)
        self.client.force_login(self.speaker)
        self.assertEqual(self.client.post(delete_url, {'confirm_delete':'yes'}).status_code, 302)
        rec.refresh_from_db()
        self.assertIsNotNone(rec.deleted_at)
        self.assertEqual(rec.audio.name, '')
        self.assertTrue(UsageLog.objects.filter(recording=rec, action='deleted').exists())
        self.assertEqual(self.client.get(reverse('play_recording', args=[rec.pk])).status_code, 404)

    def test_redesigned_home_and_official_resources_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your voice.')
        self.assertContains(response, 'How Awaaz Adhikar Works')
        resources = self.client.get(reverse('government_services'))
        self.assertEqual(resources.status_code, 200)
        self.assertContains(resources, 'API connection: Not configured')

# Create your tests here.


class CouncilDownloadRegressionTests(TestCase):
    """End-to-end permission changes: no grant survives a speaker/council revocation."""
    def setUp(self):
        self.speaker = User.objects.create_user('speaker_regression', password='safePass123!')
        self.researcher = User.objects.create_user('researcher_regression', password='safePass123!')
        self.council = User.objects.create_user('council_regression', password='safePass123!')
        self.other_council = User.objects.create_user('unrelated_council', password='safePass123!')
        Profile.objects.create(user=self.speaker, role='speaker')
        Profile.objects.create(user=self.researcher, role='researcher')
        Profile.objects.create(user=self.council, role='council', community_name='Bhojpuri')
        Profile.objects.create(user=self.other_council, role='council', community_name='Awadhi')
        self.rec = Recording.objects.create(
            speaker=self.speaker, title='Consent test', language='Bhojpuri',
            audio=SimpleUploadedFile('consent.wav', b'RIFF'+b'0'*100), allow_research=True,
        )
        CouncilPolicy.objects.update_or_create(language='Bhojpuri', purpose='research', defaults={'allowed': True})
        self.grant = AccessRequest.objects.create(
            recording=self.rec, researcher=self.researcher, purpose='research', status='approved',
        )
        self.url = reverse('researcher_download', args=[self.grant.pk])

    def test_council_review_then_revoke_and_log(self):
        self.client.force_login(self.researcher)
        self.assertEqual(self.client.post(self.url).status_code, 302)
        self.client.force_login(self.other_council)
        self.assertEqual(self.client.post(reverse('council_review_access', args=[self.grant.pk]), {'decision':'approved'}).status_code, 403)
        self.client.force_login(self.council)
        council_url = reverse('council_review_access', args=[self.grant.pk])
        self.assertEqual(self.client.post(council_url, {'decision':'approved'}).status_code, 302)
        self.client.force_login(self.researcher)
        self.assertEqual(self.client.post(self.url).status_code, 200)
        self.client.force_login(self.council)
        self.assertEqual(self.client.post(council_url, {'decision':'rejected'}).status_code, 302)
        self.client.force_login(self.researcher)
        self.assertEqual(self.client.post(self.url).status_code, 302)
        self.assertTrue(UsageLog.objects.filter(recording=self.rec, action='access_denied').exists())

    def test_speaker_revocation_overrides_council_approval(self):
        self.grant.council_status = 'approved'
        self.grant.save(update_fields=['council_status'])
        self.client.force_login(self.speaker)
        self.assertEqual(self.client.post(reverse('speaker_review_access', args=[self.grant.pk]), {'decision':'revoked'}).status_code, 302)
        self.client.force_login(self.researcher)
        self.assertEqual(self.client.post(self.url).status_code, 302)

    def test_consent_and_policy_changes_block_future_download(self):
        self.grant.council_status = 'approved'
        self.grant.save(update_fields=['council_status'])
        self.client.force_login(self.researcher)
        self.assertEqual(self.client.post(self.url).status_code, 200)
        self.rec.allow_research = False
        self.rec.save(update_fields=['allow_research'])
        self.assertEqual(self.client.post(self.url).status_code, 302)
        self.rec.allow_research = True
        self.rec.save(update_fields=['allow_research'])
        CouncilPolicy.objects.filter(language='Bhojpuri', purpose='research').update(allowed=False)
        self.assertEqual(self.client.post(self.url).status_code, 302)
