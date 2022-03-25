from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.core.mail import BadHeaderError, send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as fl
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrReadOnlyOrModeratorOrAdmin)
from .serializers import (CategorySerializer, CommentSerializer,
                          ConfirmationCodeSerializer, GenreSerializer,
                          ReadTitleSerializer, ReviewSerializer,
                          TitleSerializer, UsernameEmailSerializer,
                          UserSerializer)


ACTIVATE = 'Активируйте свой аккаунт.'
CONFIRMATION_CODE = (
    'Ваш код подтверждения: {confirmation_code}\n'
    'Передайте эндпоинту http://127.0.0.1:8000/api/v1/auth/token/\n'
    'свои "username" и "confirmation_code" для получения токена'
)
USERNAME_ALREADY_EXISTS = 'Пользователь с таким username уже существует!'
EMAIL_ALREADY_EXISTS = 'Пользователь с таким email уже существует!'


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_user(request):
    serializer = UsernameEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email').lower()
    try:
        user = User.objects.get(username=username, email=email)
    except User.DoesNotExist:
        if User.objects.filter(username=username).exists():
            raise ValidationError(USERNAME_ALREADY_EXISTS)
        if User.objects.filter(email=email).exists():
            raise ValidationError(EMAIL_ALREADY_EXISTS)
        user = User.objects.create_user(username=username, email=email)
    user.set_password(BaseUserManager().make_random_password())
    user.save()
    confirmation_code = user.password
    try:
        send_mail(
            subject=ACTIVATE, recipient_list=[email],
            from_email=settings.DEFAULT_FROM_EMAIL,
            message=CONFIRMATION_CODE.format(
                confirmation_code=confirmation_code,
            ),
            fail_silently=False
        )
    except BadHeaderError as error:
        raise BadHeaderError(f'Email не был отправлен: { error }')
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_token(request):
    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    if not User.objects.filter(username=username).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    user = User.objects.get(username=username)
    confirmation_code = serializer.validated_data.get('confirmation_code')
    if user.password == confirmation_code:
        token = str(RefreshToken.for_user(user).access_token)
        return Response(data={"token": token}, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes((IsAuthenticated,))
def self_user(request):
    if request.method == 'GET':
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save(role=request.user.role)
    return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (fl.DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            return TitleSerializer
        return ReadTitleSerializer


class MixinViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(MixinViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(MixinViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAuthorOrReadOnlyOrModeratorOrAdmin
    )

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAuthorOrReadOnlyOrModeratorOrAdmin
    )

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
