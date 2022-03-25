import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import SAFE_METHODS

from reviews.models import Category, Comment, Genre, Review, Title, User


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=200)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class UsernameEmailSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    def validate_username(self, username):
        """
        Проверяет, что значение поля 'username' не 'me'.
        """
        if username == 'me':
            raise serializers.ValidationError(
                'Такое имя пользователя запрещено!'
            )
        return username


class UserSerializer(serializers.ModelSerializer):
    def validate_username(self, username):
        """
        Проверяет, что значение поля 'username' не 'me'.
        """
        if username == 'me':
            raise serializers.ValidationError(
                'Такое имя пользователя запрещено!'
            )
        return username

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date', 'review')
        read_only_fields = ('review',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        read_only=True, slug_field='name',
    )
    score = serializers.IntegerField(
        validators=[MaxValueValidator(10), MinValueValidator(1)]
    )

    def validate(self, data):
        if (self.context['request'].method in SAFE_METHODS
           or self.context['request'].method == 'PATCH'):
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        reviews = self.context['request'].user.reviews
        if reviews.filter(title=title).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение!'
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), many=True, slug_field='slug'
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    year = serializers.IntegerField(
        validators=[MaxValueValidator(datetime.datetime.now().year)]
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReadTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ['__all__']
