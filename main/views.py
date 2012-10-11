# Create your views here.
from main.render import render_to_response
from django.contrib.auth.models import User
from django.template import RequestContext
from main.models import Post, Comment
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime
from tinymce.widgets import TinyMCE
from django.core.paginator import Paginator
from django.conf import settings

MOST_VIEWED = 'Most Viewed'
ARCHIVE = 'Archive'

class PostForm(ModelForm):
        post = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
        class Meta:
                model = Post
                fields = ('subject', 'post',)

class CommentForm(ModelForm):
        comment = forms.CharField(widget=TinyMCE(attrs={'cols': 30, 'rows': 10}))
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

def get_posts(username=None):
        if username:
                return Post.objects.filter(user__username=username)
        else:
                return Post.objects.all()

def get_sidebar(posts=None, username=None):
        if not posts:
                posts = get_posts(username=username)
        most_viewed = posts.order_by("-views")[0:5]
        sb = {MOST_VIEWED:[]}
        for mv in most_viewed:
                sb[MOST_VIEWED] += [{'url':'/view/%s/' % mv.id,
                        'name':mv.subject}]
        if username:
                archive = {}
                years_in_db = posts.dates('posted_at', 'year')
                for y in years_in_db:
                        months_in_year = posts.filter(posted_at__year=y.year).dates('posted_at', 'month')
                        archive[y.year] = months_in_year
                sb[ARCHIVE] = []
                for _year, _months in archive.items():
                        for _m in _months:
                                url = '/index/%s/%d/%d/' % (username, _year, _m.month)
                                sb[ARCHIVE] += [{'url': url,
                                        'name':'%d/%d' % (_m.month, _year)}]
        return sb

def index(request, username, year, month):
        posts = get_posts(username=username).order_by("-posted_at")

        if year:
                posts = posts.filter(posted_at__year=year)
        if month:
                posts = posts.filter(posted_at__month=month)
        for p in posts:
                p.shorten_post()
        pages = Paginator(posts, settings.ITEMS_PER_PAGE)
        if request.GET.has_key('p'):
                try:
                        curr_page = int(request.GET['p'])
                except ValueError:
                        curr_page = 1

                if curr_page > pages.num_pages:
                        curr_page = pages.num_pages
                elif curr_page < 1:
                        curr_page = 1
        else:
                curr_page = 1
        d = {'posts':pages.page(curr_page),
             'sidebar':get_sidebar(posts=posts, username=username)}
        if pages.num_pages > 1:
                last_page = pages.num_pages
                first_page = 1
                prev_page = curr_page
                next_page = curr_page
                if curr_page > 1:
                        prev_page -= 1
                if curr_page < pages.num_pages:
                        next_page += 1
                paging = {'first':first_page, 'last':last_page, 'next':next_page,
                                'prev':prev_page}
                d['paging'] = paging
        return render_to_response(request, 'index.html', d)

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

def search(request):
        posts = Post.objects.filter(post__contains=request.GET['s']).order_by('-posted_at')
        return render_to_response(request, 'index.html',
                        {'posts':posts, 'sidebar':get_sidebar()})
