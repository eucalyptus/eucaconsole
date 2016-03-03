from pyramid.view import view_config
from ..views import BaseView


class TagEditorDirectiveView(BaseView):

    @view_config(route_name='tag_editor_template', renderer='../templates/tag-editor/tag-editor.pt')
    def tag_editor_template(self):
        return dict()


class GenericDirectiveView(object):
    """
    This class is to provide views to serve directives where all that's neeeded is i18n
    """
    def __init__(self, request, **kwargs):
        self.request = request
    
    @view_config(route_name='stack_aws_dialogs', renderer='../templates/stacks/stack_aws_dialogs.pt')
    def stack_aws_dialogs_template(self):
        return dict()
    
    @view_config(route_name='stack_cancel_update_dialog', renderer='../templates/stacks/stack_cancel_update_dialog.pt')
    def stack_cancel_update_dialogs_template(self):
        return dict()
