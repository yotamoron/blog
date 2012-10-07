# Create your views here.
from main.render import render_to_response
from django.contrib.auth.models import User
from django.template import RequestContext

def index(request):
        return render_to_response(request, 'index.html', {})

