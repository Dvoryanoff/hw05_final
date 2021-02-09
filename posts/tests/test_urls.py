from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage, Site
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PostURLTests(TestCase):

    def setUp(self):

        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(
            username='Dvoryanoff')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)

        self.group_test = Group.objects.create(
            title='test_group',
            slug='group_slug',
            description='Описание тестовой группы'
        )

        self.post_test = Post.objects.create(
            text='text_test', pub_date='03.12.2020',
            author=self.user,
            group=self.group_test, )

        self.user1 = get_user_model().objects.create_user(username='Ivanoff')
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

    def test_non_authorized_guest_urls_exist(self):

        """Проверка доступности общедоступных страниц для
        неавторизованного пользователя."""

        pages = (reverse('index'),
                 reverse('about-author'),
                 reverse('about-spec'),
                 reverse('profile',
                         kwargs={'username': self.user.username}),
                 reverse('post',
                         kwargs={'username': self.user.username,
                                 'post_id': self.post_test.id}),
                 )

        for url in pages:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200, f'url: {url}')

    def test_authorized_non_author_guest_urls_exist(self):

        """Проверка доступности страниц, которые должны быть доступны
         для авторизованных пользователей, не авторов """

        pages = (reverse('new'),
                 reverse('index'),
                 reverse('about-author'),
                 reverse('about-spec'),
                 reverse('profile', kwargs={'username': self.user.username}),
                 reverse('post',
                         kwargs={'username': self.user.username,
                                 'post_id': self.post_test.id}),
                 )

        for url in pages:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200, f'url: {url}')

    def test_authorized_author_guest_urls_exist(self):

        """Проверка доступности страниц, которые должны быть
         доступны для авторизованных авторов постов """

        pages = (reverse('new'),
                 reverse('index'),
                 reverse('about-author'),
                 reverse('about-spec'),
                 reverse('profile', kwargs={'username': self.user.username}),
                 reverse('post',
                         kwargs={'username': self.user.username,
                                 'post_id': self.post_test.id}),
                 reverse('post_edit',
                         kwargs={'username': self.user.username,
                                 'post_id': self.post_test.id}),

                 )

        for url in pages:
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertEqual(response.status_code, 200, f'url: {url}')

    def test_new_post_none_authorized_redirect_login(self):

        """Страница создания нового поста перенаправит анонимного
                пользователя на страницу логина."""

        response = self.guest_client.get(reverse('new'))
        self.assertRedirects(response,
                             reverse('login') + '?next=' + '/new/')

    def test_edit_post_authorized_redirect_login(self):

        """Страница редактиования  поста перенаправит анонимного
                пользователя на страницу логина."""

        url_post_edit = reverse('post_edit',
                                kwargs={'username': self.user.username,
                                        'post_id': self.post_test.id})
        response = self.guest_client.get(url_post_edit)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + url_post_edit)

    def test_new_page_authorized_non_author_redirect_post(self):

        """Страница редактирования поста перенаправит
        зарегестрированного НЕавтора на страницу поста."""

        url_post = reverse('post_edit',
                           kwargs={'username': self.user.username,
                                   'post_id': self.post_test.id})
        response = self.authorized_client.get(url_post)
        self.assertRedirects(response,
                             reverse('post',
                                     kwargs={'username': self.user.username,
                                             'post_id': self.post_test.id}))

    def test_urls_uses_correct_template(self):

        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            reverse('index'): 'index.html',
            reverse('new'): 'new.html',
            reverse('post_edit',
                    kwargs={'username': self.user.username,
                            'post_id': self.post_test.id}): 'new.html',
            reverse('group',
                    kwargs={'slug': self.group_test.slug}): 'group.html'
        }

        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_not_found_return_404(self):

        """Проверка кода 404 если страница не найдена."""

        response = self.guest_client.get('/pagethatnotexist/')
        self.assertEqual(response.status_code, 404)
