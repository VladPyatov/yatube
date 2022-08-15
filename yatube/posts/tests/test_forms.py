import tempfile
import shutil
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus

from ..models import Post, Comment
from .constants import TEST_IMAGE

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # create user and authorized client
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.uploaded_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=TEST_IMAGE,
            content_type='image/jpeg'
        )
        # create post
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'image': self.uploaded_image
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # check that post is created
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(Post.objects.latest('pk').text, 'Текст из формы')
        self.assertEqual(Post.objects.latest('pk').author, self.user)
        self.assertEqual(Post.objects.latest('pk').image.name,
                         'posts/' + self.uploaded_image.name)

        # check redirect
        redirect = reverse('posts:profile',
                           kwargs={'username': self.user.username}
                           )
        self.assertRedirects(response, redirect)
        # check that everything works fine
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_wrong(self):
        post_count = Post.objects.count()
        # send NOT IMAGE
        form_data = {
            'text': 'Текст из формы',
            'image': SimpleUploadedFile("file.txt", b"file_content")
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # check that post does not created
        self.assertEqual(Post.objects.count(), post_count)

    def test_post_edit(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст из формы',
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            data=form_data,
            follow=True
        )
        # check that there is no new posts
        self.assertEqual(Post.objects.count(), post_count)
        # check that post have changes
        self.assertEqual(Post.objects.get(pk=self.post.pk).text,
                         'Новый текст из формы')


class CommentFormTests(TestCase):
    def setUp(self):
        # create user and authorized client
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # create post
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )

    def test_comment_add(self):
        # count comments
        comments_num = self.post.comments.count()
        form_data = {
            'text': 'Новый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.pk,)),
            data=form_data,
            follow=True
        )
        # check new comment
        self.assertEqual(self.post.comments.count(), comments_num + 1)
        self.assertEqual(Comment.objects.latest('pk').text,
                         'Новый комментарий'
                         )
        self.assertEqual(Comment.objects.latest('pk').post,
                         self.post
                         )
        self.assertEqual(Comment.objects.latest('pk').author,
                         self.user
                         )
        # check redirect
        redirect = reverse('posts:post_detail', args=(self.post.pk,))
        self.assertRedirects(response, redirect)
        # check that everything works fine
        self.assertEqual(response.status_code, HTTPStatus.OK)
