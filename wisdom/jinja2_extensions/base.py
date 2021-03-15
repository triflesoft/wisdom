from functools import partialmethod
from jinja2 import nodes
from jinja2.ext import Extension


#class DiscoverExtension(Extension):
#    tags = set(['TAG'])
#
#    def parse(self, parser):
#        while parser.stream.current.type != 'block_end':
#            next(parser.stream)
#
#        body = parser.parse_statements(['name:endTAG'], drop_needle=True)
#
#        return nodes.Const('')


def _discover_extension_parse(self, close_tag, parser):
        while parser.stream.current.type != 'block_end':
            next(parser.stream)

        parser.parse_statements([close_tag], drop_needle=True)

        return nodes.Const('')


def discover_extension(name, tag):
    attributes = {
        'tags': set([tag]),
        'parse': partialmethod(_discover_extension_parse, f'name:end{tag}')
    }

    return type(name, (Extension, ), attributes)

#class GenerateExtension(Extension):
#    tags = set(['TAG'])
#
#    def parse(self, parser):
#        name_token = parser.stream.next_if('name')
#        args = [nodes.ContextReference()]
#
#        while parser.stream.current.type != 'block_end':
#            if parser.stream.current.type in ('name', 'string'):
#                args.append(nodes.Const(parser.stream.current.value))
#                next(parser.stream)
#
#        if len(args) > 3:
#            args = args[0:3]
#        elif len(args) == 2:
#            args.append(nodes.Const('svg'))
#        elif len(args) == 1:
#            args.append(nodes.Const('dot'))
#            args.append(nodes.Const('svg'))
#
#        lineno = parser.stream.current.lineno
#        body = parser.parse_statements(['name:endTAG'], drop_needle=True)
#
#        return nodes.CallBlock(self.call_method('_process_markup', args), [], [], body).set_lineno(lineno)


def _generate_extension_parse(self, close_tag, default_attributes, parser):
        name_token = parser.stream.next_if('name')
        args = [nodes.ContextReference()]

        while parser.stream.current.type != 'block_end':
            if parser.stream.current.type in ('name', 'string'):
                args.append(nodes.Const(parser.stream.current.value))

            next(parser.stream)

        for index, value in enumerate(default_attributes):
            if len(args) <= index + 1:
                args.append(nodes.Const(value))

        args = args[0:len(default_attributes) + 1]
        lineno = parser.stream.current.lineno
        body = parser.parse_statements([close_tag], drop_needle=True)

        return nodes.CallBlock(self.call_method('_process_markup', args), [], [], body).set_lineno(lineno)


def generate_extension(name, tag, default_attributes):
    attributes = {
        'tags': set([tag]),
        'parse': partialmethod(_generate_extension_parse, f'name:end{tag}', default_attributes)
    }

    return type(name, (Extension, ), attributes)
