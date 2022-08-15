import tempfile
import shutil

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Group, Post, Follow
from yatube.settings import POSTS_PER_PAGE, BASE_DIR
from .constants import TEST_IMAGE, SIMPLE_POSTS_NUM, GROUP_POSTS_NUM

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # create unauthorized user
        self.guest_client = Client()
        # create authorized user
        self.user = User.objects.create_user(username='test_user')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group_slug',
            description='Тестовое описание',
        )
        self.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_group_slug2',
            description='Тестовое описание 2',
        )
        self.uploaded_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=TEST_IMAGE,
            content_type='image/jpeg'
        )
        # create simple post
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            image=self.uploaded_image
        )
        # create 6 posts without group
        self.simple_posts_num = SIMPLE_POSTS_NUM
        for i in range(self.simple_posts_num):
            Post.objects.create(author=self.user, text=f'Тестовый пост {i}')
        # create 6 posts with group and image
        self.group_posts_num = GROUP_POSTS_NUM
        self.group_posts = []
        for i in range(self.group_posts_num):
            self.group_posts.append(
                Post.objects.create(
                    author=self.user,
                    text=f'Тестовый пост группы {i}',
                    group=self.group,
                    image=self.uploaded_image
                )
            )

        # create authorized author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # create authorized non-author user
        self.user_nonauthor = User.objects.create_user(username='test_user2')
        self.nonauthor_client = Client()
        self.nonauthor_client.force_login(self.user_nonauthor)
        # create follower user
        self.follower = User.objects.create_user(username='follower')
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

    def test_pages_uses_correct_template(self):
        """URL-address uses apropriate template."""
        pages_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Home template generated with right context."""
        response = self.authorized_client.get(reverse('posts:index'))

        self.assertEqual(
            response.context['description'],
            'Это главная страница проекта Yatube'
        )
        self.assertIsInstance(response.context['page_obj'], Page)
        # check first page contains 10 posts
        self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)
        # check image
        self.assertEqual(response.context['page_obj'][0].image.name,
                         self.group_posts[-1].image.name)
        # check second page contains 3 posts
        response = self.authorized_client.get(reverse('posts:index')
                                              + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_index_page_cache(self):
        """Home template generated with cache."""
        response = self.authorized_client.get(reverse('posts:index'))
        first = response.content
        Post.objects.latest('pk').delete()
        response = self.authorized_client.get(reverse('posts:index'))
        second = response.content
        self.assertEqual(first, second)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        third = response.content
        self.assertNotEqual(second, third)

    def test_group_list_page_show_correct_context(self):
        """Group_list template generated with right context."""
        query = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        response = self.authorized_client.get(query)

        self.assertEqual(
            response.context['description'],
            'Информация о группах проекта Yatube'
        )
        # check group attributes
        self.assertEqual(response.context['group'].title, 'Тестовая группа')
        self.assertEqual(response.context['group'].slug, 'test_group_slug')
        self.assertEqual(response.context['group'].description,
                         'Тестовое описание')
        # check page contains 6 posts
        self.assertEqual(len(response.context['page_obj']), GROUP_POSTS_NUM)
        # check that posts arranged in order of "last addition"
        for i in range(self.group_posts_num, 0):
            self.assertEqual(response.context['page_obj'][i].text,
                             f'Тестовый пост группы {i}')
        # check image
        self.assertEqual(response.context['page_obj'][0].image.name,
                         self.group_posts[-1].image.name)

    def test_profile_page_show_correct_context(self):
        """Profile template generated with right context."""
        query = reverse('posts:profile',
                        kwargs={'username': self.user.username}
                        )
        response = self.authorized_client.get(query)

        self.assertEqual(
            response.context['description'],
            'Информация о пользователе'
        )
        self.assertEqual(
            response.context['author'],
            self.user
        )
        self.assertEqual(
            response.context['total_count'],
            1 + self.simple_posts_num + self.group_posts_num
        )

        # check first page contains POSTS_PER_PAGE posts
        self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)
        # check image
        self.assertEqual(response.context['page_obj'][0].image.name,
                         self.group_posts[-1].image.name)
        # check second page contains 3 posts
        response = self.authorized_client.get(reverse('posts:index')
                                              + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_post_detail_show_correct_context(self):
        """Post_detail template generated with right context."""
        query = reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        response = self.authorized_client.get(query)

        self.assertEqual(
            response.context['description'],
            'Информация о посте'
        )
        self.assertEqual(
            response.context['preview'],
            self.post.text[:30]
        )
        self.assertEqual(
            response.context['post'],
            self.post
        )
        self.assertEqual(
            response.context['total_count'],
            self.post.author.posts.count()
        )
        # check image
        self.assertEqual(response.context['post'].image.name,
                         self.post.image.name)

    def test_edit_post_show_correct_context(self):
        """Create_post template generated with right context."""
        query = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        response = self.authorized_client.get(query)

        self.assertTrue(response.context['is_edit'])
        self.assertEqual(response.context['post_id'], self.post.pk)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        # check fields values
        self.assertEqual(response.context['form']['text'].value(),
                         'Тестовый пост')
        self.assertEqual(response.context['form']['group'].value(), None)
        self.assertEqual(response.context['form']['image'].value().name,
                         self.post.image.name)

    def test_create_post_show_correct_context(self):
        """Create_post template generated with right context."""
        query = reverse('posts:post_create')
        response = self.authorized_client.get(query)

        self.assertFalse(response.context['is_edit'])

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_created_post_shows_on_pages(self):
        # check that post appears in index, group and profile
        group_query = reverse('posts:group_list',
                              kwargs={'slug': self.group.slug})
        profile_query = reverse('posts:profile',
                                kwargs={'username': self.user.username})
        page_responses = {
            'index': self.authorized_client.get(reverse('posts:index')),
            'group': self.authorized_client.get(group_query),
            'profile': self.authorized_client.get(profile_query),
        }
        for page, response in page_responses.items():
            with self.subTest(page=page):
                self.assertEqual(response.context['page_obj'][0].text,
                                 f'Тестовый пост группы '
                                 f'{self.group_posts_num - 1}')
                self.assertEqual(response.context['page_obj'][0].author,
                                 self.user)
                self.assertEqual(response.context['page_obj'][0].group,
                                 self.group)

        # check that this post does not appear in another group
        group_query = reverse('posts:group_list',
                              kwargs={'slug': self.group2.slug})
        response = self.authorized_client.get(group_query)

        self.assertEqual(len(response.context['page_obj']), 0)

    def test_follow_auth(self):
        """Test that auth. user can subscribe and unsubscribe"""
        # count number of subscriptions
        count = Follow.objects.filter(user=self.user).count()
        # follow
        follow_query = reverse('posts:profile_follow',
                               args=(self.user_nonauthor,)
                               )
        self.authorized_client.get(follow_query)
        count_after_follow = Follow.objects.filter(
            user=self.user
        ).count()
        self.assertEqual(count_after_follow, count + 1)
        # unfollow
        unfollow_query = reverse('posts:profile_unfollow',
                                 args=(self.user_nonauthor,)
                                 )
        self.authorized_client.get(unfollow_query)
        count_after_unfollow = Follow.objects.filter(
            user=self.user
        ).count()
        self.assertEqual(count_after_unfollow, count)

    def test_follow_appears_in_feed(self):
        """Test that new post appears in follower's feed and does not appears
         in other's feed"""

        # get num of posts in follow feed
        response = self.follower_client.get(reverse('posts:follow_index'))
        follower_posts = len(response.context['page_obj'])

        response = self.authorized_client.get(reverse('posts:follow_index'))
        authorized_posts = len(response.context['page_obj'])

        # follow self.user_nonauthor
        follow_query = reverse('posts:profile_follow',
                               args=(self.user_nonauthor,)
                               )
        self.follower_client.get(follow_query)
        # self.user_nonauthor creates new post
        Post.objects.create(author=self.user_nonauthor,
                            text='Тестовый пост для подщипчиков',
                            )

        # check that there is 1 new post in follower feed
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']),
                         follower_posts + 1
                         )
        self.assertEqual(response.context['page_obj'][0].text,
                         'Тестовый пост для подщипчиков'
                         )

        # check that there is no new posts in authorized feed
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']),
                         authorized_posts
                         )
