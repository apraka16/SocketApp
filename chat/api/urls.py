from django.conf.urls import url
from .views import (
    ConversationListAPIView, MessageListAPIView, SongListAPIView, UserListAPIView,
    ConversationDetailAPIView, MessageDetailAPIView, SongDetailAPIView,
    ConversationDeleteAPIView, MessageDeleteAPIView, MessageCreateAPIView,
    UserCreateAPIView, UserLoginAPIView, ConversationCreateAPIView
)

app_name = 'chat'

urlpatterns = [
    url(r'^conversation/$', ConversationListAPIView.as_view(), name='conversation_list'),
    url(r'^conversation/(?P<pk>[0-9]+)/$', ConversationDetailAPIView.as_view(), name='conversation_detail'),
    url(r'^conversation/(?P<conversation_id>[0-9]+)/messages/$', MessageListAPIView.as_view(),
        name='message_list'),
    url(r'^conversation/(?P<conversation_id>[0-9]+)/messages/(?P<pk>[0-9]+)/$', MessageDetailAPIView.as_view(),
        name='message_detail'),

    url(r'^conversation/(?P<conversation_id>[0-9]+)/messages/create/$', MessageCreateAPIView.as_view(),
        name='message_create'),

    url(r'^conversation/create/$', ConversationCreateAPIView.as_view(),
        name='conversation_create'),
    url(r'^conversation/(?P<pk>[0-9]+)/delete/$', ConversationDeleteAPIView.as_view(),
        name='conversation_delete'),
    url(r'^conversation/(?P<conversation_id>[0-9]+)/messages/(?P<pk>[0-9]+)/delete/$', MessageDeleteAPIView.as_view(),
        name='message_delete'),



    url(r'^songs(?P<q>.+)$', SongListAPIView.as_view(), name='song_list'),
    url(r'^login/$', UserLoginAPIView.as_view(), name='login'),
    url(r'^register/$', UserCreateAPIView.as_view(), name='register'),
    url(r'^users/$', UserListAPIView.as_view(), name='user_list'),
    url(r'^songs/(?P<pk>[0-9]+)/$', SongDetailAPIView.as_view(), name='song_detail'),
]





