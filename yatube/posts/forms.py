from django import forms
from .models import Comment, Post


class PostForm(forms.ModelForm):
    help_texts = {
        'text': 'Введите текст поста',
        'group': 'Выберитте группу',
        'image': 'Вставьте картинку',
    }

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    help_texts = {
        'post': 'Пост комметария',
        'text': 'Текст комментария',
        'author': 'Автор комментария',
    }

    class Meta:
        model = Comment
        fields = ('text',)
