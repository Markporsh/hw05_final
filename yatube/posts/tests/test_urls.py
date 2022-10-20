from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from posts.models import Group, Post, Follow


User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug'
        )
        Post.objects.create(text='тест', author_id=1)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(reverse('posts:homepage'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse(
                'posts:profile', kwargs={'username': 'HasNoName'}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse(
                'posts:group_list', kwargs={'group_slug': 'test-slug'}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_exists_at_desired_location(self):
        """Страница /posts/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_edit_exists_at_desired_location(self):
        """Страница /edit/ доступна только одному пользователю."""
        response = self.guest_client.get(
            reverse(
                'posts:post_update', kwargs={'post_id': '1'}
            )
        )
        self.assertNotEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get(
            reverse(
                'posts:post_update', kwargs={'post_id': '1'}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_exists_at_desired_location(self):
        """Страница /create/ доступна только
         зарегестрированному пользователю."""
        response = self.guest_client.get(
            reverse('posts:post_create')
        )
        self.assertNotEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_broken_location(self):
        """Страница с несуществующим адесом."""
        response = self.authorized_client.get('/somepage/')
        self.assertEqual(response.status_code, 404)

    def test_comments(self):
        """Комметарии доступны только авторизованному пользователю."""
        response_guest = self.guest_client.get(
            reverse(
                'posts:add_comment', kwargs={'post_id': 1}
            )
        )
        response_register = self.authorized_client.get(
            reverse(
                'posts:add_comment', kwargs={'post_id': 1}
            )
        )
        self.assertNotEqual(response_register, response_guest)

    def test_check_following(self):
        """Проверка доступности подписки авторизованному пользователю"""
        user2 = User.objects.create_user(username='follower')
        authorized_client2 = Client()
        authorized_client2.force_login(user2)
        response = authorized_client2.get(
            reverse(
                'posts:profile_follow', kwargs={'username': 'HasNoName'}
            )
        )
        self.assertEqual(response.status_code, 302)
        followers = Follow.objects.count()
        self.assertEqual(1, followers)
        response_2 = authorized_client2.get(
            reverse(
                'posts:profile_unfollow', kwargs={'username': 'HasNoName'}
            )
        )
        self.assertEqual(response_2.status_code, 302)
        followers = Follow.objects.count()
        self.assertEqual(0, followers)
