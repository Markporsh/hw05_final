from django import forms
from .models import Comment, Post


class PostForm(forms.ModelForm):
    help_text = {
        'text': 'Введите текст поста',
        'group': 'Выберитте группу',
        'image': 'Вставьте картинку',
    }

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
