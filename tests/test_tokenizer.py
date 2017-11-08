from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import text, from_regex
import io

from actinide.tokenizer import *

class ReadablePort(io.StringIO):
    def __repr__(self):
        # Slightly friendlier debugging output
        return f"ReadablePort(str={repr(self.getvalue())}, pos={self.tell()})"

def not_(f):
    return lambda *args, **kwargs: not f(*args, **kwargs)

@given(text(), text())
def test_tokenize_eof(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_eof(s, port)

    assert token is None
    assert lookahead == s
    assert next == tokenize_eof
    assert port.tell() == 0

def comment_continues(text):
    if text == '':
        return False
    return text[0] != '\n'

@given(text(), text().filter(comment_continues))
def test_tokenize_comment_continues(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_comment(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == input[0]
    assert next == tokenize_comment

@given(text(), text().filter(not_(comment_continues)))
def test_tokenize_comment_ends(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_comment(s, port)

    assert token is None
    assert port.tell() == (1 if input else 0)
    assert lookahead == (input[0] if input else '')
    assert next == tokenize_any

@given(text(), text())
def test_tokenize_syntax(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_syntax(s, port)

    assert token == Syntax(s)
    assert isinstance(token, Syntax)
    assert port.tell() == (1 if input else 0)
    assert lookahead == (input[0] if input else '')
    assert next == tokenize_any

@given(text(), text())
def test_tokenize_whitespace(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_whitespace(s, port)

    assert token is None
    assert port.tell() == (1 if input else 0)
    assert lookahead == (input[0] if input else '')
    assert next == tokenize_any

def symbol_continues(text):
    if text == '':
        return False
    return text[0] not in ' \n\t();"'

@given(text(), text().filter(symbol_continues))
def test_tokenize_symbol_continues(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_symbol(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == s + input[0]
    assert next == tokenize_symbol

@given(text(), text().filter(not_(symbol_continues)))
def test_tokenize_symbol_ends(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_symbol(s, port)

    assert token == Symbol(s)
    assert isinstance(token, Symbol)
    assert port.tell() == (1 if input else 0)
    assert lookahead == (input[0] if input else '')
    assert next == tokenize_any

def string_continues(text):
    if text == '':
        return False
    return not text[0] == '"'

@given(text(), text().filter(string_continues))
def test_tokenize_string_continues(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_string(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == input[0]
    assert next == tokenize_string_character

@given(text(), text().filter(not_(string_continues)))
def test_tokenize_string_ends(s, input):
    try:
        port = ReadablePort(input)
        token, lookahead, next = tokenize_string(s, port)

        assert token is None
        assert port.tell() == 1
        assert lookahead == ''
        assert next == tokenize_string_end
    except TokenError:
        assert input == ''
        assert port.tell() == 0

def is_escape(text):
    if text == '':
        return False
    return text[0] == '\\'

@given(text(), text().filter(string_continues).filter(not_(is_escape)))
def test_tokenize_string_character_continues(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_string_character(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == s + input[0]
    assert next == tokenize_string_character

# Using from_regex() rather than text() because searching randomly for strings
# that start with a specific character is far, _far_ too slow. (It often fails
# to find any examples.) I _think_ this preserves the property that this group
# of three tests are exhaustive, but it's not as obvious as it would be if I
# could use text() here.
@given(text(), from_regex(r'\\.*').filter(string_continues).filter(is_escape))
def test_tokenize_string_character_begins_escape(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_string_character(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == s
    assert next == tokenize_escaped_string_character

@given(text(), text().filter(not_(string_continues)))
def test_tokenize_string_character_ends(s, input):
    try:
        port = ReadablePort(input)
        token, lookahead, next = tokenize_string_character(s, port)

        assert token is None
        assert port.tell() == 1
        assert lookahead == s
        assert next == tokenize_string_end
    except TokenError:
        assert input == ''
        assert port.tell() == 0

@given(text(), text())
def test_tokenize_escaped_string_character(s, input):
    try:
        port = ReadablePort(input)
        token, lookahead, next = tokenize_escaped_string_character(s, port)

        assert token is None
        assert port.tell() == 1
        assert lookahead == s + input[0]
        assert next == tokenize_string_character
    except TokenError:
        assert input == '' or input[0] not in '\\n'
        assert port.tell() == (1 if input else 0)

@given(text(), text())
def test_tokenize_string_end(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_string_end(s, port)

    assert token == s
    assert isinstance(token, String)
    assert port.tell() == (1 if input else 0)
    assert lookahead == (input[0] if input else '')
    assert next == tokenize_any
