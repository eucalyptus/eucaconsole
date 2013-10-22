from pyramid.view import view_config


@view_config(route_name='instances', renderer='../templates/instances/instances.pt')
def my_view(request):
    return {'project': 'koala'}
