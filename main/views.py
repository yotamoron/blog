# Create your views here.
from main.render import render_to_response
from django.contrib.auth.models import User
from django.template import RequestContext
from main.models import Post, Comment
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime

MOST_VIEWED = 'Most Viewed'

class PostForm(ModelForm):
        class Meta:
                model = Post
                fields = ('subject', 'post',)

class CommentForm(ModelForm):
        class Meta:
                model = Comment
                fields = ('subject', 'comment',)

def message(request, msg):
        return render_to_response(request, 'message.html',
                        {'message':msg},
                         context_instance=RequestContext(request))

def get_post_by_id(post_id):
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
        most_viewed = posts.order_by("-views")[0:5]
        for p in posts:
                p.shorten_post()
        sb = {}
        for mv in most_viewed:
                if not sb.has_key(MOST_VIEWED):
                        sb[MOST_VIEWED] = []
                sb[MOST_VIEWED] += [{'url':'/view/%s/' % mv.id,
                        'name':mv.subject}]

        return render_to_response(request, 'index.html', {'posts':posts,
                'sidebar':sb})

def view(request, post_id):
        the_post = get_post_by_id(post_id)
        if not the_post:
                return message(request, "The post you asked for doesn't exist")
        if request.method == "POST":
                the_comment = Comment()
                the_comment.on_post_id = the_post.id
                the_comment.user_id = request.user.id
                form = CommentForm(request.POST, instance=the_comment)
                if form.is_valid():
                        form.save()
                        return HttpResponseRedirect(reverse('main.views.view',
                                args=(post_id,)))
        comments = Comment.objects.filter(on_post__id=the_post.id).order_by('posted_at')
        d = {'post':the_post, 'comments':comments}
        if request.user.is_authenticated():
                d['comment_form'] = CommentForm()
        the_post.views += 1
        the_post.save()
        return render_to_response(request, 'view.html', d,
                        context_instance=RequestContext(request))

@login_required
def delete(request, post_id):
        the_post = get_post_by_id(post_id)
        if not the_post:
                msg = "The post you asked for doesn't exist"
        elif request.user.has_object_perm(the_post, 'delete'):
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
                the_post = get_post_by_id(post_id)
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
                        the_post.views = 0
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

