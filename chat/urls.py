from django.conf.urls import url, include
from . import views

app_name = 'chat'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<user_id>[0-9]+)/$', views.fetch_conversation, name='conversation'),
    url(r'^search/$', views.search_song, name='search_song'),

    url(r'^api/', include('chat.api.urls', namespace='chat-api')),
]

