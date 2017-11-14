# ## The Reader
#
# Reads one Actinide form and parses it.

from decimal import Decimal, InvalidOperation
from .tokenizer import read_token
from .types import *

# Raised if the reader encounters invalid syntax in the underlying port.
class SyntaxError(Exception):
    pass

# Returned on ``read`` if it has reached the end of the input. This is a
# special, non-interned token guaranteed to be unequal to any other token.
EOF = Symbol('#<end-of-input>')

# Reads one form from a port. This will consume all of the tokens included in
# the form, but leave trailing data after the final token untouched.
#
# Any symbols read will be resolved using the passed symbol table (from the
# ``symbol_table`` module), to implement interning.
#
# This uses a simple recursive descent algorithm to read forms. If the first
# token is a ``(``, this recursively reads forms until it encounters a trailing
# ``)``, and builds a list (or a dotted pair) out of the forms read. Otherwise,
# this reads the atom found.
def read(port, symbols):
    head = read_token(port)
    if head is None:
        return EOF
    if head == ')':
        raise SyntaxError("Unexpected ')'")
    if head == '(':
        return read_list(port, symbols)
    return read_atom(head, port, symbols)

# Reads the body of a list from a port. This will read forms, recursively, until
# it encounters the terminating ``)`` that closes the current list, or until it
# encounters a ``.``, in which case it reads a trailing dotted pair.
#
# Under the hood, this method only reads the first token. If the list continues,
# subsequent atoms are read using read_list_tail, which handles lists and dotted
# pairs.
def read_list(port, symbols):
    head = read_token(port)
    if head is None:
        raise SyntaxError("Unexpected end of input")
    if head == ')':
        return list()
    if head == '(':
        return cons(
            read_list(port, symbols),
            read_list_tail(port, symbols),
        )
    return cons(
        read_atom(head, port, symbols),
        read_list_tail(port, symbols),
    )

# Reads the tail of a list from a port, recursively. This will read forms, until
# it encounters either a ``)`` (which terminates the list) or a ``.`` (which
# begins a terminating sequence of dotted pairs).
def read_list_tail(port, symbols):
    head = read_token(port)
    if head is None:
        raise SyntaxError("Unexpected end of input")
    if head == ')':
        return None
    if head == '(':
        return cons(
            read_list(port, symbols),
            read_list_tail(port, symbols),
        )
    if head == '.':
        return read_cons_head(port, symbols)
    return cons(
        read_atom(head, port, symbols),
        read_list_tail(port, symbols),
    )

# Reads the first atom after a dot, then delegates to ``read_cons_tail`` to read
# the second. This generates a dotted pair out of the tail of the input.
def read_cons_head(port, symbols):
    head = read_token(port)
    if head is None:
        raise SyntaxError("Unexpected end of input")
    if head == ')':
        raise SyntaxError("Unexpected ')'")
    if head == '(':
        return read_cons_tail(
            read_list(port, symbols),
            port,
            symbols,
        )
    return read_cons_tail(read_atom(head, port, symbols), port, symbols)

# Reads the second form of a dotted pair from the input. This must either be a
# terminating ``)``, or another dotted pair.
def read_cons_tail(head, port, symbols):
    tail = read_token(port)
    if tail is None:
        raise SyntaxError("Unexpected end of input")
    if tail == ')':
        return head
    if tail == '.':
        return cons(
            head,
            read_cons_head(port, symbols),
        )
    raise SyntaxError("Unexpected value after dotted pair")

# Converts an atom into its lisp representation, using the following priorities:
#
# * ``read_boolean``
# * ``read_integer``
# * ``read_decimal``
# * ``read_symbol`` in the current symbol table (which always succeeds)
#
# This also reconstructs quoted forms.
#
# The first reader to accept the string determines the type of the result.
quotes = {
    "'": 'quote',
    "`": 'quasiquote',
    ",": 'unquote',
    ",@": 'unquote-splicing',
}
def read_atom(atom, port, symbols):
    def read_as_first(val, *funcs):
        for func in funcs:
            result = func(val)
            if result is not None:
                return result

    if atom in quotes:
        quoted = read(port, symbols)
        if quoted == EOF:
            raise SyntaxError("Unexpected end of input")
        return list(symbols[quotes[atom]], quoted)

    if atom[0] == '"':
        return read_string(atom)
    return read_as_first(
        atom,
        read_boolean,
        read_integer,
        read_decimal,
        lambda val: read_symbol(val, symbols),
    )
