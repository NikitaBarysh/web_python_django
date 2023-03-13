from django.test import TestCase, Client
from ..models import Group, Post
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse

from http import HTTPStatus

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.user_author = User.objects.create_user(
            username='user_author'
        )
        cls.another_user = User.objects.create_user(
            username='another_user'
        )
        cls.post = Post.objects.create(
            text='Текст который просто больше 15 символов...',
            author=cls.user_author,
            group=cls.group,
        )
        cls.url_names = [
            '/',
            '/group/test_slug/',
            '/profile/another_user/',
            '/posts/1/',
        ]
        cls.url_names_only_authorized = [
            '/posts/1/edit/',
            '/create/'
        ]

    def setUp(self):
        self.unauthorized_user = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user_author)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.another_user)
        cache.clear()

    def test_unauthorized_user_urls_status_code(self):
        """Проверка status_code для неавторизованного пользователя."""
        for url in self.url_names:
            with self.subTest(url=url):
                response = self.unauthorized_user.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_user_urls_redirect_anonymous(self):
        """
        Страницы перенаправят неавторизованного пользователя
        на страницу логина.
        """
        for url in self.url_names_only_authorized:
            with self.subTest(url=url):
                response = self.unauthorized_user.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_user_search_not_found_page(self):
        """Проверка на несуществующуй адрес"""
        response = self.unauthorized_user.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_author_user_urls_status_code(self):
        """Проверка status_code для авторизированого автора."""
        response = self.post_author.\
            get(reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_no_author_user_urls_redirect(self):
        """Проверка status_code для авторизированого автора."""
        response = self.authorized_user.\
            get(reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse(
                'posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): 'posts/post_create.html',
            reverse(
                'posts:post_create'): 'posts/post_create.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.post_author.get(adress)
                self.assertTemplateUsed(response, template)
