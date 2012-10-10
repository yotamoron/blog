from django.db import models
from django.contrib.auth.models import User
import objectpermissions

# Create your models here.

# Post
class Post(models.Model):
        user = models.ForeignKey(User)
        subject = models.CharField('Subject', max_length=128)
        post = models.TextField('')
        posted_at = models.DateTimeField("Posted at", auto_now=False)
        views = models.IntegerField()

        def shorten_post(self):
                if len(self.post) > 200:
                        last = 200
                        while not self.post[last] == ' ' and last > 190:
                                last -= 1
                        self.post = self.post[0:last] + ' ...'

# Comment
class Comment(models.Model):
        user = models.ForeignKey(User)
        on_post = models.ForeignKey(Post)
        subject = models.CharField(max_length=128)
        comment = models.TextField()
        posted_at = models.DateTimeField("Posted at", auto_now=True)

permissions = ['read', 'write', 'edit', 'delete']
objectpermissions.register(Post, permissions)
objectpermissions.register(Comment, permissions)

