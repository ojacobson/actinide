# ## Actinide Types

from collections import namedtuple
from decimal import Decimal, InvalidOperation

# Circular import. Hard to avoid: Procedure calls `eval`, `eval` calls
# `lambda_`, `lambda_` eventually calls `Procedure`. We indirect the call
# through the module object to avoid problems with import order.
from . import evaluator as e

from .environment import *
from .builtin import make_registry

ACTINIDE_BINDINGS, ACTINIDE_VOIDS, ACTINIDE_FNS, ACTINIDE_BUILTINS, bind, void, fn, builtin = make_registry()

# ### Nil
#
# Nil is a type with a single value, usually taken to denote no value.

nil = bind('nil', None)

@fn
def nil_p(value):
    return value is None

@fn
def read_nil(value):
    return nil

@fn
def display_nil(value):
    return '()'

# ### Booleans
#
# The true and false values.

true = bind('#t', True)
false = bind('#f', False)

@fn
def boolean_p(value):
    return value is true or value is false

@fn
def read_boolean(value):
    if value == '#t':
        return true
    if value == '#f':
        return false
    return None

@fn
def display_boolean(value):
    return '#t' if value else '#f'


# ### Integers
#
# These are fixed-precision numbers with no decimal part, obeying common notions
# of machine integer arithmetic. They support large values.

integer = bind('integer', int)

@fn
def integer_p(value):
    return isinstance(value, integer)

@fn
def read_integer(value):
    try:
        return integer(value)
    except ValueError:
        return nil

@fn
def display_integer(value):
    return str(value)

# ### Decimals
#
# These are variable-precision numbers, which may have a decimal part.

decimal = bind('decimal', Decimal)

@fn
def decimal_p(value):
    return isinstance(value, decimal)

@fn
def read_decimal(value):
    try:
        return decimal(value)
    except InvalidOperation:
        return nil

@fn
def display_decimal(value):
    return str(value)

# ### Strings
#
# Sequences of characters.

string = bind('string', str)

@fn
def string_p(value):
    return not symbol_p(value) and isinstance(value, string)

@fn
def read_string(value):
    value = value[1:-1]
    value = value.replace('\\"', '"')
    value = value.replace('\\\\', '\\')
    return value

@fn
def display_string(value):
    value = value.replace('\\', '\\\\')
    value = value.replace('"', '\\"')
    return f'"{value}"'

# ### Symbols
#
# Short, interned strings used as identifiers. Interning is handled by a
# SymbolTable.

class Symbol(object):
    def __init__(self, value):
        self.value = value
    def __hash__(self):
        return hash(self.value)
    def __str__(self):
        return f"{self.value}"
    def __repr__(self):
        return f'Symbol({repr(self.value)})'

# bind manually, fix the symbol table
def symbol(string, symbol_table):
    return symbol_table[string]

@fn
def symbol_p(value):
    return isinstance(value, Symbol)

@fn
def read_symbol(value, symbol_table):
    return symbol(value, symbol_table)

@fn
def display_symbol(value):
    return str(value)

# ### Conses
#
# Pairs.

Cons = namedtuple('Cons', 'head tail')

@fn
def cons(head, tail):
    return Cons(head, tail)

@fn
def cons_p(value):
    return isinstance(value, Cons)

@fn
def head(cons):
    return cons.head

@fn
def tail(cons):
    return cons.tail

@fn
def display_cons(value):
    parts = []
    while cons_p(value):
        parts.append(display(head(value)))
        value = tail(value)
    if not nil_p(value):
        parts.append('.')
        parts.append(display(value))
    return '(' + ' '.join(parts) + ')'

# ### Lists

@fn
def list(*elems):
    if elems:
        head, *tail = elems
        return cons(head, list(*tail))
    else:
        return nil

@fn
def list_p(value):
    return nil_p(value) or cons_p(value) and list_p(tail(value))

def flatten(list):
    r = []
    while not nil_p(list):
        r.append(head(list))
        list = tail(list)
    return r

# ### Procedures

class Procedure(object):
    def __init__(self, body, formals, environment, symbols):
        self.body = body
        self.continuation = e.eval(body, symbols, None)
        self.formals = formals
        self.environment = environment

    def __call__(self, *args):
        call_env = self.invocation_environment(*args)
        return e.run(self.continuation, call_env, ())

    def invocation_environment(self, *args):
        return Environment(zip(self.formals, args), self.environment)

@fn
def procedure_p(value):
    return callable(value)

@fn
def display_procedure(proc):
    if isinstance(proc, Procedure):
        formals = ' '.join(display(formal) for formal in proc.formals)
        body = display(proc.body)
        return f'<procedure: (lambda ({formals}) {body})>'
    return f'<builtin: {proc.__name__}>'

# ### General-purpose functions
@fn
def display(value):
    if cons_p(value):
        return display_cons(value)
    if symbol_p(value):
        return display_symbol(value)
    if string_p(value):
        return display_string(value)
    if nil_p(value):
        return display_nil(value)
    if boolean_p(value):
        return display_boolean(value)
    if integer_p(value):
        return display_integer(value)
    if decimal_p(value):
        return display_decimal(value)
    if procedure_p(value):
        return display_procedure(value)
    # Give up and use repr to avoid printing `None`.
    return repr(value)
