# Create your views here.
from main.render import render_to_response
from django.contrib.auth.models import User
from django.template import RequestContext
from main.models import Post
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime

class Sidebar(object):
        """
        sb = Sidebar()
        sb.add_link('Cat1', '/index/blabla1/', 'Blabla1')
        sb.add_link('Cat1', '/index/blabla2/', 'Blabla2')
        sb.add_link('Cat2', '/index/bb1/', 'Bb1')
        sb.add_link('Cat2', '/index/bb2/', 'Bb2')
        """
        links = {}

        def add_link(self, cat, url, name):
                if not self.links.has_key(cat):
                        self.links[cat] = []
                self.links[cat] += [{'url':url, 'name':name}]

def shorten_post(posts):
        for post in posts:
                if len(post.post) > 200:
                        last = 200
                        while not post.post[last] == ' ':
                                last -= 1
                        post.post = post.post[0:last] + ' ...'
        return posts

def index(request, username):
        if username:
                posts = Post.objects.filter(user__username=username)
        else:
                posts = Post.objects.all()

        # Need to shorten the post to 200 chars
        posts = shorten_post(posts).order_by("-posted_at")
        return render_to_response(request, 'index.html', {'posts':posts})

class PostForm(ModelForm):
        class Meta:
                model = Post
                fields = ('subject', 'post',)

def can_edit(req, post):
        return req.user.id == post.user.id

def view(request, post_id):
        if post_id:
                try:
                        post_by_id = Post.objects.get(id=post_id)
                except Post.DoesNotExist:
                        return render_to_response(request, 'message.html',
                                        {'message':"The post you asked for doesn't exist"},
                                         context_instance=RequestContext(request))
        post = Post.objects.get(id=post_id)
        if can_edit(request, post_by_id):
                post.edit_url = reverse('main.views.post',
                                        args=(str(post_id) + '/edit',))
        return render_to_response(request, 'index.html', {'posts':[post]},
                          context_instance=RequestContext(request))

@login_required
def post(request, post_id, action):

        if post_id:
                try:
                        post_by_id = Post.objects.get(id=post_id)
                except Post.DoesNotExist:
                        return render_to_response(request, 'message.html',
                                        {'message':"The post you asked for doesn't exist"},
                                         context_instance=RequestContext(request))
        if action == 'edit' and not can_edit(request, post_by_id):
                return render_to_response(request, 'message.html',
                                {'message':"You have no permissions to edit \
                                                this post"},
                                context_instance=RequestContext(request))

        if action == 'edit':
                post_url = reverse('main.views.post',
                                args=(str(post_id) + '/edit',))
        else:
                post_url = reverse('main.views.post')
        if request.method == "POST":
                if action == 'edit':
                        post = post_by_id
                else:
                        post = Post()
                        post.user_id = request.user.id
                        post.posted_at = datetime.datetime.utcnow()
                form = PostForm(request.POST, instance=post)
                if form.is_valid():
                        form.save()
                        return HttpResponseRedirect(reverse('main.views.index',
                                args=(request.user.username,)))
                else:
                        error = 'Form did not validate'
                        return render_to_response(request, 'post.html',
                                        {'form':form,
                                         'post_url':post_url},
                                        context_instance=RequestContext(request))
        else:
                if action == 'edit':
                        form = PostForm(instance=post_by_id)
                else:
                        form = PostForm()
                return render_to_response(request, 'post.html',
                                {'form':form, 'post_url':post_url},
                                 context_instance=RequestContext(request))

