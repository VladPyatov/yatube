"""Posts app Models"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    """Group model"""
    title = models.CharField(verbose_name='Title', max_length=200)
    slug = models.SlugField(verbose_name='Slug', unique=True)
    description = models.TextField(verbose_name='Description')

    class Meta:
        """metaclass for Group model"""
        verbose_name = 'Social group'
        verbose_name_plural = 'Social groups'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Post model"""
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        """metaclass for Post model"""
        verbose_name = 'Text post'
        verbose_name_plural = 'Text posts'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Comment model"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Текст комментария',
    )
    created = models.DateTimeField(verbose_name='Дата публикации',
                                   auto_now_add=True)

    class Meta:
        """metaclass for Comment model"""
        verbose_name = 'Post comment'
        verbose_name_plural = 'Post comments'
        ordering = ('-created',)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    """Comment model"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        """metaclass for Follow model"""
        verbose_name = 'Follow model'
        verbose_name_plural = 'Follows'
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_user_author_pair"
            ),
            models.CheckConstraint(
                name="self_follow",
                check=~models.Q(user=models.F("author")),
            ),
        ]

    def __str__(self):
        return str(self.user) + " follows " + str(self.author)
