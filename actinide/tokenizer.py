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
# Internally, the tokenizer is a state machine which maintains two pieces of
# state: the "lookahead" (holding data to feed to the next state transition
# function) and the next state transition function. The top-level ``tokenize``
# function acts as a trampoline, repeatedly calling ``next`` until input is
# exhausted, yielding tokens any time ``next`` includes a token in its return
# value.
#
# The various ``next`` functions take the current lookahead and the port,
# perform whatever logic is needed (including, potentially, reading from the
# port) to determine the next state, and return a 3-tuple of ``token`` (may be
# ``None``), ``lookahead`` (which replaces the previous lookahead), and ``next``
# (the new next state transition function).
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

# Tokenize a port, producing a generator that yields successive tokens as it's
# advanced.
#
# This is the top-level driver for the state machine that divides the underlying
# input into tokens. It does no input handling itself, other than reading the
# first character of the port: this calls the next state transition function to
# determine what to do and how to change the lookahead.
#
# Initially, this is in the ``tokenize_any`` state, and exits once it reaches
# the ``tokenize_eof`` state.
def tokenize(port):
    lookahead, next = port.read(1), tokenize_any
    while next != tokenize_eof:
        token, lookahead, next = next(lookahead, port)
        if token is not None:
            yield token

# If the lookahead is exactly one character, this will correctly determine the
# next token type and transition to that state without consuming input. This is
# generally the correct state to transition to any time the next token is
# unknown - for example, at the end of another token.
#
# This never produces a token directly. It can transition to the tokenizer state
# for any token type, as well as to the trap state for EOF.
def tokenize_any(lookahead, port):
    if lookahead == '':
        return None, lookahead, tokenize_eof
    if lookahead == ';':
        return None, lookahead, tokenize_comment
    if lookahead in '()':
        return None, lookahead, tokenize_syntax
    if lookahead in ' \t\n':
        return None, lookahead, tokenize_whitespace
    return None, lookahead, tokenize_atom

# Special trap state. This never produces a token, and always transitions to
# itself. The lookahead in this state is generally ``''``, and since this never
# performs any further reads, it will remain that value indefinitely.
#
# The top-level parser exits in this situation by examining ``lookahead``, but
# it's possible to reach this state from string literal tokenization or after a
# comment.
def tokenize_eof(lookahead, port):
    return None, lookahead, tokenize_eof

# Consumes one character at a time until it finds an end of line or runs out of
# input. This throws away comments entirely, at tokenization time, without
# considering whether the comment content can be separated into tokens. As this
# scans the comment, the lookahead will be set to successive characters from the
# port, but never more than one character at a time.
#
# This never produces a token.
def tokenize_comment(lookahead, port):
    next = port.read(1)
    if next == '':
        return None, next, tokenize_any
    if next == '\n':
        return None, next, tokenize_any
    return None, next, tokenize_comment

# Generates the entire lookahead as a token. This is generally appropriate for
# the ``(`` and ``)`` syntactic elements.
#
# The resulting lookahead will be the next character of input, and this always
# dispatches back to ``tokenize_any`` so that the next token (if any) can be
# determined.
def tokenize_syntax(lookahead, port):
    return lookahead, port.read(1), tokenize_any

# Consumes and ignores one character of input. This never produces a token, and
# throws away the lookahead entirely. The resulting lookahead is the next
# character of input.
def tokenize_whitespace(lookahead, port):
    return None, port.read(1), tokenize_any

# We've ruled out all non-atom tokens. If the lookahead is a string delimiter,
# transitions to a state which tokenizes a single string literal; otherwise,
# transitions to a state which consumes a single non-string atom. In both cases,
# this leaves the lookahead alone, and generates no token.
def tokenize_atom(lookahead, port):
    if lookahead == '"':
        return None, lookahead, tokenize_string
    return None, lookahead, tokenize_nonstring_atom

# Consumes characters until it finds a character which cannot be part of a
# non-string atom, or until it finds the end of input, accumulating them into a
# single token. This is a heavily-overloaded token category, as it contains not
# only Actinide symbols but also all non-String literals.
#
# While the tokenizer remains in this state, the lookahead accumulates the
# characters of the token. When this matches a completed token, it produces a
# Symbol token, and resets the lookahead back to a single read result containing
# the next character of input.
def tokenize_nonstring_atom(lookahead, port):
    next = port.read(1)
    if next == '':
        return lookahead, next, tokenize_any
    if next in '"(); \t\n':
        return lookahead, next, tokenize_any
    return None, lookahead + next, tokenize_nonstring_atom

# ### STRINGS
#
# The following family of states handles string literals in the input stream.
# String literals are fairly simple: they begin with a quote, contain arbitrary
# characters other than a bare \ or ", and end with a quote. (Note that ``\n``
# is not an escape sequence: unescaped newlines are permitted within string
# literals.)
#
# These states use the lookahead to accumulate the characters of the string. On
# transition back to ``tokenize_any``, the lookahead is always set back to a
# single character. If, at any point, these states encounter EOF, they raise a
# ``TokenError``: no legal token in Actinide begins with a quote mark and ends
# with EOF.
#
# Because tokenization is only concerned with dividing the input into tokens,
# this machine *does not* strip quotes or replace escape sequences. On success,
# it generates a token containing the whole the string literal, verbatim.

# The lookahead is assumed to be the opening quote of a string, and discarded.
# Read forwards one character to determine whether this is an empty string
# literal or not, then proceed either to ``tokenize_string_end`` for an empty
# string, or to ``tokenize_string_character`` for a non-empty string.
#
# This never yields a token. The lookahead is set to the characters of the
# string read so far.
def tokenize_string(lookahead, port):
    next = port.read(1)
    if next == '':
        raise TokenError('Unclosed string literal')
    if next == '\\':
        return None, lookahead + next, tokenize_escaped_string_character
    if next == '"':
        return None, lookahead + next, tokenize_string_end
    return None, lookahead + next, tokenize_string_character

# The lookahead contains the body of the string read so far. Reads forwards one
# character to determine if the string continues, contains an escaped character,
# or ends.
#
# This never yields a token.
def tokenize_string_character(lookahead, port):
    next = port.read(1)
    if next == '':
        raise TokenError('Unclosed string literal')
    if next == '\\':
        return None, lookahead + next, tokenize_escaped_string_character
    if next == '"':
        return None, lookahead + next, tokenize_string_end
    return None, lookahead + next, tokenize_string_character

# The lookahead contains the body of the string so far. Reads forwards one
# character to determine which, if any, escaped character to process: if it's
# one we recognize, append it to the string, otherwise raise a TokenError.
#
# This never yields a token, and always dispatches back to
# ``tokenize_string_character`` on a legal escape character.
def tokenize_escaped_string_character(lookahead, port):
    next = port.read(1)
    if next == '':
        raise TokenError('Unclosed string literal')
    if next == '"':
        return None, lookahead + next, tokenize_string_character
    if next == '\\':
        return None, lookahead + next, tokenize_string_character
    raise TokenError(f"Invalid string escape '\\{next}'")

# Package the lookahead (the full string body, de-escaped and without leading
# and trailing quotes) up as a String token and return it, then transition back
# to the ``tokenize_any`` state with a single read result in the lookahead.
def tokenize_string_end(lookahead, port):
    return lookahead, port.read(1), tokenize_any
