from django.contrib import admin

from .models import Artist, Album, Alias, Genre, Mood, Conversation, Song, Message

admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Alias)
admin.site.register(Genre)
admin.site.register(Mood)
admin.site.register(Conversation)
admin.site.register(Song)
admin.site.register(Message)
