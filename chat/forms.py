from django import forms
from django.contrib.auth.models import User


class NetworkForm(forms.Form):

    def __init__(self, uid_list, *args, **kwargs):
        super(NetworkForm, self).__init__(*args, **kwargs)
        self.fields['user_id'].queryset = User.objects.filter(id__in=uid_list)

    error_css_class = 'error'

    user_id = forms.ModelChoiceField(queryset=User.objects.all(), empty_label='None', label='',
                                     widget=forms.Select(attrs={'class': 'all_users'}),
                                     error_messages={"invalid_choice": "User has already added you. Check out your network below."},
                                     )





