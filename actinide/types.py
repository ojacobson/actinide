# ## Actinide Types

from collections import namedtuple
from decimal import Decimal, InvalidOperation

# Circular import. Hard to avoid: Procedure calls `eval`, `eval` calls
# `lambda_`, `lambda_` eventually calls `Procedure`. We indirect the call
# through the module object to avoid problems with import order.
from . import evaluator as e

from .environment import *

# ### Nil
#
# Nil is a type with a single value, usually taken to denote no value.

nil = None

def nil_p(value):
    return value is None

def read_nil(value):
    return nil

def display_nil(value):
    return '()'

# ### Booleans
#
# The true and false values.

true = True
false = False

def boolean_p(value):
    return value in (true, false)

def read_boolean(value):
    if value == '#t':
        return true
    if value == '#f':
        return false
    return None

def display_boolean(value):
    return '#t' if value else '#f'


# ### Integers
#
# These are fixed-precision numbers with no decimal part, obeying common notions
# of machine integer arithmetic. They support large values.

integer = int

def integer_p(value):
    return isinstance(value, integer)

def read_integer(value):
    try:
        return integer(value)
    except ValueError:
        return nil

def display_integer(value):
    return str(value)

# ### Decimals
#
# These are variable-precision numbers, which may have a decimal part.

decimal = Decimal

def decimal_p(value):
    return isinstance(value, decimal)

def read_decimal(value):
    try:
        return decimal(value)
    except InvalidOperation:
        return nil

def display_decimal(value):
    return str(value)

# ### Strings
#
# Sequences of characters.

string = str

def string_p(value):
    return not symbol_p(value) and isinstance(value, string)

def read_string(value):
    value = value[1:-1]
    value = value.replace('\\"', '"')
    value = value.replace('\\\\', '\\')
    return value

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

def symbol(string, symbol_table):
    return symbol_table[string]

def symbol_p(value):
    return isinstance(value, Symbol)

def read_symbol(value, symbol_table):
    return symbol(value, symbol_table)

def display_symbol(value):
    return str(value)

# ### Conses
#
# Pairs.

Cons = namedtuple('Cons', 'head tail')

def cons(head, tail):
    return Cons(head, tail)

def cons_p(value):
    return isinstance(value, Cons)

def head(cons):
    return cons.head

def tail(cons):
    return cons.tail

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

def list(*elems):
    if elems:
        head, *tail = elems
        return cons(head, list(*tail))
    else:
        return nil

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
        self.formals = formals
        self.environment = environment
        self.symbols = symbols

    def __call__(self, *args):
        call_env = self.invocation_environment(*args)
        call_cont = self.continuation(call_env, None)
        return e.run(call_cont, ())

    def invocation_environment(self, *args):
        return Environment(zip(self.formals, args), self.environment)

    def continuation(self, environment, continuation):
        return e.eval(self.body, environment, self.symbols, continuation)

def procedure_p(value):
    return callable(value)

# ### General-purpose functions
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
