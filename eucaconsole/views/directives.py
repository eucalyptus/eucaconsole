from pyramid.view import view_config
from pyramid.renderers import render_to_response


@view_config(route_name='render_template')
def render_template(request):
    template_name = '/'.join(request.subpath)
    return render_to_response('eucaconsole:templates/{0}.pt'.format(template_name), {}, request=request)
