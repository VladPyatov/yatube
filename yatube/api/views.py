from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import filters, status, viewsets, permissions, mixins

from posts.models import Post, Group, Comment, Follow
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (PostSerializer, GroupSerializer, CommentSerializer,
                          FollowSerializer)


class PermissionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnlyPermission,)


class PostViewSet(PermissionViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentViewSet(PermissionViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def list(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def create(self, request, post_id):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            post = get_object_or_404(Post, id=post_id)
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=user__username', '=following__username')

    def get_queryset(self):
        queryset = Follow.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)
