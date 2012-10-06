# Create your views here.

from django.shortcuts import render_to_response
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.decorators.cache import never_cache
from django.conf import settings as _s
from django.contrib.sites.models import RequestSite, Site
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from forms import AuthenticationRememberMeForm
from django.views.decorators.csrf import csrf_protect

@login_required
def settings(request):
        return render_to_response('settings.html', {})

@csrf_protect
@never_cache
def remember_me_login(request, template_name='registration/login.html',
                redirect_field_name=REDIRECT_FIELD_NAME):
        redirect_to = request.REQUEST.get(redirect_field_name, '')
        if request.method == "POST":
                form = AuthenticationRememberMeForm(data=request.POST)
                if form.is_valid():
                        if not redirect_to or '//' in redirect_to or \
                                        ' ' in redirect_to:
                                redirect_to = _s.LOGIN_REDIRECT_URL
                        if not form.cleaned_data['remember_me']:
                                request.session.set_expiry(0)
                        login(request, form.get_user())
                        if request.session.test_cookie_worked():
                                request.session.delete_test_cookie()
                        return HttpResponseRedirect(redirect_to)
        else:
                form = AuthenticationRememberMeForm(request)
        request.session.set_test_cookie()
        if Site._meta.installed:
                current_site = Site.objects.get_current()
        else:
                current_site = RequestSite(request)
        return render_to_response(template_name, {'form':form,
                redirect_field_name:redirect_to, 'site':current_site,
                'site_name':current_site.name},
                context_instance=RequestContext(request))

