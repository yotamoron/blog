from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Post
class Post(models.Model):
        user = models.ForeignKey(User)
        subject = models.CharField('Subject', max_length=128)
        post = models.TextField('')
        posted_at = models.DateTimeField("Posted at", auto_now=False)
        edited_at = models.DateTimeField("Last edited at", auto_now=True)

# Comment
class Comment(models.Model):
        post = models.ForeignKey(Post)
        posted_by = models.IntegerField()
        subject = models.CharField(max_length=128)
        comment = models.TextField()
        posted_at = models.DateTimeField("Posted at", auto_now=True)


