import shutil
import tempfile
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Group, Post, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        for i in range(14):
            Post.objects.create(
                text=i, author_id=cls.user.id, group=group, image=cls.uploaded
            )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:homepage'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'group_slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'StasBasov'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_update', kwargs={'post_id': '1'}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:homepage'))
        first_object = response.context['page_obj'][0]
        task_title_0 = first_object.text
        self.assertEqual(
            task_title_0,
            Post.objects.order_by('-pub_date')[0].text
        )

    def test_first_homepage_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:homepage'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_homepage_page_contains_three_records(self):
        response = self.client.get(reverse('posts:homepage') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'group_slug': 'test-slug'})
        )
        self.assertEqual(
            response.context.get('group').title, 'Тестовый заголовок'
        )
        self.assertEqual(
            response.context.get('group').description, 'Тестовое описание'
        )
        self.assertEqual(
            response.context.get('group').slug, 'test-slug'
        )

    def test_first_group_list_page_contains_ten_records(self):
        response = self.client.get(
            reverse(
                'posts:group_list', kwargs={'group_slug': 'test-slug'}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_group_list_page_contains_three_records(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'group_slug': 'test-slug'}
                    ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'StasBasov'})
        )
        self.assertEqual(
            response.context.get('posts')[0].text,
            Post.objects.order_by('-pub_date')[0].text
        )

    def test_first_profile_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'StasBasov'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page_contains_three_records(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'StasBasov'}
                    ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': Post.objects.order_by('id')[0].id}
            )
        )
        self.assertEqual(
            response.context.get('posts').text,
            Post.objects.order_by('id')[0].text)

    def test_create_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_update_show_correct_context(self):
        """Шаблон update сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_update',
                kwargs={'post_id': Post.objects.order_by('id')[1].id}
            )
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_on_homepage(self):
        new_post = Post.objects.create(
            text='Тестируем', author_id=self.user.id
        )
        response = self.authorized_client.get(reverse('posts:homepage'))
        homepage = response.context.get('page_obj').object_list[0]
        self.assertEqual(homepage, new_post)

    def test_post_on_group_page(self):
        group = Group.objects.create(
            title='Тестовый заголовок для теста группы',
            description='Тест',
            slug='test-slug-group'
        )
        new_post = Post.objects.create(
            text='Тестируем группу', author_id=self.user.id, group=group
        )
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'group_slug': 'test-slug-group'}
            )
        )
        group_page = response.context.get('page_obj').object_list[0]
        self.assertEqual(group_page, new_post)

    def test_post_in_profile(self):
        new_post = Post.objects.create(text='Тестируем', author_id=1)
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': 'StasBasov'}
            )
        )
        profile = response.context.get('page_obj').object_list[0]
        self.assertEqual(profile, new_post)

    def test_image_in_context_homepage(self):
        """Шаблон home сформирован с картинкой в контексте."""
        response = self.authorized_client.get(reverse('posts:homepage'))
        first_object = response.context['page_obj'][0].image
        self.assertIsNotNone(first_object)

    def test_image_in_context_profile(self):
        """Шаблон profile сформирован с картинкой в контексте."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': 'StasBasov'}
            )
        )
        first_object = response.context['page_obj'][0].image
        self.assertIsNotNone(first_object)

    def test_image_in_context_group(self):
        """Шаблон group_list сформирован с картинкой в контексте."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'group_slug': 'test-slug'})
        )
        first_object = response.context['page_obj'][0].image
        self.assertIsNotNone(first_object)

    def test_image_in_context_post(self):
        """Шаблон post сформирован с картинкой в контексте."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': Post.objects.order_by('id')[0].id}
            )
        )
        first_object = response.context['posts'].image
        self.assertIsNotNone(first_object)

    def test_cache(self):
        """Проверка кэширования постов на Главной"""
        cache.clear()
        new_post = Post.objects.create(
            text='Тест кеша',
            author_id=self.user.id,
        )
        response = self.authorized_client.get(
            reverse('posts:homepage')
        )
        first_object = response.context['posts'][0].text
        self.assertEqual(first_object, new_post.text)
        new_post.delete()
        response_del = self.authorized_client.get(
            reverse('posts:homepage')
        )
        self.assertEqual(response.content, response_del.content)

    def test_posts_followers(self):
        """Проверка пост появляется после подписки
         на автора в ленте на главной странице"""
        user2 = User.objects.create_user(username='follower')
        authorized_client2 = Client()
        authorized_client2.force_login(user2)
        Follow.objects.create(user=user2, author=self.user)
        response = authorized_client2.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        user3 = User.objects.create_user(username='not_follower')
        authorized_client3 = Client()
        authorized_client3.force_login(user3)
        response_unfollower = authorized_client3.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_unfollower.context['page_obj']), 0)

    def test_check_following(self):
        """Проверка доступности подписки авторизованному пользователю"""
        user2 = User.objects.create_user(username='follower')
        authorized_client2 = Client()
        authorized_client2.force_login(user2)
        response = authorized_client2.get(
            reverse(
                'posts:profile_follow', kwargs={'username': 'StasBasov'}
            )
        )
        self.assertEqual(response.status_code, 302)
        followers = Follow.objects.count()
        self.assertEqual(1, followers)
        response_2 = authorized_client2.get(
            reverse(
                'posts:profile_unfollow', kwargs={'username': 'StasBasov'}
            )
        )
        self.assertEqual(response_2.status_code, 302)
        followers = Follow.objects.count()
        self.assertEqual(0, followers)


class CommentsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasComm')
        group = Group.objects.create(
            title='Тестовый заголовок комментов',
            description='Тестовое описание комментов',
            slug='test-slug-comm'
        )
        for i in range(14):
            Post.objects.create(
                text=i, author_id=cls.user.id, group=group
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_comments(self):
        """Комметарии доступны только авторизованному пользователю."""
        response_guest = self.guest_client.get(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': Post.objects.order_by('id')[0].id}
            )
        )
        response_register = self.authorized_client.get(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': Post.objects.order_by('id')[0].id}
            )
        )
        self.assertNotEqual(response_register, response_guest)
