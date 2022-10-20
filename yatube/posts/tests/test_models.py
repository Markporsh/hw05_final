from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        group = self.group
        expected_group_name = group.title
        self.assertEqual(expected_group_name, str(group))
        post = self.post
        expected_post_name = post.text
        self.assertEqual(expected_post_name, str(post))
        post_2 = Post.objects.create(
            author=self.user,
            text='Тестируем количество симвлов текста'
        )
        post_text = post_2.text
        self.assertEqual(post_text[:15], str(post_2)[:15])

    # def test_check_following(self):
    #     """Проверка доступности подписки авторизованному пользователю"""
    #     user2 = User.objects.create_user(username='follower')
    #     user_follower = Client()
    #     user_follower.force_login(user2)
    #     response = user_follower.get(
    #         reverse(
    #             'posts:profile', kwargs={'username': 'StasBasov'}
    #         )
    #     )