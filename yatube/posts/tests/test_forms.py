import shutil
import tempfile
from django.contrib.auth import get_user_model
from posts.forms import PostForm
from posts.models import Post
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test')
        Post.objects.create(
            text='Тестовый текст',
            author_id=cls.user.id,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_task(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'author_id': self.user.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': 'Test'}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                author_id=self.user.id
            ).exists()
        )

    def test_update_task(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': 'Измененный текст',
            'author_id': self.user.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_update', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': 1}
            )
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertTrue(
            Post.objects.filter(
                text='Измененный текст',
                author=self.user.id
            ).exists()
        )
        test_user = User.objects.create_user(username='Test_validity')
        self.authorized_client.force_login(test_user)
        response_2 = self.authorized_client.post(
            reverse('posts:post_update', kwargs={'post_id': 1}),
        )
        self.assertRedirects(
            response_2, reverse(
                'posts:post_detail', kwargs={'post_id': 1}
            )
        )
