from pyramid.view import view_config
from ..views import BaseView


class TagEditorDirectiveView(BaseView):

    @view_config(route_name='tag_editor_template', renderer='../templates/tag-editor/tag-editor.pt')
    def tag_editor_template(self):
        return dict()