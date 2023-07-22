from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from post.models import Post, PostComment, PostLike, CommentLike
from post.serializers import PostSerializer, CommentSerializer
from shared.custom_pagination import CustomPagination


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_class = [AllowAny, ]
    pagination_class = CustomPagination


    def get_queryset(self):
        return Post.objects.all()



class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return serializer

class PostRetriveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]


    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                'code': status.HTTP_200_OK,
                "message": "Post succesfully updated",
                "data": serializer.data
            }
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response(
            {
                "success": True,
                'code': status.HTTP_204_NO_CONTENT,
                "message": "Post succesfully delete"
            }
        )



class PostCommentLikeView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny, ]


    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostComment.objects.filter(post_id=post_id)
        return queryset



class PostCommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, ]


    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author=self.request.user, post_id=post_id)
        return queryset



class CommetListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    queryset = PostComment.objects.all()
    pagination_class = CustomPagination


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return serializer




class PostLikeAPIView(APIView):


    def post(self, request, pk):
        try:
            post_like = PostLike.objects.create(
                author=self.request.user,
                post_id=pk
            )
            serilaizer = PostSerilizer(post_like)
            data = {
                "success": True,
                "message": "Like bosildi",
                "data": serilaizer.data
            }
            return Response(data, status.HTTP_201_CREATED)
        except Exception as e:
            data = {
                "success": False,
                "message": f"{str(e)}",
                "data": None

            }
            return Response(data, status.HTTP_400_BAD_REQUEST)

    def delete(self,request, pk):
        try:
            post_id = PostLike.objects.get(
                author = self.request.user,
                post_id = pk
            )
            post_id.delete()
            data = {
                "success": True,
                "message": "Like o'chirildi",
                "data": None
            }
            return Response(data, status.HTTP_204_NO_CONTENT)
        except Exception as e:
            data = {
                "success": False,
                "message": f"{str(e)}",
                "data": None

            }
            return Response(data, status.HTTP_400_BAD_REQUEST)




class CommentLikeView(APIView):



    def post(self, request, pk):
        try:
            comment_like = CommentLike.objects.get(
                author=self.request.user,
                comment_id=pk
            )
            comment_like.delete()
            data = {
                "success": True,
                "message": "Like o'chirildi",
                "data": None
            }
            return Response(data, status.HTTP_204_NO_CONTENT)
        except CommentLike.DoesNot.Exists:

            comment_like = CommentLike.objects.create(
                author=self.request.user,
                comment_like=pk
            )
            serilaizer = CommentLike(comment_like)
            data = {
                "success": True,
                "message": "Like bosildi",
                "data": serilaizer.data
            }

            return Response(data, status.HTTP_201_CREATED)




























# class ChornavoyView(APIView:)
#     def post(self,request, pk):
#         try:
#             comment_id = CommentLike.objects.create(
#                 author = self.request.user,
#                 comment_id = pk
#             )
#             serilizer = CommentSerializer(comment_id)
#             data = {
#                 "success": True,
#                 "message": "Like bosildi",
#                 "data": serilizer.data
#
#             }
#             return Response(data, status.HTTP_201_CREATED)
#         except Exception as e:
#             data = {
#                 "success": False,
#                 "message": "Like bosilmadi",
#                 "data": None
#             }
#             return Response(data, status.HTTP_400_BAD_REQUEST)
#
#
#     def delete(self, request, pk):
#         try:
#             comment_id = CommentLike.objects.get(
#                 author=self.request.user,
#                 comment_id=pk
#             )
#             comment_id.delete()
#             data= {
#                 "succes": True,
#                 "message": "Like o'chirildi",
#                 "data": None
#             }
#             return Response(data, status.HTTP_204_NO_CONTENT)
#         except Exception as e:
#             data = {
#                 "succes": False,
#                 "message": "Like o'chirilmadi",
#                 "data": None
#             }
#             return Response(data, status.HTTP_400_BAD_REQUEST)
#
