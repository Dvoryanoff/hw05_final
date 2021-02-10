import os
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

import yatube.settings as st
from posts.models import Group, Post

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hw04_tests.settings")

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

UPLOADED_GIF = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)

settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):

        User = get_user_model()
        super().setUpClass()

        cls.user = User.objects.create(username='test-user',
                                       email='testauthor@mail.com',
                                       password='JimBeam1234')

        cls.user1 = get_user_model().objects.create_user(username='Ivanoff')

        cls.group = Group.objects.create(title='test-group',
                                         slug='test_slug',
                                         description='test-description')

        cls.group_2 = Group.objects.create(title='test-group_2',
                                           slug='test_slug_2',
                                           description='test-description_2')

        cls.post = Post.objects.create(text='test-text',
                                       pub_date='24.11.2020',
                                       author=cls.user,
                                       group=cls.group,
                                       image=UPLOADED_GIF)

        cls.post_2 = Post.objects.create(text='test-text2',
                                         pub_date='24.11.2020',
                                         author=cls.user,
                                         group=cls.group_2,
                                         image=UPLOADED_GIF)

        cls.post_3 = Post.objects.create(text='test-text3',
                                         pub_date='24.11.2020',
                                         author=cls.user1,
                                         group=cls.group_2,
                                         image=UPLOADED_GIF)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):

        self.authorized_author = Client()
        self.authorized_author.force_login(self.user)
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)

        site = Site.objects.get(pk=1)

        self.flat_about = FlatPage.objects.create(
            url=reverse('about-author'),
            title='about me',
            content='<b>some content</b>')

        self.flat_spec = FlatPage.objects.create(
            url=reverse('about-spec'),
            title='about me',
            content='<b>some content</b>'
        )
        self.flat_about.sites.add(site)
        self.flat_spec.sites.add(site)

    def test_pages_uses_correct_template(self):

        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new'),
            'group.html': (reverse('group',
                                   kwargs={'slug': self.group.slug}))}

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):

        """Главная страница отображает правильный контекст."""

        response = self.authorized_author.get(reverse('index'))

        post = response.context.get('paginator').get_page(1)[0]

        self.assertEqual(response.context.get('paginator').per_page,
                         st.PAGINATOR_PAGE_SIZE)
        self.assertIn('page', response.context)
        self.assertIn('paginator', response.context)
        # self.assertEqual(post.image, UPLOADED_GIF.name)
        self.assertTrue(post.image)

    def test_new_page_show_correct_context(self):

        """Страница создания поста отображает правильный контекст."""

        response = self.authorized_author.get(reverse('new'))
        self.assertIn('form', response.context)

    def test_group_page_show_correct_context(self):

        """Страница группы отображает правильный контекст."""

        response = self.authorized_author.get(
            reverse('group', kwargs={'slug': self.group.slug}))

        post = response.context.get('paginator').get_page(1)[0]

        is_slug = response.context.get('group').slug
        is_title = response.context.get('group').title
        is_description = response.context.get('group').description
        self.assertEqual(is_slug, 'test_slug')
        self.assertEqual(is_title, 'test-group')
        self.assertEqual(is_description, 'test-description')
        # self.assertEqual(post.image, UPLOADED_GIF.name)
        self.assertTrue(post.image)

    def test_post_edit_page_show_correct_context(self):

        """Страница редактирования поста отображает правильный контекст."""

        response = self.authorized_author.get(
            reverse('post_edit',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id})
        )
        self.assertIn('form', response.context)
        self.assertIn('post', response.context)

    def test_profile_page_show_correct_context(self):

        """Страница профиля пользователя отображает правильный контекст."""

        response = self.authorized_author.get(reverse(
            'profile', kwargs={'username': self.user.username}))

        post = response.context.get('paginator').get_page(1)[0]

        self.assertIn('author', response.context)
        self.assertIn('page', response.context)
        self.assertIn('paginator', response.context)
        self.assertIn('post_count', response.context)
        # self.assertEqual(post.image, UPLOADED_GIF.name)
        self.assertTrue(post.image)

    def test_group_page_show_post_correct_way(self):

        """Пост появляется на  странице группы."""

        response = self.authorized_author.get(reverse(
            'group', kwargs={'slug': self.group.slug}))

        post = response.context.get('paginator').get_page(1)[0]

        self.assertEqual(post.text, self.post.text)

        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.group, self.post.group)
        # self.assertEqual(post.image, UPLOADED_GIF.name)
        self.assertTrue(post.image)

    def test_post_not_go_to_wrong_group_page(self):

        """Пост не появляется на несоответствующей группе странице."""

        response = self.authorized_author.get(reverse(
            'group', kwargs={'slug': self.group_2.slug}))
        querriedPost = response.context.get('paginator').get_page(1)[0]
        self.assertNotEqual(querriedPost.group, self.post.group)

    def test_object_name(self):
        """Пост появляется с правильным именем."""
        post = TaskPagesTests.post
        fields = {str(post.group): post.group.title,
                  str(post): post.text[:15]}
        for value, expected in fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_about_author_show_correct_context(self):

        """Шаблон about_author сформирован с правильным контекстом."""

        response = self.guest_client.get(reverse('about-author'))
        flat_auth_data = {
            response.context.get('flatpage').content: self.flat_about.content,
            response.context.get('flatpage').title: self.flat_about.title,
            response.context.get('flatpage').url: self.flat_about.url
        }
        for value, expected in flat_auth_data.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_about_spec_show_correct_context(self):

        """Шаблон about_spec сформирован с правильным контекстом."""

        response = self.guest_client.get(reverse('about-spec'))
        flat_spec_data = {
            response.context.get('flatpage').content: self.flat_spec.content,
            response.context.get('flatpage').title: self.flat_spec.title,
            response.context.get('flatpage').url: self.flat_spec.url
        }
        for value, expected in flat_spec_data.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_index_cache(self):

        """Содержимое страницы index хранится в кэше."""

        cache.clear()
        response = self.guest_client.get(reverse('index')).content
        Post.objects.create(
            text='NewPost!',
            author=self.user1,
        )
        response_2 = self.guest_client.get(reverse('index')).content
        self.assertEqual(response, response_2)
        cache.clear()
        response_3 = self.guest_client.get(reverse('index')).content
        self.assertNotEqual(response_3, response)

    # def test_index_cache(self):
    #
    #     """Содержимое страницы index хранится в кэше."""
    #
    #     response = self.authorized_client.get(reverse('index'))
    #     content = response.content
    #     Post.objects.all().delete()
    #     response = self.authorized_client.get(reverse('index'))
    #     self.assertEqual(content, response.content)
    #     cache.clear()
    #     response = self.authorized_client.get(reverse('index'))
    #     self.assertNotEqual(content, response.content)
