from django import forms
from django.contrib.auth.models import User


class NetworkForm(forms.Form):
    user_id = forms.ModelChoiceField(queryset=User.objects.all(), empty_label='None', label='',
                                     widget=forms.Select(attrs={'class': 'all_users'}))

