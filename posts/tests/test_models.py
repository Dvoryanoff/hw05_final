from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User = get_user_model()
        super().setUpClass()

        cls.user = User.objects.create(username='test-author',
                                       email='testauthor@mail.com',
                                       password='JimBeam1234')

        cls.group = Group.objects.create(title='test-group',
                                         slug='test_slug',
                                         description='test-description')

        cls.post = Post.objects.create(text='Test-text', pub_date='24.11.2020',
                                       author=cls.user,
                                       group=cls.group)

    def test_verbose_name(self):

        """verbose_name в полях совпадает с ожидаемым."""

        post = PostModelTest.post

        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_test(self):

        """help_text в полях совпадает с ожидаемым."""

        post = PostModelTest.post

        fields_help_texts = {
            'text': 'Здесь следует ввести текст не более 2000 знаков'
        }
        for value, expected in fields_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_post_str(self):
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post),
                          'объект Post не соответствует полю Text '
                          'или больше 15 символов')


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User = get_user_model()

        super().setUpClass()
        cls.user = User.objects.create(username='test-author',
                                       email='testauthor@mail.com',
                                       password='JimBeam1234')

        cls.group = Group.objects.create(title='test-group',
                                         slug='test_slug',
                                         description='test-description')

        cls.post = Post.objects.create(text='Test-text',
                                       pub_date='24.11.2020',
                                       author=cls.user,
                                       group=cls.group)

    def test_str_return(self):
        group = GroupModelTest.group
        self.assertEquals(group.title, str(group),
                          'объект Group не соответствует полю title')

    def test_verbose_name(self):

        """verbose_name в полях совпадает с ожидаемым."""

        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Слаг',
            'description': 'Описание'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_test(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        fields_help_texts = {'title': 'Краткое название группы',
                             'slug': 'По-английски желаемый слаг',
                             'description': 'Про что группа?'}
        for value, expected in fields_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)
