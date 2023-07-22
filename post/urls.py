from django.urls import path

from post.views import PostListAPIView, PostCreateView, PostRetriveUpdateDestroyView, PostCommentLikeView, \
    PostCommentCreateView, CommetListCreateView, PostLikeAPIView, CommentLikeView

urlpatterns = [
    path('posts', PostListAPIView.as_view()),
    path('create', PostCreateView.as_view()),
    path('update-put-destroy/<uuid:pk>/', PostRetriveUpdateDestroyView.as_view()),
    path('<uuid:pk>/comment/', PostCommentLikeView.as_view()),
    path('<uuid:pk>/comment-create/', PostCommentCreateView.as_view()),
    path('<uuid:pk>/commentlist-create/', CommetListCreateView.as_view()),
    path('<uuid:pk>/post/like-create-delete/', PostLikeAPIView.as_view()),
    path('<uuid:pk>/post/like-create-delete/', CommentLikeView.as_view()),

]