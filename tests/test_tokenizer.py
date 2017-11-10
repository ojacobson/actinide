from hypothesis import given, settings, HealthCheck, event
from hypothesis.strategies import just, text, characters, from_regex, one_of, tuples, sampled_from
import io

from actinide.tokenizer import *

from .tokens import spaced_token_sequences

class ReadablePort(io.StringIO):
    def __repr__(self):
        # Slightly friendlier debugging output
        return f"ReadablePort(str={repr(self.getvalue())}, pos={self.tell()})"

# Many of the following tests proceed by cases, because the underlying behaviour
# is too complex to treat as a uniform set of properties. The cases are meant to
# be total, and in principle could be defined as a set of filters on the
# ``text()`` generator that , combined, exhaust the possible outcomes of that
# generator.
#
# Implementing the tests that way causes Hypothesis to generate a significant
# number of examples that it then throws away without verifying, because
# Hypothesis has no insight into filters to use when generating examples.
# Instead, this test suite specifies generators per-case.

# Cases for tokenize_any:

# We test this a bit differently from the subsequent tokenizer states. Because
# it's a pure routing state, we can generate lookahead, expected_state pairs and
# check them in one pass, rather than testing each possible outcome separately.
# In every case, the input is irrelevant: this state never reads.

def next_token_states():
    return one_of(
        tuples(just(''), just(tokenize_eof)),
        tuples(just(';'), just(tokenize_comment)),
        tuples(sampled_from('()'), just(tokenize_syntax)),
        tuples(sampled_from(' \t\n'), just(tokenize_whitespace)),
        tuples(just('"'), just(tokenize_atom)),
        tuples(characters(blacklist_characters=' \t\n();"'), just(tokenize_atom)),
    )

@given(next_token_states(), text())
def test_tokenize_any(lookahead_next, input):
    s, expected_state = lookahead_next
    port = ReadablePort(input)
    token, lookahead, next = tokenize_any(s, input)

    assert token is None
    assert lookahead == s
    assert next == expected_state
    assert port.tell() == 0

# Since the previous test case is rigged for success, also verify that no input
# causes tokenize_any to enter an unexpected state or to throw an exception.
@given(text(), text())
def test_tokenize_any_fuzz(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_any(s, input)

    assert token is None
    assert lookahead == s
    assert next in (tokenize_eof, tokenize_comment, tokenize_syntax, tokenize_whitespace, tokenize_atom)
    assert port.tell() == 0

# Cases for tokenize_eof:

# * any lookahead, any input: tokenize_eof is a trap state performing no reads,
#   always returning to itself, and never generating a token.
@given(text(), text())
def test_tokenize_eof(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_eof(s, port)

    assert token is None
    assert lookahead == s
    assert next == tokenize_eof
    assert port.tell() == 0

# Cases for tokenize_comment:

# * any lookahead, one or more characters beginning with a non-newline as input:
#   tokenize_comment continues the current comment, throwing away one character
#   of input, without generating a token.
@given(text(), from_regex(r'^[^\n].*'))
def test_tokenize_comment_continues(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_comment(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == input[0]
    assert next == tokenize_comment

# * any lookahead, one or more characters beginning with a newline as input, and
# * any lookahead, empty input:
#   tokenize_comment concludes the current comment and prepares for the next
#   token, without generating a token.
@given(text(), just('') | from_regex(r'^\n.*'))
def test_tokenize_comment_ends(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_comment(s, port)

    assert token is None
    assert port.tell() == (1 if input else 0)
    assert lookahead == (input[0] if input else '')
    assert next == tokenize_any

# Cases for tokenize_syntax:

# * any lookahead, any input: generate the lookahead as a Syntax token and
#   transition back to tokenize_any to prepare for the next token, with one
#   character of lookahead ready to go.
@given(text(), text())
def test_tokenize_syntax(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_syntax(s, port)

    assert token == s
    assert port.tell() == (1 if input else 0)
    assert lookahead == (input[0] if input else '')
    assert next == tokenize_any

# Cases for test_tokenize_whitespace:

# * any lookahead, any input: throw away the presumed-whitespace lookahead, then
#   transition back to tokenize_any to prepare for the next token, with one
#   character of lookahead ready to go, without generating a token.
@given(text(), text())
def test_tokenize_whitespace(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_whitespace(s, port)

    assert token is None
    assert port.tell() == (1 if input else 0)
    assert lookahead == (input[0] if input else '')
    assert next == tokenize_any

# Cases for tokenize_nonstring_atom:

# * any lookahead, any non-empty input not beginning with whitespace, syntax, a
#   comment delimiter, or a string literal: accumulate one character of input
#   onto the lookahead, then transition back to tokenize_symbol to process the
#   next character of input, without generating a token.
@given(text(), from_regex(r'^[^ \n\t();"].*'))
def test_tokenize_nonstring_atom_continues(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_nonstring_atom(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == s + input[0]
    assert next == tokenize_nonstring_atom

# * any lookahead, a non-empty input beginning with whitespace, syntax, a
#   comment delimiter, or a string literal, and
# * any lookahead, empty input:
#   generate the accumulated input as a Symbol token, then transition back to tokenize_any with one character of lookahead ready to go.
@given(text(), just('') | from_regex(r'^[ \n\t();"].*'))
def test_tokenize_tokenize_nonstring_atom_ends(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_nonstring_atom(s, port)

    assert token == s
    assert port.tell() == (1 if input else 0)
    assert lookahead == (input[0] if input else '')
    assert next == tokenize_any

# And now, the _worst_ part of the state machine. Cases for tokenize_string:

# * any lookahead, a non-empty input not beginning with a string delimiter:
#   begin a non-empty string by transitioning to the tokenize_string_character
#   state with one character of lookahead, without generating a token.
@given(text(), from_regex(r'^[^"].*'))
def test_tokenize_string_continues(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_string(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == s + input[0]
    assert next == tokenize_string_character

# * any lookahad, a non-empty input beginning with a string delimiter: terminate
#   an empty string by transitioning to the tokenize_string_end state with an
#   *empty* lookahead, without generating a token.
@given(text(), from_regex(r'^["].*'))
def test_tokenize_string_empty(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_string(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == s + input[0]
    assert next == tokenize_string_end

# * any lookahead, empty input: emit a tokenization error, as we've encountered
#   EOF inside of a string.
@given(text(), just(''))
def test_tokenize_string_eof(s, input):
    try:
        port = ReadablePort(input)
        token, lookahead, next = tokenize_string(s, port)

        assert False # must raise
    except TokenError:
        assert port.tell() == 0

# Cases for tokenize_string_character:

# * any lookahead, any non-empty input not beginning with a string delimiter or
#   escape character: append one character of input to the lookahead, then
#   continue in the tokenize_string_character state without generating a token.
@given(text(), from_regex(r'^[^\\"].*'))
def test_tokenize_string_character_continues(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_string_character(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == s + input[0]
    assert next == tokenize_string_character

# * any lookahead, any non-empty input which begins with an escape character:
#   leave the lookahead unchanged, but transition to the
#   tokenize_escaped_string_character state to determine which escape character
#   we're dealing with, without emitting a token.
@given(text(), from_regex(r'^[\\].*'))
def test_tokenize_string_character_begins_escape(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_string_character(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == s + input[0]
    assert next == tokenize_escaped_string_character

# * any lookahead, any non-empty input which begins with a string delimiter:
#   we're at the end of a string. Transition to the tokenize_string_end state
#   with the current lookahead, without generating a token.
@given(text(), from_regex(r'^["].*'))
def test_tokenize_string_character_ends(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_string_character(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == s + input[0]
    assert next == tokenize_string_end

# * any lookahead, empty input: emit a tokenization error, as we've encountered
#   EOF inside of a string literal.
@given(text(), just(''))
def test_tokenize_string_character_eof(s, input):
    try:
        port = ReadablePort(input)
        token, lookahead, next = tokenize_string_character(s, port)

        assert False # must raise
    except TokenError:
        assert input == ''
        assert port.tell() == 0

# Cases for tokenize_escaped_string:

# * any lookahead, any non-empty input beginning with a legal string escaped
#   character: de-escape the first character of the input, append the result to
#   the lookahead, then transition back to the tokenize_string_character state.
@given(text(), from_regex(r'^["\\].*'))
def test_tokenize_escaped_string_character_valid(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_escaped_string_character(s, port)

    assert token is None
    assert port.tell() == 1
    assert lookahead == s + input[0]
    assert next == tokenize_string_character

# * any lookahead, any non-empty input not beginning with a legal string escaped
#   character: emit a tokenization error, we've found an invalid string escape.
@given(text(), from_regex(r'^[^"\\].*'))
def test_tokenize_escaped_string_character_invalid(s, input):
    try:
        port = ReadablePort(input)
        token, lookahead, next = tokenize_escaped_string_character(s, port)

        assert False # must raise
    except TokenError:
        assert port.tell() == 1

# * any lookahead, empty input: emit a tokenization error, we've found an EOF
#   inside of a string literal.
@given(text(), just(''))
def test_tokenize_escaped_string_character_eof(s, input):
    try:
        port = ReadablePort(input)
        token, lookahead, next = tokenize_escaped_string_character(s, port)

        assert False # must raise
    except TokenError:
        assert port.tell() == 0

# Cases for tokenize_string_end:

# * any lookahead, any input: generate a String token from the lookahead, then
#   transition back to the tokenize_any state with one character of lookahead
#   ready to go.
@given(text(), text())
def test_tokenize_string_end(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_string_end(s, port)

    assert token == s
    assert port.tell() == (1 if input else 0)
    assert lookahead == (input[0] if input else '')
    assert next == tokenize_any

# Cases for tokenize_atom:

# * lookahead containing a string delimiter, any input: found a string atom,
#   transition to the tokenize_string state without reading or generating a
#   token.
@given(just('"'), text())
def test_tokenize_atom_string(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_atom(s, port)

    assert token is None
    assert port.tell() == 0
    assert lookahead == s
    assert next == tokenize_string

# * lookahead containing something other than a string delimiter, any input:
#   found a nonstring atom, transition to the tokenize_nonstring_atom state
#   without reading or generating a token.
@given(from_regex(r'^[^"]'), text())
def test_tokenize_atom_nonstring(s, input):
    port = ReadablePort(input)
    token, lookahead, next = tokenize_atom(s, port)

    assert token is None
    assert port.tell() == 0
    assert lookahead == s
    assert next == tokenize_nonstring_atom

# Cases for the tokenizer:

# * any sequence of separator-token pairs: if the pairs are coalesced into a
#   single giant input, does the tokenizer recover the tokens?
@given(spaced_token_sequences())
def test_tokenizer(spaced_tokens):
    input = ''.join(''.join(pair) for pair in spaced_tokens)
    tokens = [token for (_, token) in spaced_tokens]

    port = ReadablePort(input)

    assert list(tokenize(port)) == tokens
