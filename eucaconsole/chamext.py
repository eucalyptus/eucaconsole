import ast
from chameleon import PageTemplate


def setup_exts(config):
    PageTemplate.expression_types['braceescape'] = escape_double_braces


def escape_double_braces(s):
    def compiler(target, engine):
        escaped = s.replace('{{', '&#123;')
        escaped = escaped.replace('}}', '&#125;')
        value = ast.Str(escaped)
        return [ast.Assign(targets=[target], value=value)]
    return compiler
