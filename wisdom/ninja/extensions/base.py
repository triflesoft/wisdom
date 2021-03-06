from enum import auto
from enum import Enum
from functools import partialmethod
from jinja2 import nodes
from jinja2 import TemplateSyntaxError
from jinja2.ext import Extension
# from jinja2.lexer import TOKEN_ADD                   # +
from jinja2.lexer import TOKEN_ASSIGN                  # =
# from jinja2.lexer import TOKEN_BLOCK_BEGIN           # {%
from jinja2.lexer import TOKEN_BLOCK_END               # %}
# from jinja2.lexer import TOKEN_COLON                 # :
from jinja2.lexer import TOKEN_COMMA                   # ,
# from jinja2.lexer import TOKEN_COMMENT
# from jinja2.lexer import TOKEN_COMMENT_BEGIN
# from jinja2.lexer import TOKEN_COMMENT_END
# from jinja2.lexer import TOKEN_DATA
# from jinja2.lexer import TOKEN_DIV                   # /
# from jinja2.lexer import TOKEN_DOT                   # .
# from jinja2.lexer import TOKEN_EOF
# from jinja2.lexer import TOKEN_EQ                    # ==
from jinja2.lexer import TOKEN_FLOAT
# from jinja2.lexer import TOKEN_FLOORDIV              # //
# from jinja2.lexer import TOKEN_GT                    # >
# from jinja2.lexer import TOKEN_GTEQ                  # >=
# from jinja2.lexer import TOKEN_INITIAL
from jinja2.lexer import TOKEN_INTEGER
# from jinja2.lexer import TOKEN_LBRACE                # {
# from jinja2.lexer import TOKEN_LBRACKET              # [
# from jinja2.lexer import TOKEN_LINECOMMENT
# from jinja2.lexer import TOKEN_LINECOMMENT_BEGIN
# from jinja2.lexer import TOKEN_LINECOMMENT_END
# from jinja2.lexer import TOKEN_LINESTATEMENT_BEGIN
# from jinja2.lexer import TOKEN_LINESTATEMENT_END
# from jinja2.lexer import TOKEN_LPAREN                # (
# from jinja2.lexer import TOKEN_LT                    # <
# from jinja2.lexer import TOKEN_LTEQ                  # <=
# from jinja2.lexer import TOKEN_MOD                   # %
# from jinja2.lexer import TOKEN_MUL                   # *
from jinja2.lexer import TOKEN_NAME
# from jinja2.lexer import TOKEN_NE                    # !=
# from jinja2.lexer import TOKEN_OPERATOR
# from jinja2.lexer import TOKEN_PIPE                  # |
# from jinja2.lexer import TOKEN_POW                   # **
# from jinja2.lexer import TOKEN_RAW_BEGIN
# from jinja2.lexer import TOKEN_RAW_END
# from jinja2.lexer import TOKEN_RBRACE                # }
# from jinja2.lexer import TOKEN_RBRACKET              # ]
# from jinja2.lexer import TOKEN_RPAREN                # )
# from jinja2.lexer import TOKEN_SEMICOLON             # ;
from jinja2.lexer import TOKEN_STRING
# from jinja2.lexer import TOKEN_SUB                   # -
# from jinja2.lexer import TOKEN_TILDE                 # ~
# from jinja2.lexer import TOKEN_VARIABLE_BEGIN
# from jinja2.lexer import TOKEN_VARIABLE_END
# from jinja2.lexer import TOKEN_WHITESPACE
from os.path import abspath
from os.path import dirname
from os.path import isfile
from os.path import join
from os.path import normpath


class AutomataState(Enum):
    Expect_Name = auto()
    Expect_Assign = auto()
    Expect_Value = auto()
    Expect_Comma = auto()


def _embed_extension_parse(self, open_token_condition, close_token_condition, parser):
        args = [nodes.ContextReference(), nodes.Const(parser.filename), nodes.Const(parser.stream.current.lineno)]
        kwargs = {}
        name_token = parser.stream.expect(open_token_condition)
        automata_state = AutomataState.Expect_Name
        content_path = None

        while parser.stream.current.type != TOKEN_BLOCK_END:
            if automata_state == AutomataState.Expect_Name:
                name_token = parser.stream.expect(TOKEN_NAME)
                automata_state = AutomataState.Expect_Assign
            elif automata_state == AutomataState.Expect_Assign:
                parser.stream.skip_if(TOKEN_ASSIGN)
                automata_state = AutomataState.Expect_Value
            elif automata_state == AutomataState.Expect_Value:
                value_token = parser.stream.next_if(TOKEN_FLOAT)

                if value_token:
                    kwargs[name_token.value] = value_token.value
                else:
                    value_token = parser.stream.next_if(TOKEN_INTEGER)

                    if value_token:
                        kwargs[name_token.value] = value_token.value
                    else:
                        value_token = parser.stream.expect(TOKEN_STRING)

                        if name_token.value == 'absolute_path':
                            content_path = normpath(abspath(join(parser.environment.globals['source_path'], value_token.value)))
                        elif name_token.value == 'relative_path':
                            content_path = normpath(abspath(join(dirname(parser.filename), value_token.value)))
                        else:
                            kwargs[name_token.value] = value_token.value

                automata_state = AutomataState.Expect_Comma
            elif automata_state == AutomataState.Expect_Comma:
                parser.stream.skip_if(TOKEN_COMMA)
                automata_state = AutomataState.Expect_Name

        lineno = parser.stream.current.lineno

        if content_path is not None:
            if not isfile(content_path):
                raise TemplateSyntaxError(f'Cannot find content file "{content_path}".', lineno, parser.filename)

            kwargs['content_path'] = content_path
            body = []
        else:
            body = parser.parse_statements([close_token_condition], drop_needle=True)

        return nodes.CallBlock(
            self.call_method(
                '_process_markup',
                args,
                [nodes.Keyword(name, nodes.Const(value)) for name, value in kwargs.items()]),
            [],
            [],
            body).set_lineno(lineno)


def embed_extension(name, tag):
    attributes = {
        'tags': set([tag]),
        'parse': partialmethod(_embed_extension_parse, f'{TOKEN_NAME}:{tag}', f'{TOKEN_NAME}:end{tag}'),
    }

    return type(name, (Extension, ), attributes)


def _empty_extension_parse(self, open_token_condition, parser):
        args = [nodes.ContextReference(), nodes.Const(parser.filename), nodes.Const(parser.stream.current.lineno)]
        kwargs = {}
        name_token = parser.stream.expect(open_token_condition)
        automata_state = AutomataState.Expect_Name

        while parser.stream.current.type != TOKEN_BLOCK_END:
            if automata_state == AutomataState.Expect_Name:
                name_token = parser.stream.expect(TOKEN_NAME)
                automata_state = AutomataState.Expect_Assign
            elif automata_state == AutomataState.Expect_Assign:
                parser.stream.skip_if(TOKEN_ASSIGN)
                automata_state = AutomataState.Expect_Value
            elif automata_state == AutomataState.Expect_Value:
                value_token = parser.stream.next_if(TOKEN_FLOAT)

                if value_token:
                    kwargs[name_token.value] = value_token.value
                else:
                    value_token = parser.stream.next_if(TOKEN_INTEGER)

                    if value_token:
                        kwargs[name_token.value] = value_token.value
                    else:
                        value_token = parser.stream.expect(TOKEN_STRING)
                        kwargs[name_token.value] = value_token.value

                automata_state = AutomataState.Expect_Comma
            elif automata_state == AutomataState.Expect_Comma:
                parser.stream.skip_if(TOKEN_COMMA)
                automata_state = AutomataState.Expect_Name

        lineno = parser.stream.current.lineno

        return nodes.CallBlock(
            self.call_method(
                '_process_markup',
                args,
                [nodes.Keyword(name, nodes.Const(value)) for name, value in kwargs.items()]),
            [],
            [],
            []).set_lineno(lineno)


def empty_extension(name, tag):
    attributes = {
        'tags': set([tag]),
        'parse': partialmethod(_empty_extension_parse, f'{TOKEN_NAME}:{tag}')
    }

    return type(name, (Extension, ), attributes)
