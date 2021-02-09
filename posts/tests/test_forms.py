from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

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


class PostsCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username='test-user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def setUp(self):
        super().setUp()
        self.form = PostForm()

        self.group_test = Group.objects.create(
            title='test_group',
            slug='group_slug',
            description='Описание тестовой группы'
        )

        self.post_test = Post.objects.create(
            text='text_test', pub_date='03.12.2020',
            author=self.user,
            group=self.group_test, )

    def test_create_post(self):

        """Валидная форма создает post."""

        group = Group.objects.create(
            title='test',
            slug='test-slug',
            description='test'
        )

        post_count = Post.objects.count()

        form_data = {
            'text': self.post_test.text,
            'group': group.id,
            'image': UPLOADED_GIF
        }

        response = self.authorized_client.post(
            reverse('new'),
            data=form_data,
            follow=True
        )

        post = response.context['page'][0]

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])

    def test_edit_post(self):

        """Валидная форма редактирует запись в Post."""

        form_data = {
            'text': 'self.post.text',
            'group': self.group_test.id,
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
                reverse('post_edit',
                        kwargs={'username': self.user.username,
                                'post_id': self.post_test.id}),
                data=form_data,
                follow=True)
        post = response.context.get('post')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertRedirects(response,
                             reverse('post',
                                     kwargs={'username': self.user.username,
                                             'post_id': self.post_test.id}))
