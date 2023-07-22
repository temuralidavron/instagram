from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db import models
from django.db.models import UniqueConstraint
from users.models import User
from shared.models import Basemodel

# User=get_user_model
class Post(Basemodel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='post_images', validators=[
        FileExtensionValidator(allowed_extensions=['jpeg', 'jpg', 'png'])])
    caption = models.TextField(validators=[MaxLengthValidator(2000)])


    class Meta:
        db_table = 'posts'
        verbose_name = 'post'
        verbose_name_plural = 'posts'


        def __str__(self):
            return f"{self.author} post haqida {self.caption}"


class PostComment(Basemodel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,related_name='child'
    )

class PostLike(Basemodel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'post'],
                name='postlikeUnique'
            )
        ]


class CommentLike(Basemodel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'comment'],
                name='commentlikeUnique'
            )
        ]
