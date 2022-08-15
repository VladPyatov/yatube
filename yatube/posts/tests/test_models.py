from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

# get_user_model method will return the currently active user model
# – the custom user model if one is specified, or User otherwise.
User = get_user_model()


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_model_have_correct_object_names(self):
        """check __str__ method for model """
        self.assertEqual(str(PostModelTests.post), 'Тестовая пост')

    def test_model_verbose_names(self):
        """check model verbose name"""
        self.assertEqual(PostModelTests.post._meta.verbose_name,
                         'Text post')
        self.assertEqual(PostModelTests.post._meta.verbose_name_plural,
                         'Text posts')


class GroupModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_model_have_correct_object_names(self):
        """check __str__ method for models """
        self.assertEqual(str(GroupModelTests.group), 'Тестовая группа')

    def test_model_verbose_names(self):
        """check model verbose name"""
        self.assertEqual(GroupModelTests.group._meta.verbose_name,
                         'Social group')
        self.assertEqual(GroupModelTests.group._meta.verbose_name_plural,
                         'Social groups')


class CommentModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    def test_model_have_correct_object_names(self):
        """check __str__ method for models """
        self.assertEqual(str(CommentModelTests.comment), 'Тестовый коммен')

    def test_model_verbose_names(self):
        """check model verbose name"""
        self.assertEqual(CommentModelTests.comment._meta.verbose_name,
                         'Post comment')
        self.assertEqual(CommentModelTests.comment._meta.verbose_name_plural,
                         'Post comments')


class FollowModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='auth1')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.follow = Follow.objects.create(user=cls.user1, author=cls.user2)

    def test_model_have_correct_object_names(self):
        """check __str__ method for models """
        golden = (str(FollowModelTests.user1)
                  + ' follows '
                  + str(FollowModelTests.user2)
                  )
        self.assertEqual(str(FollowModelTests.follow), golden)

    def test_model_verbose_names(self):
        """check model verbose name"""
        self.assertEqual(FollowModelTests.follow._meta.verbose_name,
                         'Follow model')
        self.assertEqual(FollowModelTests.follow._meta.verbose_name_plural,
                         'Follows')
