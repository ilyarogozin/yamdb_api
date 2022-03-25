import datetime as dt

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
CHOICE_OF_ROLE = [
    (USER, 'Аутентифицированный пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
]


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        help_text=(
            'Обязательное. 150 символов или меньше. '
            'Только буквы, цифры и "@/./+/-/_".'
        ),
        validators=[username_validator],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует',
        },
    )
    first_name = models.CharField(
        verbose_name='Имя', max_length=150, blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия', max_length=150, blank=True
    )
    email = models.EmailField(
        verbose_name='Почта', max_length=254, unique=True
    )
    bio = models.TextField(
        verbose_name='Биография', blank=True,
    )
    role = models.CharField(
        verbose_name='Роль', choices=CHOICE_OF_ROLE, default=USER,
        max_length=max([len(x[0]) for x in CHOICE_OF_ROLE])
    )

    def is_admin(self):
        return self.is_staff or self.role == ADMIN

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    name = models.CharField(verbose_name='Название категории',
                            max_length=256, unique=True)
    slug = models.SlugField(verbose_name='Уникальный URL-ярлык',
                            unique=True, max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(verbose_name='Название жанра',
                            max_length=256, unique=True)
    slug = models.SlugField(verbose_name='Уникальный URL-ярлык',
                            unique=True, max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField(verbose_name='Название')
    year = models.IntegerField(
        verbose_name='Год', blank=True, null=True,
        validators=[
            MaxValueValidator(
                dt.datetime.now().year,
                message='Год выпуска не может быть больше текущего!'
            )
        ]
    )
    description = models.TextField(
        verbose_name='Описание', blank=True, null=True
    )
    genre = models.ManyToManyField(
        Genre, related_name='titles', verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('-year', 'category')
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[
            MaxValueValidator(10), MinValueValidator(1)
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author'
            )
        ]

    def __str__(self):
        return (
            f'{ self.text[:30] }, '
            f'{ self.title.name }, '
            f'{ self.author.username }, '
            f'{ self.score }'
        )


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (
            f'{ self.text[:30] }\n'
            f'{ self.review }\n'
            f'{ self.author.username }'
        )
