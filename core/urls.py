from django.urls import path
from .auth_views import ParticipantLoginView, ParticipantLogoutView
from . import views

urlpatterns = [
    path('council/dashboard/', views.council_dashboard, name='council_dashboard'),
    path('council/setup/', views.council_setup, name='council_setup'),
    path('language-services/', views.government_services, name='government_services'),
    path('my-recordings/', views.my_recordings, name='my_recordings'),
    path('recordings/<int:pk>/delete/', views.delete_recording, name='delete_recording'),
    path('communities/', views.communities, name='communities'),
    path('communities/<int:pk>/join/', views.join_community, name='join_community'),
    path('community-memberships/<int:pk>/review/', views.review_membership, name='review_membership'),
    path('recordings/<int:pk>/consent/', views.update_consent, name='update_consent'),
    path('recordings/<int:pk>/withdraw/', views.withdraw_recording, name='withdraw_recording'),
    path('council/access-request/<int:pk>/review/', views.council_review_access, name='council_review_access'),
    path('council/policy/', views.council_policy, name='council_policy'),
    path('researcher/access/<int:pk>/', views.researcher_access, name='researcher_access'),
    path('researcher/download/<int:pk>/', views.researcher_download, name='researcher_download'),
    path('speaker/access-request/<int:pk>/review/', views.speaker_review_access, name='speaker_review_access'),
    path('recordings/upload/', views.upload_recording, name='upload_recording'),
    path('recordings/<int:pk>/play/', views.play_recording, name='play_recording'),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', ParticipantLoginView.as_view(), name='login'),
    path('logout/', ParticipantLogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
