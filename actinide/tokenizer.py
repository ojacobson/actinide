from .ports import *

# ## TOKENIZATION
#
# The following code implements a state-machine-driven tokenizer which can
# separate an input port into a sequence of lisp tokens. The following token
# classes are defined:
#
# * Comments: ``;`` followed by all bytes to EOF or to the end of the line.
#
# * Open and close parens: ``(`` and ``)`` are returned as freestanding tokens.
#
# * Whitespace: Space, horizontal tab, and newline characters are discarded
#   during tokenization.
#
# * Strings: ``"`` through to the next unescaped ``"`` are read and returned.
#   Sequences within the string beginning with ``\`` indicate an escape, and may
#   only be followed by the character ``"`` or ``\``. An unclosed string literal
#   or an unknown escape sequence is a tokenization error.
#
# * Atoms: Any sequence of characters not included in one of the above classes
#   is read and returned as a single token. This includes words, numbers, and
#   special literals. (Strings are, technically, a kind of atom, but the lexer
#   treats them specially due to their complexity.)
#
# Internally, the tokenizer is a state machine where each state (``next``) is a
# function taking a port as input. The top-level ``tokenize`` function acts as a
# trampoline, repeatedly calling ``next`` until input is exhausted or until
# ``next`` includes a token in its return value.
#
# The various ``next`` functions take the the port, perform whatever logic is
# needed to determine the next state, and return a 2-tuple of ``token`` (may be
# ``None``) and ``next`` (the new next state transition function).
#
# This is heavily inspired by various tail-recursive approaches to tokenizing
# lisp streams. However, the host language does not guarantee tail call
# optimizations, so we use an explicit trampoline function to drive the state
# machine instead of calling each parser directly.

class TokenError(Exception):
    '''
    Raised during ``tokenize`` if the input stream cannot be divided into legal
    tokens.
    '''
    pass

whitespace = " \n\t"
parens = "()"
quotes = "'`," # ,@ is also a quote, but not a single-character quote
comment_delim = ';'
string_delim = '"'
string_escaped = '"\\'

# Read one token from a port.
#
# This is the top-level driver for the state machine that divides the underlying
# input into tokens. It does no input handling itself: it calls the next state
# transition function to determine what to do and how to change the lookahead,
# and relies on that function to perform any necessary input on the port.
#
# Initially, this is in the ``tokenize_any`` state, and exits once it reaches
# the ``tokenize_eof`` state or once it reads a complete token.
#
# This never reads past the end of the current token, relying on ``peek`` to
# determine whether it should continue reading from the port.
def read_token(port):
    next = tokenize_any
    while next != tokenize_eof:
        token, next = next(port)
        if token is not None:
            return token

# Looks ahead one character in the port to determine what kind of token appears
# next in the port. This is an appropriate state to transition to at any time
# when the next token is not known, such as at the end of a token.
#
# This never produces a token directly. It can transition to the tokenizer state
# for any token type, for any non-token type, or the trap state for EOF.
def tokenize_any(port):
    lookahead = peek_next(port)
    if lookahead == '':
        return None, tokenize_eof
    if lookahead in comment_delim:
        return None, tokenize_comment
    if lookahead in parens:
        return None, tokenize_syntax
    if lookahead in quotes:
        return None, tokenize_quote
    if lookahead in whitespace:
        return None, tokenize_whitespace
    return None, tokenize_atom

# EOF trap state This never produces a token, and always transitions to itself
# without reading any input. The tokenizer cannot exit this state.
def tokenize_eof(port):
    return None, tokenize_eof

# Consumes one character at a time until it finds an end of line or runs out of
# input. This throws away comments entirely, at tokenization time, without
# considering whether the comment content can be separated into tokens. As this
# scans the comment, the lookahead will be set to successive characters from the
# port, but never more than one character at a time.
#
# This never produces a token.

# Consumes one character and throws it away, transitioning back to tokenize_any
# once it encounters either an end of line or the end of the input. This
# consumes commments, and as it never generates a token, discards them.
def tokenize_comment(port):
    next = read_next(port)
    if next == '':
        return None, tokenize_any
    if next == '\n':
        return None, tokenize_any
    return None, tokenize_comment

def tokenize_quote(port):
    next = read_next(port)
    if next == ',':
        return None, tokenize_unquote(next)
    return next, tokenize_any

def tokenize_unquote(state):
    def tokenize_unquote_next(port):
        next = peek_next(port)
        if next == '@':
            return state + read_next(port), tokenize_any
        return state, tokenize_any
    return tokenize_unquote_next

# Consumes one character, returning it as a token, before transitioning back to
# the ``tokenize_any`` state. This correctly tokenizes the ``(`` and ``)``
# tokens if they are at the front of the port.
def tokenize_syntax(port):
    return read_next(port), tokenize_any

# Consumes and ignores one character of input. This never produces a token. This
# is appropriate for discarding whitespace in the port.
def tokenize_whitespace(port):
    read_next(port)
    return None, tokenize_any

# Looks ahead one character into the port to determine which kind of atom to
# tokenize: if the input begins with a quote, tokenize a string literal;
# otherwise, tokenize a non-string atom such as a symbol or numeric literal.
# This never generates a token directly.
def tokenize_atom(port):
    lookahead = peek_next(port)
    if lookahead == '"':
        return None, tokenize_string
    return None, tokenize_nonstring_atom('')

# A state factory returning states that build non-string atoms. The resulting
# state family consumes characters until it finds a character which cannot be
# part of a non-string atom, or until it finds the end of input, accumulating
# them into a single token. When either of those cases arise, the resulting
# state generates the accumulated token and returns to the ``tokenize_any``
# state to prepare for the next token.
def tokenize_nonstring_atom(state):
    def tokenize_nonstring_atom_next(port):
        next = peek_next(port)
        if next == '':
            return state, tokenize_any
        if next in '"(); \t\n':
            return state,  tokenize_any
        return None, tokenize_nonstring_atom(state + read_next(port))
    return tokenize_nonstring_atom_next

# ### STRINGS
#
# The following family of states and state factories handles string literals in
# the input stream. String literals are fairly simple: they begin with a quote,
# contain arbitrary characters other than a bare \ or ", and end with a quote.
# (Note that ``\n`` is not an escape sequence: unescaped newlines are permitted
# within string literals.)
#
# These states accumulate the characters of the string. On transition back to
# ``tokenize_any``, the accumulated characters are returned as a token. If, at
# any point, these states encounter EOF or an invalid escape sequence, they
# raise a ``TokenError``: no legal token in Actinide begins with a quote mark
# and ends with EOF, and no legal token includes an invalid escape sequence.
#
# Because tokenization is only concerned with dividing the input into tokens,
# this machine *does not* strip quotes or replace escape sequences. On success,
# it generates a token containing the whole the string literal, verbatim.

# Reads the first character of a string literal, and looks ahead one character
# to determine how the string proceeds so that it can transition to an
# appropriate state.
#
# This never generates a token. The lookahead is set to the characters of the
# string read so far.
def tokenize_string(port):
    quote = read_next(port)
    next = peek_next(port)
    if next == '':
        raise TokenError('Unclosed string literal')
    if next == '\\':
        return None, tokenize_escaped_string_character(quote + read_next(port))
    if next == '"':
        return None, tokenize_string_end(quote)
    return None, tokenize_string_character(quote)

# A state factory returning states which accumulate string characters. The
# returned states look ahead one character to determine how to proceed, and read
# one token under most circumstances.
#
# This never yields a token.
def tokenize_string_character(state):
    def tokenize_string_character_next(port):
        next = peek_next(port)
        if next == '':
            raise TokenError('Unclosed string literal')
        if next == '\\':
            return None, tokenize_escaped_string_character(state + read_next(port))
        if next == '"':
            return None, tokenize_string_end(state)
        return None, tokenize_string_character(state + read_next(port))
    return tokenize_string_character_next

# A state factory returning states which only recognize valid string escaped
# characters (``\\`` and ``"``). If they encounter a valid character, they
# accumulate it onto the string being read and continue reading the string;
# otherwise, they reject the string by raising a TokenError.
#
# This never yields a token.
def tokenize_escaped_string_character(state):
    def tokenize_escaped_string_character_next(port):
        next = read_next(port)
        if next == '':
            raise TokenError('Unclosed string literal')
        if next in string_escaped:
            return None, tokenize_string_character(state + next)
        raise TokenError(f"Invalid string escape '\\{next}'")
    return tokenize_escaped_string_character_next

# A state factory which terminates a string literal. These states read off the
# closing quote mark, and generates the accumulated string as a token before
# transitioning back to the ``tokenize_any`` state.
def tokenize_string_end(state):
    def tokenize_string_end_next(port):
        return state + read_next(port), tokenize_any
    return tokenize_string_end_next

def read_next(port):
    return read_port(port, 1)

def peek_next(port):
    return peek_port(port, 1)
