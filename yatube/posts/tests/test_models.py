from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

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
        """Проверяем, что у моделей корректно работает __str__."""
        test_post = PostModelTest.post
        test_group = PostModelTest.group
        expected_object_post = test_post.text[
            :settings.QUANTITY_SYMBOLOS_IN_POST
        ]
        expected_object_group = test_group.title
        self.assertEqual(expected_object_post, str(test_post))
        self.assertEqual(expected_object_group, str(test_group))

    def test_verbose_name(self):
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                verbose_name = self.post._meta.get_field(field).verbose_name
                self.assertEqual(verbose_name, expected_value)

    def test_post_help_text(self):
        field_help_text = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                help_text = self.post._meta.get_field(field).help_text
                self.assertEqual(help_text, expected_value)
