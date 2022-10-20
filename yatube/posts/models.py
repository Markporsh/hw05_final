from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import CreatedModel


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='URL'
    )
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('group_list', kwargs={'group_slug': self.slug})


class Post(CreatedModel):
    text = models.TextField(verbose_name='Текст')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='group_posts',
        verbose_name='Группа'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Коментарий'
    )
    text = models.TextField(verbose_name='Текст комментария')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user', 'author')

    def __str__(self):
        return f"Последователь: '{self.user}', автор: '{self.author}'"
