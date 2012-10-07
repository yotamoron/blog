
from django.shortcuts import render_to_response as _

def render_to_response(request, template_name, dictionary, context_instance=None,
                mimetype=None):
        dictionary['request'] = request
        return _(template_name, dictionary, context_instance=context_instance,
                        mimetype=mimetype)

