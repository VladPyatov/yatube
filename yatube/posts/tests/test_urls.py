from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus

from ..models import Group, Post
from .constants import INDEX_URL, CREATE_URL

User = get_user_model()


class PostURLsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        # create unauthorized user
        self.guest_client = Client()
        # create authorized user
        self.user = User.objects.create_user(username='test_user')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовая пост',
        )
        # setup constants
        self.GROUP_URL = '/group/test_slug/'
        self.PROFILE_URL = '/profile/test_user/'
        self.POST_URL = f'/posts/{self.post.pk}/'
        self.POST_EDIT_URL = self.POST_URL + 'edit/'
        self.POST_COMMENT_URL = self.POST_URL + 'comment/'

        # create authorized and non-authorized users
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_nonauthor = User.objects.create_user(username='test_user2')
        self.nonauthor_client = Client()
        self.nonauthor_client.force_login(self.user_nonauthor)

    def test_urls_uses_correct_template(self):
        """URL-address uses appropriate template."""
        url_templates_names = {
            INDEX_URL: 'posts/index.html',
            self.GROUP_URL: 'posts/group_list.html',
            self.PROFILE_URL: 'posts/profile.html',
            self.POST_URL: 'posts/post_detail.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            CREATE_URL: 'posts/create_post.html',

        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location(self):
        """Check urls for all users"""
        url_status = {
            INDEX_URL: HTTPStatus.OK,
            self.GROUP_URL: HTTPStatus.OK,
            self.PROFILE_URL: HTTPStatus.OK,
            self.POST_URL: HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,

        }
        for url, status in url_status.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_create_url_exists_at_desired_location_authorized(self):
        """Page /create/ available only for auth user."""
        response = self.authorized_client.get(CREATE_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous(self):
        """Page /create/ redirects anonymous user."""
        response = self.guest_client.get(CREATE_URL)
        self.assertRedirects(
            response, '/auth/login/?next=' + CREATE_URL
        )

    def test_edit_url_exists_at_desired_location_authorized(self):
        """Page /posts/{self.post.pk}/edit/ available only for author"""
        response = self.authorized_client.get(self.POST_EDIT_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_redirect_nonauthor(self):
        """Page /posts/{self.post.pk}/edit/ redirects non-author user."""
        response = self.nonauthor_client.get(self.POST_EDIT_URL)
        self.assertRedirects(response, self.POST_URL)

    def test_comment_url_redirect_guest(self):
        """Page /posts/{self.post.pk}/comment/ redirects anonymous user."""
        response = self.guest_client.get(self.POST_COMMENT_URL)
        self.assertRedirects(
            response, '/auth/login/?next=' + self.POST_COMMENT_URL
        )
