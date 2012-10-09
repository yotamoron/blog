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

class PostForm(ModelForm):
        class Meta:
                model = Post
                fields = ('subject', 'post',)

def message(request, msg):
        return render_to_response(request, 'message.html',
                        {'message':msg},
                         context_instance=RequestContext(request))

def get_post_by_id(request, post_id):
        try:
                return Post.objects.get(id=post_id)
        except Post.DoesNotExist:
                return None

def index(request, username):
        if username:
                posts = Post.objects.filter(user__username=username)
        else:
                posts = Post.objects.all()

        posts = posts.order_by("-posted_at")
        for p in posts:
                p.shorten_post()

        return render_to_response(request, 'index.html', {'posts':posts})

def view(request, post_id):
        the_post = get_post_by_id(request, post_id)
        if not the_post:
                return message(request, "The post you asked for doesn't exist")
        the_post.can_edit = request.user.has_object_perm(the_post, 'edit')
        return render_to_response(request, 'index.html', {'posts':[the_post]},
                          context_instance=RequestContext(request))

@login_required
def delete(request, post_id):
        the_post = get_post_by_id(request, post_id)
        if not the_post:
                msg = "The post you asked for doesn't exist"
        if request.user.has_object_perm(the_post, 'delete'):
                the_post.delete()
                msg = "You post \"%s\" has been deleted" % the_post.subject
        else:
                msg = "You have no permissions to delete this post"
        return message(request, msg)

@login_required
def post(request, post_id, action):

        is_edit = action == 'edit'
        the_post = None
        if post_id:
                the_post = get_post_by_id(request, post_id)
                if not the_post:
                        return message(request,
                                        "The post you asked for doesn't exist")

        if is_edit and not request.user.has_object_perm(the_post, 'edit'):
                return message(request,
                                "You have no permissions to edit this post")

        if request.method == "POST":
                if not is_edit:
                        the_post = Post()
                        the_post.user_id = request.user.id
                        the_post.posted_at = datetime.datetime.utcnow()
                form = PostForm(request.POST, instance=the_post)
                if form.is_valid():
                        form.save()
                        request.user.grant_object_perm(the_post,
                                        ['edit', 'delete'])
                        return HttpResponseRedirect(reverse('main.views.index',
                                args=(request.user.username,)))
                else:
                        return render_to_response(request, 'post.html',
                                        {'form':form},
                                        context_instance=RequestContext(request))
        else:
                instance = None
                if is_edit:
                        instance = the_post
                form = PostForm(instance=instance)
                return render_to_response(request, 'post.html', {'form':form},
                                 context_instance=RequestContext(request))

