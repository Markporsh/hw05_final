from django import forms
from .models import *


class PostForm(forms.ModelForm):
    help_text = {
        'text': 'models.TextField',
        'group': 'models.ForeignKey(Group, blank=True)',
        'image': 'models.ImageField',
    }

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    help_text = {
        'text': 'models.TextField',
        'group': 'models.ForeignKey(Group, blank=True)',
        'image': 'models.ImageField',
    }

    class Meta:
        model = Comment
        fields = ('text',)
