import json
from django.db import models
from django.contrib.auth.models import User
from channels import Group
from django_languages.fields import LanguageField
from django_countries.fields import CountryField


class Artist(models.Model):
    SEX = (  # correct field
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unknown')
    )
    artist_name = models.CharField(max_length=250)  # correct field
    artist_gender = models.CharField(max_length=1, choices=SEX, null=True, blank=True)  # correct field
    artist_impression = models.IntegerField(default=0)  # correct field  # How many times it's been used

    def __str__(self):
        return self.artist_name


class Album(models.Model):  # correct field # the equivalent of movie for a dialogue
    album_name = models.CharField(max_length=250)
    album_release_date = models.DateField(null=True, blank=True)
    album_impression = models.IntegerField(default=0)  # How many times it's been used

    def __str__(self):
        return self.album_name


class Alias(models.Model):
    alias_name = models.CharField(max_length=250, null=True, blank=True)
    alias_impression = models.IntegerField(default=0)

    def __str__(self):
        return self.alias_name


class Genre(models.Model):
    genre_name = models.CharField(max_length=50, null=True, blank=True)
    genre_impression = models.IntegerField(default=0)  # How many times it's been used

    def __str__(self):
        return self.genre_name


class Mood(models.Model):
    MOOD = (  # correct field
        ('ANGR', 'Anger'),
        ('DSGT', 'Disgust'),
        ('FEAR', 'Fear'),
        ('HAPP', 'Happy'),
        ('SADN', 'Sadness'),
        ('SURP', 'Surprise')
    )
    mood_name = models.CharField(max_length=4, choices=MOOD, null=True, blank=True)
    mood_impression = models.IntegerField(default=0)  # How many times it's been used

    def __str__(self):
        return self.mood_name


class Conversation(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')
    started_at = models.DateTimeField('date started', auto_now=True)

    class Meta:
        unique_together = (("user1", "user2"), ("user2", "user1"),)

    def __str__(self):
        return str(self.id)

    @property
    # def websocket_group(self):
    #     return Group("conversation-%s" % self.id)
    def websocket_group(self):
        return Group("room")

    def send_message(self, message, user):
        conversation = Conversation.objects.get(pk=str(self.id))
        if  user == conversation.user1.username:
            recipient = conversation.user2.username
        else:
            recipient = conversation.user1.username
        final_msg = {'conversation': str(self.id), 'message': message, 'username': user, 'recipient': recipient}
        print final_msg
        self.websocket_group.send(
            {"text": json.dumps(final_msg)}
        )


class Song(models.Model):
    CATEGORY = (  # correct field
        ('SG', 'Song'),
        ('SP', 'Speech')
    )
    category = models.CharField(max_length=2, choices=CATEGORY)  # for filtering search res
    song_name = models.CharField(max_length=200)
    song_desc = models.CharField(max_length=500)
    song = models.FileField(upload_to='songs/', default=None)  # the song itself in media format
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    alias = models.ForeignKey(Alias, on_delete=models.CASCADE, null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True, blank=True)
    mood = models.ForeignKey(Mood, on_delete=models.CASCADE, null=True, blank=True)
    song_language = LanguageField()  # to create a language field # for filtering search res
    song_country = CountryField()  # to create a language field
    created_at = models.DateTimeField('date created', auto_now=True)
    last_used = models.DateTimeField('date last used', null=True, blank=True)
    song_impression = models.IntegerField(default=0)

    def __unicode__(self):
        return self.song_desc


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    created_at = models.DateTimeField('date created', auto_now=True)
    message = models.CharField(max_length=1000)

    def __str__(self):
        return self.message




