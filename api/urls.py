from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_videos, name='search_videos'),
    path('video/<str:video_id>/', views.video_details, name='video_details'),
    path('embed/<str:video_id>/', views.embed_video, name='embed_video'),
    path('channel/<str:channel_id>/', views.channel_details, name='channel_details'),
    path('upload/', views.upload_video, name='upload_video'),
    path('edit-video-details/', views.edit_video, name='edit_video_details'), # Added edit-video-details route
]